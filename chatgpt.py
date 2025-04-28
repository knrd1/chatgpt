import openai
import socket
import ssl
import time
import configparser
import pyshorteners
import requests
import json
from typing import Union, Tuple

# Read configuration from file
config = configparser.ConfigParser()
config.read('chat.conf')

# Set up local server
target_ip = config.get('localserver', 'target_ip')
local_port = config.get('localserver', 'local_port')
mapping = config.get('localserver', 'mapping')
use_local_server = config.getboolean('localserver', 'use_local_server')
url = f"http://{target_ip}:{local_port}{mapping}"

# Set up OpenAI API key
if not use_local_server:
    openai.api_key = config.get('openai', 'api_key')

# Set up ChatCompletion parameters
model = config.get('chatcompletion', 'model')
role = config.get('chatcompletion', 'role')
temperature =  config.getfloat('chatcompletion', 'temperature')
max_tokens = config.getint('chatcompletion', 'max_tokens')
top_p = config.getint('chatcompletion', 'top_p')
frequency_penalty = config.getint('chatcompletion', 'frequency_penalty')
presence_penalty = config.getint('chatcompletion', 'presence_penalty')
request_timeout = config.getint('chatcompletion', 'request_timeout')
context = config.get('chatcompletion', 'context')

# Set up IRC connection settings
server = config.get('irc', 'server')
port = config.getint('irc', 'port')
usessl = config.getboolean('irc', 'ssl')
channels = config.get('irc', 'channels').split(',')
nickname = config.get('irc', 'nickname')
ident = config.get('irc', 'ident')
realname = config.get('irc', 'realname')
password = config.get('irc', 'password')

# Define the list of models
completion_models = ["gpt-3.5-turbo-instruct", "babbage-002", "davinci-002"]
chatcompletion_models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-3.5-turbo"]
images_models = ["dall-e-2", "dall-e-3"]

# Connect to IRC server
def connect(server, port, usessl, password, ident, realname, nickname, channels):
    while True:
        try:
            print("Connecting to: " + server)
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((server, port))
            if usessl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                irc = context.wrap_socket(irc, server_hostname=server)
            if password:
                irc.send(bytes("PASS " + password + "\n", "UTF-8"))
            irc.send(bytes("USER " + ident + " 0 * :" + realname + "\n", "UTF-8"))
            irc.send(bytes("NICK " + nickname + "\n", "UTF-8"))
            print("Connected to: " + server)
            return irc
        except:
            print("Connection failed. Retrying in 5 seconds...")
            time.sleep(5)

irc = connect(server, port, usessl, password, ident, realname, nickname, channels)

accumulated_messages = [{'role': 'system', 'content': context }]
local_data = {
    'messages': accumulated_messages, 
    'temperature': temperature,
    'max_tokens': max_tokens,
    'stream': False
}
headers = { 'Content-Type': 'application/json' }

def get_llm_response(question):
    local_data["messages"].append({'role':'user', 'content': question})
    print("sending json:" + json.dumps(local_data))
    response = requests.post(url, headers=headers, json=local_data, stream=False)
    response.raise_for_status()
    output = []

    content = response.json()['choices'][0]['message']['content']
    print(content)
    local_data["messages"].append({'role':'assistant', 'content': content})
    
    for line in response.json()['choices'][0]['message']['content'].split('\n'):
        output.append(line)

    return output

