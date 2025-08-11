# ChatGPT IRC Bot

A simple Python-based IRC bot for ChatGPT, now upgraded with modern OpenAI API support.

## ChatGPT IRC Bot now supports online web search!

### August 2025 major upgrade - important for existing users

- You **must** reinstall/upgrade to **OpenAI Python SDK 1.x**:
 ```
pip3 install "openai>=1.0.0"
```
- You **must** re-configure your configuration file chat.conf with new variables and models. Legacy "completions" models are no longer supported.

### What’s new?

- Fully migrated to **OpenAI Python SDK v1.x**.
- Enabled **web search integration** - model will fetch live information when needed.
- Configuration-driven model selection:
  - Variable `model` defines the current mode (text or image).
  - Lists of supported chat and image models are now maintained in `chat.conf`.

### Prerequisities:

Create an account and obtain your API key: https://platform.openai.com/account/api-keys

Install python3 and the official Python bindings:
```
$ apt install python3 python3-pip (Debian/Ubuntu)
$ yum install python3 python3-pip (RedHat/CentOS)
$ pip3 install "openai>=1.0.0"  pyshorteners
$ git clone https://github.com/knrd1/chatgpt.git
$ cd chatgpt
$ cp example-chat.conf chat.conf
```
### Configuration:

Edit chat.conf and adjust variables. Example configuration for IRCNet:

Variable "context" is optional: you can leave it blank or enter what you want the bot to know and how you want the bot to behave. This will work only with models connecting to endpoint /v1/chat/completions

```
[openai]
api_key = <YOUR_API_KEY_HERE>

[chatcompletion]
model = gpt-5-mini
role = user
context = 
max_completion_tokens = 4096
top_p = 1
frequency_penalty = 0
presence_penalty = 0
request_timeout = 60

[irc]
server = open.ircnet.net
port = 6667
ssl = false
channels = #linux,github
nickname = ChatGPT
ident = chatgpt
realname = ChatGPT IRC Bot
password = 

[models]
chatcompletion_models = gpt-5,gpt-5-mini,gpt-5-nano,gpt-5-chat,GPT-4.1,GPT-4.1-mini,o1,o1-preview,o1-mini,o3,o3-mini,o3-pro,o4-mini,o4-mini-high
images_models = dall-e-3,gpt-image-1

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
11:52:56 <@knrd1> ChatBot: Check online to see what the weather forecast is for tomorrow in London?
11:53:07 < ChatGPT> Tomorrow (August 12, 2025) in London: mostly sunny and warm. Low about 19°C (66°F) in the early morning, rising to a high near 33°C (91°F) in the mid/late afternoon. Evening will cool into the high 20s °C. Hourly conditions show sunshine/clear to partly sunny throughout the day (no rain indicated).

```
If you set the model to "dall-e-3", the ChatGPT IRC Bot will return a shortened URL to the generated image:
```
17:33:16 <@knrd1> ChatGPT: impressionist style painting: two horses dancing on the street
17:33:23 < ChatGPT> https://tinyurl.com/2hr5uf4w
```
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
