# ChatGPT IRC Bot
ChatGPT IRC bot is a simple IRC bot written in Python. It connects to OpenAI endpoints to answer questions or generate images.

ChatGPT IRC Bot uses official bindings from OpenAI to interact with the API through HTTP requests:
https://platform.openai.com/docs/api-reference

### Prerequisities:

Create an account and obtain your API key: https://platform.openai.com/account/api-keys

Install python3 and the official Python bindings:
```
$ apt install python3 python3-pip (Debian/Ubuntu)
$ yum install python3 python3-pip (RedHat/CentOS)
$ pip3 install openai==0.28 pyshorteners
$ git clone https://github.com/knrd1/chatgpt.git
$ cd chatgpt
$ cp example-chat.conf chat.conf
```
### Configuration:

Edit chat.conf and change variables. Example configuration for IRCNet:

**There is a new variable "context", it's optional: you can leave it blank or enter what you want the bot to know and how you want the bot to behave. This will work only with models connecting to endpoint /v1/chat/completions.**

**e.g.: You are an ironic and arrogant bot on the #linux channel, James and Mark are on the channel with you. James loves to play guitar and Mark is a footballer. You speak Scottish slang.**
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
### Connecting bot to IRC server:
```
$ python3 chatgpt.py
```
Use screen to run bot in the background and keep it running even after you log out of your session:
```
$ screen python3 chatgpt.py
```
To detach from the screen session (leaving your ChatGPT IRC Bot running in the background), press Ctrl + A followed by d (for "detach").
If you need to reattach to the screen session later, use the following command:
```
screen -r
```
### Interaction:
ChatGPT IRC Bot will interact only if you mention its nickname:
```
10:31:12 <@knrd1> ChatGPT: hello, how are you?
10:31:14 < ChatGPT> Hi there, I'm doing well, thank you. How about you?
10:35:56 <@knrd1> ChatGPT: do you like IRC?
10:35:59 < ChatGPT> Yes, I like IRC. It is a great way to communicate with people from around the world.

```
If you set the model to "dalle", the ChatGPT IRC Bot will return a shortened URL to the generated image:
```
17:33:16 <@knrd1> ChatGPT: impressionist style painting: two horses dancing on the street
17:33:23 < ChatGPT> https://tinyurl.com/2hr5uf4w
```
### Model endpoint compatibility

ChatGPT IRC Bot can use three API endpoints: 

Following models support endpoint /v1/chat/completions:

> gpt-4, gpt-4-0613, gpt-4-1106-preview, gpt-4-vision-preview, gpt-4-32k, gpt-4-32k-0613, gpt-3.5-turbo, gpt-3.5-turbo-0613, gpt-3.5-turbo-16k, gpt-3.5-turbo-16k-0613

Models that support /v1/completions (Legacy):

> gpt-3.5-turbo-instruct, text-davinci-003, text-davinci-002, text-davinci-001, text-curie-001, text-babbage-001, text-ada-001, davinci, curie, babbage, ada, babbage-002, davinci-002

Create an image using endpoint /v1/images/generations:

> dalle

More details about models: https://platform.openai.com/docs/models

### Docker

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