# Listen for messages from users and answer questions
while True:
    try:
        data = irc.recv(4096).decode("UTF-8")
        if data:
            print(data)
    except UnicodeDecodeError:
        continue
    except:
        print("Connection lost. Reconnecting...")
        time.sleep(5)
        irc = connect(server, port, usessl, password, ident, realname, nickname, channels)
    irc.send(bytes("JOIN " + ",".join(channels) + "\n", "UTF-8"))
    chunk = data.split()
    if len(chunk) > 0:
        if data.startswith(":"):
            command = chunk[1]
        else:
            command = chunk[0]
        if command == "PING":
            irc.send(bytes("PONG " + chunk[1] + "\n", "UTF-8"))
        elif command == "ERROR":
            print("Received ERROR from server. Reconnecting...")
            time.sleep(5)
            irc = connect(server, port, usessl, password, ident, realname, nickname, channels)
        elif command == "471" or command == "473" or command == "474" or command == "475":
            print("Unable to join " + chunk[3] + ": Channel can be full, invite only, bot is banned or needs a key.")
        elif command == "KICK" and chunk[3] == nickname:
            irc.send(bytes("JOIN " + chunk[2] + "\n", "UTF-8"))
            print("Kicked from channel " + chunk[2] + ". Rejoining...")
        elif command == "INVITE":
            if data.split(" :")[1].strip() in channels:
                irc.send(bytes("JOIN " + data.split(" :")[1].strip() + "\n", "UTF-8"))
                print("Invited into channel " + data.split(" :")[1].strip() + ". Joining...")
        elif command == "PRIVMSG" and chunk[2].startswith("#") and chunk[3] == ":" + nickname + ":":
            if use_local_server:
                channel = chunk[2].strip()
                question = data.split(nickname + ":")[1].strip()
                response = get_llm_response(question)
                for answer in response:
                    if len(answer) <= 392:
                        irc.send(bytes("PRIVMSG " + channel + " :" + answer + "\n", "UTF-8"))
                        answer = ""
                    else:
                        last_space_index = answer[:392].rfind(" ")
                        if last_space_index == -1:
                            last_space_index = 392
                        irc.send(bytes("PRIVMSG " + channel + " :" + answer[:last_space_index] + "\n", "UTF-8"))
                        answer = answer[last_space_index:].lstrip()
            else:
                channel = chunk[2].strip()
                question = data.split(nickname + ":")[1].strip()
                if model in chatcompletion_models:
                    try:
                        response = openai.ChatCompletion.create(
                            model=model,
                            messages=[{"role": "system", "content": context}, {"role": "user", "content": question}],
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty,
                            request_timeout=request_timeout
                        )
                        answers = [x.strip() for x in response.choices[0].message.content.strip().split('\n')]
                        for answer in answers:
                            while len(answer) > 0:
                                if len(answer) <= 392:
                                    irc.send(bytes("PRIVMSG " + channel + " :" + answer + "\n", "UTF-8"))
                                    answer = ""
                                else:
                                    last_space_index = answer[:392].rfind(" ")
                                    if last_space_index == -1:
                                        last_space_index = 392
                                    irc.send(bytes("PRIVMSG " + channel + " :" + answer[:last_space_index] + "\n", "UTF-8"))
                                    answer = answer[last_space_index:].lstrip()
                    except openai.error.Timeout as e:
                        print("Error: " + str(e))
                        irc.send(bytes("PRIVMSG " + channel + " :API call timed out. Try again later.\n", "UTF-8"))
                    except openai.error.OpenAIError as e:
                        print("Error: " + str(e))
                        irc.send(bytes(f"PRIVMSG {channel} :API call failed. {str(e)}\n", "UTF-8"))
                    except Exception as e:
                        print("Error: " + str(e))
                        irc.send(bytes(f"PRIVMSG {channel} :An unexpected error occurred. {str(e)}\n", "UTF-8"))
                elif model in completion_models:
                    try:
                        response = openai.Completion.create(
                            model=model,
                            prompt="Q: " + question + "\nA:",
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty,
                            request_timeout=request_timeout
                        )
                        answers = [x.strip() for x in response.choices[0].text.strip().split('\n')]
                        for answer in answers:
                            while len(answer) > 0:
                                if len(answer) <= 392:
                                    irc.send(bytes("PRIVMSG " + channel + " :" + answer + "\n", "UTF-8"))
                                    answer = ""
                                else:
                                    last_space_index = answer[:392].rfind(" ")
                                    if last_space_index == -1:
                                        last_space_index = 392
                                    irc.send(bytes("PRIVMSG " + channel + " :" + answer[:last_space_index] + "\n", "UTF-8"))
                                    answer = answer[last_space_index:].lstrip()
                    except openai.error.Timeout as e:
                        print("Error: " + str(e))
                        irc.send(bytes("PRIVMSG " + channel + " :API call timed out. Try again later.\n", "UTF-8"))
                    except openai.error.OpenAIError as e:
                        print("Error: " + str(e))
                        irc.send(bytes(f"PRIVMSG {channel} :API call failed. {str(e)}\n", "UTF-8"))
                    except Exception as e:
                        print("Error: " + str(e))
                        irc.send(bytes(f"PRIVMSG {channel} :An unexpected error occurred. {str(e)}\n", "UTF-8"))
                elif model in images_models:
                    try:
                        response = openai.Image.create(
                        prompt="Q: " + question + "\nA:",
                        n=1,
                        size="1024x1024"
                        )
                        long_url = response.data[0].url
                        type_tiny = pyshorteners.Shortener()
                        short_url = type_tiny.tinyurl.short(long_url)
                        irc.send(bytes("PRIVMSG " + channel + " :" + short_url + "\n", "UTF-8"))
                    except openai.error.Timeout as e:
                        print("Error: " + str(e))
                        irc.send(bytes("PRIVMSG " + channel + " :API call timed out. Try again later.\n", "UTF-8"))
                    except openai.error.OpenAIError as e:
                        print("Error: " + str(e))
                        irc.send(bytes(f"PRIVMSG {channel} :API call failed. {str(e)}\n", "UTF-8"))
                    except Exception as e:
                        print("Error: " + str(e))
                        irc.send(bytes(f"PRIVMSG {channel} :An unexpected error occurred. {str(e)}\n", "UTF-8"))
                else:
                    print("Invalid model.")
                    irc.send(bytes("PRIVMSG " + channel + " :Invalid model.\n", "UTF-8"))
                    continue
    else:
        continue
    time.sleep(1)
