import openai
import socket
import time
import configparser

# Read configuration from file
config = configparser.ConfigParser()
config.read('chat.conf')

# Set up OpenAI API key
openai.api_key = config.get('openai', 'api_key')

# Set up IRC connection settings
server = config.get('irc', 'server')
port = config.getint('irc', 'port')
channel = config.get('irc', 'channel')
nickname = config.get('irc', 'nickname')

# Connect to IRC server
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))
irc.send(bytes("USER " + nickname + " " + nickname + " " + nickname + " :" + nickname + "\n", "UTF-8"))
irc.send(bytes("NICK " + nickname + "\n", "UTF-8"))
irc.send(bytes("JOIN " + channel + "\n", "UTF-8"))

# Listen for messages from users
while True:
    message = irc.recv(2048).decode("UTF-8")
    if message.find("PING") != -1:
        # Respond to server PING requests
        irc.send(bytes("PONG " + message.split()[1] + "\n", "UTF-8"))
    elif message.find("PRIVMSG " + channel + " :" + nickname + ":") != -1:
        question = message.split(nickname + ":")[1].strip()
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Q: " + question + "\nA:",
            temperature=0.8,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        answers = [x.strip() for x in response.choices[0].text.strip().split('\n')]
        for answer in answers:
            while len(answer) > 0:
                irc.send(bytes("PRIVMSG " + channel + " :" + answer[:400] + "\n", "UTF-8"))
                answer = answer[400:]
    time.sleep(1)
