# ChatGPT IRC Bot
ChatGPT IRC Bot is a simple IRC bot written in Python. It connects to OpenAI endpoints to answer questions or generate images and uses official bindings from OpenAI to interact with the API through HTTP requests.

https://platform.openai.com/docs/api-reference

## Prerequisites
1. Create an account and obtain your API key: https://platform.openai.com/account/api-keys
2. Install Python3 and the official Python bindings (openai: 0.28.0, 0.28.1; pyshorteners)
   * Debian/Ubuntu
     ```
     apt install python3 python3-pip
     pip3 install openai==0.28.1 pyshorteners
     ```
   * RedHat/CentOS
     ```
     yum install python3 python3-pip
     pip3 install openai==0.28.1 pyshorteners
     ```
   * FreeBSD
     ```
     pkg install python311 py311-pip
     pip install openai==0.28.1 pyshorteners
     ```

## Installation
```
git clone https://github.com/knrd1/chatgpt.git
```

## Configuration
ChatGPT IRC Bot uses __chat.conf__ plaintext file as its configuration file. The package includes an example IRCnet configuration file (example-chat.conf) which you can copy and modify.
```
cd chatgpt
cp example-chat.conf chat.conf
```
> Variable __context__ is optional, you can leave it blank or enter what you want the bot to know and how you want the bot to behave. This will work only with models connecting to endpoint /v1/chat/completions (see below).

```
[openai]
api_key = sk-XXXXXXXXXXXXXXX

[chatcompletion]
model = gpt-3.5-turbo
role = user
context = You are a helpful and friendly bot on IRC channel #linux.
temperature = 0.8
max_tokens = 1000
top_p = 1
frequency_penalty = 0
presence_penalty = 0
request_timeout = 60

[irc]
server = open.ircnet.net
port = 6667
ssl = false
channels = #linux,#github
nickname = MyBot
ident = mybot
realname = My Bot
password = 
```

## Running bot
To start bot, run the command below.
* Debian/Ubuntu/RedHat/CentOS
  ```
  python3 chatgpt.py
  ```
* FreeBSD
  ```
  python3.11 chatgpt.py
  ```

Use __screen__ to run bot in the background and keep it running even after you log out of your session:
* Debian/Ubuntu/RedHat/CentOS
  ```
  screen python3 chatgpt.py
  ```
* FreeBSD
  ```
  screen python3.11 chatgpt.py
  ```

To detach from the __screen__ session (leaving your ChatGPT IRC Bot running in the background), press Ctrl + A followed by d (for "detach").
If you need to reattach to the screen session later, use the following command:
```
screen -r
```

## Interaction
ChatGPT IRC Bot will interact only if you mention its nickname.
```
10:31:12 <@knrd1> ChatGPT: hello, how are you?
10:31:14 < ChatGPT> Hi there, I'm doing well, thank you. How about you?
10:35:56 <@knrd1> ChatGPT: do you like IRC?
10:35:59 < ChatGPT> Yes, I like IRC. It is a great way to communicate with people from around the world.
```

If you set the model to __dall-e-2__ or __dall-e-3__, the ChatGPT IRC Bot will return a shortened URL to the generated image.
```
17:33:16 <@knrd1> ChatGPT: impressionist style painting: two horses dancing on the street
17:33:23 < ChatGPT> https://tinyurl.com/2hr5uf4w
```

## Model endpoint compatibility
ChatGPT IRC Bot can use three API models:
* Models that support endpoint /v1/chat/completions
  > gpt-4o-mini, gpt-4o, gpt-4, gpt-4-turbo, gpt-4-turbo-preview, gpt-3.5-turbo
* Models that support /v1/completions (Legacy)
  > gpt-3.5-turbo-instruct, babbage-002, davinci-002
* Models that support the creation of an image using endpoint /v1/images/generations
  > dall-e-2, dall-e-3

More details about models: https://platform.openai.com/docs/models

## Docker
To build the Docker image, you can use the following command:
```
docker build -t my-chatgpt-app .
```
To run the Docker container, you can use the following command:
```
docker run -it my-chatgpt-app
```
To detach from a running Docker, press Ctrl + P. While holding down Ctrl, press Q.
To reattach to the container later, use the following command:
```
docker attach <container_id>
```
