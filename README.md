# ChatGPT
ChatGPT is a simple IRC bot written in Python. It connects to OpenAI endpoints to answer questions or generate images.

ChatGPT uses official bindings from OpenAI to interact with the API through HTTP requests:
https://platform.openai.com/docs/api-reference

### Prerequisities:

Create an account and obtain your API key: https://platform.openai.com/account/api-keys

Install python3 and the official Python bindings:
```
$ apt install python3 python3-pip (Debian/Ubuntu)
$ yum install python3 python3-pip (RedHat/CentOS)
$ pip3 install openai
$ pip3 install pyshorteners
$ git clone https://github.com/knrd1/chatgpt.git
$ cd chatgpt
$ cp example-chat.conf chat.conf
```
### Configuration:

Edit chat.conf and change variables. Example configuration for IRCNet:
```
[openai]
api_key = sk-XXXXXXXXXXXXXXX

[chatcompletion]
model = gpt-3.5-turbo
role = user
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
channels = #knrd1,#github
nickname = MyBot
ident = mybot
realname = My Bot
password = 
```
### Connecting bot to IRC server:
```
$ python3 chatgpt.py
```
### Interaction:
ChatGPT will interact only if you mention its nickname:
```
10:31:12 <@knrd1> ChatGPT: hello, how are you?
10:31:14 < ChatGPT> Hi there, I'm doing well, thank you. How about you?
10:35:56 <@knrd1> ChatGPT: do you like IRC?
10:35:59 < ChatGPT> Yes, I like IRC. It is a great way to communicate with people from around the world.

```
If you set the model to "dalle", the ChatGPT IRC bot will return a shortened URL to the generated image:
```
17:33:16 <@knrd1> ChatGPT: two horses dancing on the street
17:33:23 < ChatGPT> https://tinyurl.com/2hr5uf4w
```
### Model endpoint compatibility

ChatGPT IRC bot can use three API endpoints.

Following models support endpoint /v1/chat/completions:
```
gpt-4, gpt-4-0314, gpt-4-32k, gpt-4-32k-0314, gpt-3.5-turbo, gpt-3.5-turbo-0301
```
Models that support /v1/completions:
```
text-davinci-003, text-davinci-002, text-curie-001, text-babbage-001, text-ada-001, davinci, curie, babbage, ada
```
Use the "dalle" model to generate the image:
```
dalle
```
More details about models: https://platform.openai.com/docs/models
