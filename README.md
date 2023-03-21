# ChatGPT
ChatGPT is a simple IRC bot written in Python. It connects to OpenAI endpoints to answer questions.

ChatGPT uses official bindings from OpenAI to interact with the API through HTTP requests:
https://platform.openai.com/docs/api-reference

### Prerequisities:

Create an account and obtain your API key: https://platform.openai.com/account/api-keys

Install python3 and the official Python bindings:
```
apt install python3 (Debian/Ubuntu)
yum install python3 (RedHat/CentOS)
pip3 install openai
git clone https://github.com/knrd1/chatgpt.git
cd chatgpt
cp example-chat.conf chat.conf
```
### Configuration:

Edit chat.conf and change variables. Example configuration for IRCNet:
```
[openai]
api_key = sk-XXXXXXXXXXXXXXX

[irc]
server = open.ircnet.net
port = 6667
channel = #irc
nickname = MyBot
```
### Optional settings:

You can optionally adjust following settings in chatgpt.py, please see docs for more details:
https://platform.openai.com/docs/api-reference/completions
```
            temperature=0.8,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
```
Also, you can edit the model, the list of compatible models below:
```
                model="text-davinci-003",
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
### Model endpoint compatibility

ChatGPT uses endpoint v1/completions. Following models are compatible.
```
text-davinci-003
text-davinci-002
text-curie-001
text-babbage-001
text-ada-001
davinci
curie
babbage
ada
```
More details about models: https://platform.openai.com/docs/models
