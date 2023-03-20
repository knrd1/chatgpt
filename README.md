# ChatGPT
ChatGPT is a simple IRC bot written in python using Open AI endpoints to answer questions.

ChatGPT uses official bindings from OpenAI to interact with the API through HTTP requests:
https://platform.openai.com/docs/api-reference

### Prerequisities:

Create an account and obtain your API key: https://platform.openai.com/account/api-keys

Install python3 and the official Python bindings:
```
apt install python3 (Debian/Ubuntu)
yum install python3 (RedHat/CentOS)
pip3 install openai
```
### Configuration:

Edit chatgpt.py and change variables to the file. Example configuration for IRCNet:
```
openai.api_key = "sk-XXXXXXXXXXXXXXXX"
server = "open.ircnet.net"
port = 6667
channel = "#irc"
nickname = "MyBot"
```
Optionally you can edit the engine, the list of compatible engines below:
```
                engine="text-davinci-003",
```
IMPORTANT: When you specify "nickname", make sure you replace ALL occurences of ChatGPT in chatgpt.py file to the new nickname. For example, if your bot nick name is "MyBot", do:
```
$ sed -i 's/ChatGPT/MyBot/g' chatgpt.py
```
You can optionally adjust following settings, for more details see:
https://platform.openai.com/docs/api-reference/completions
```
            temperature=1,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
```
### Connecting bot to IRC server:
```
$ python3 chatgpt.py
```
### Interaction:
ChatGPT will interact only reply if you mention its nickname:
```
10:31:12 <@knrd1> ChatGPT: hello, how are you?
10:31:14 < ChatGPT> Hi there, I'm doing well, thank you. How about you?
```
### Model endpoint compatibility

ChatGPT uses endpoint /v1/completions. Following engines are compatible:
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
