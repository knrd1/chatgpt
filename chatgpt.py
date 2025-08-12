#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import ssl
import time
import configparser
from typing import List
import traceback
import base64
import uuid

from openai import OpenAI
import openai
import pyshorteners

config = configparser.ConfigParser()
config.read('chat.conf')

OPENAI_API_KEY = config.get('openai', 'api_key')
client = OpenAI(api_key=OPENAI_API_KEY)

model = config.get('chatcompletion', 'model').strip()
role = config.get('chatcompletion', 'role').strip()
context = config.get('chatcompletion', 'context').strip()
max_completion_tokens = config.getint('chatcompletion', 'max_completion_tokens')
top_p = config.getint('chatcompletion', 'top_p')
frequency_penalty = config.getint('chatcompletion', 'frequency_penalty')
presence_penalty = config.getint('chatcompletion', 'presence_penalty')
request_timeout = config.getint('chatcompletion', 'request_timeout')
reasoning_effort_conf = config.get('chatcompletion', 'reasoning_effort', fallback="medium").strip().lower()

server = config.get('irc', 'server')
port = config.getint('irc', 'port')
usessl = config.getboolean('irc', 'ssl')
channels = [ch.strip() for ch in config.get('irc', 'channels').split(',') if ch.strip()]
nickname = config.get('irc', 'nickname')
ident = config.get('irc', 'ident')
realname = config.get('irc', 'realname')
password = config.get('irc', 'password')

completion_models: List[str] = [m.strip() for m in config.get('models', 'completion_models', fallback="").split(",") if m.strip()]
chatcompletion_models: List[str] = [m.strip() for m in config.get('models', 'chatcompletion_models', fallback="").split(",") if m.strip()]
images_models: List[str] = [m.strip() for m in config.get('models', 'images_models', fallback="").split(",") if m.strip()]
web_search_models: List[str] = [m.strip() for m in config.get('features', 'web_search_models', fallback="").split(",") if m.strip()]

reasoning_models = [
    "o1", "o1-mini", "o3", "o3-mini", "o4", "o4-mini",
    "gpt-5", "gpt-5-mini", "gpt-5-nano"
]

def connect(server, port, usessl, password, ident, realname, nickname, channels):
    while True:
        try:
            print("Connecting to: " + server)
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            irc.connect((server, port))
            if usessl:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                irc = ctx.wrap_socket(irc, server_hostname=server)
            if password:
                irc.send(bytes("PASS " + password + "\n", "UTF-8"))
            irc.send(bytes("USER " + ident + " 0 * :" + realname + "\n", "UTF-8"))
            irc.send(bytes("NICK " + nickname + "\n", "UTF-8"))
            print("Connected to: " + server)
            return irc
        except Exception as e:
            print("Connection failed. Retrying in 5 seconds...")
            print(repr(e))
            time.sleep(5)

irc = connect(server, port, usessl, password, ident, realname, nickname, channels)

def send_long_message(irc_sock, channel: str, text: str, max_len: int = 392):
    text = text.replace("\r", "").replace("\n", " ").strip()
    while text:
        if len(text) <= max_len:
            irc_sock.send(bytes(f"PRIVMSG {channel} :{text}\n", "UTF-8"))
            break
        last_space_index = text[:max_len].rfind(" ")
        if last_space_index == -1:
            last_space_index = max_len
        irc_sock.send(bytes(f"PRIVMSG {channel} :{text[:last_space_index]}\n", "UTF-8"))
        text = text[last_space_index:].lstrip()

def answer_with_lines(irc_sock, channel: str, body: str):
    lines = [x.strip() for x in body.split("\n") if x.strip()]
    for line in lines:
        send_long_message(irc_sock, channel, line)

def _responses_call(full_input: str, use_search: bool):
    kwargs = {
        "model": model,
        "input": full_input,
        "temperature": 1,
        "top_p": top_p,
        "max_output_tokens": max_completion_tokens
    }
    if context:
        kwargs["instructions"] = context
    if use_search:
        kwargs["tools"] = [{"type": "web_search"}]
        kwargs["tool_choice"] = "auto"
    if model in reasoning_models:
        kwargs["reasoning"] = {"effort": reasoning_effort_conf}
    return client.with_options(timeout=float(request_timeout)).responses.create(**kwargs)

def generate_with_web_search(question: str) -> str:
    full_input = question if not context else f"{context}\n\n{question}"
    use_search = model in web_search_models
    try:
        resp = _responses_call(full_input, use_search)
    except openai.BadRequestError:
        resp = _responses_call(full_input, False)
    txt = getattr(resp, "output_text", None)
    if txt:
        return txt.strip()
    try:
        parts = []
        for item in (resp.output or []):
            if getattr(item, "type", "") == "message":
                for c in getattr(item, "content", []):
                    if getattr(c, "type", "") == "output_text":
                        parts.append(getattr(c, "text", ""))
        return "\n".join([p for p in parts if p]).strip() or "No content in the response."
    except Exception:
        return "Could not parse the response."

def generate_legacy_completion(question: str) -> str:
    comp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": context},
                  {"role": role, "content": question}],
        temperature=1,
        top_p=top_p
    )
    return comp.choices[0].message.content.strip()

def generate_image_url(prompt: str) -> str:
    gen = client.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024"
    )
    img_url = getattr(gen.data[0], "url", None)
    if img_url:
        try:
            short_url = pyshorteners.Shortener().tinyurl.short(img_url)
            return short_url
        except Exception:
            return img_url
    b64 = getattr(gen.data[0], "b64_json", None)
    if not b64:
        return "No URL or base64 data in image response."
    img_bytes = base64.b64decode(b64)
    fn = f"/tmp/oai_{uuid.uuid4().hex}.png"
    with open(fn, "wb") as f:
        f.write(img_bytes)
    return f"Image saved locally: {fn}"

while True:
    try:
        data = irc.recv(4096).decode("UTF-8", errors="ignore")
        if data:
            print(data)
    except Exception as e:
        print("Connection lost. Reconnecting...")
        print(repr(e))
        time.sleep(5)
        irc = connect(server, port, usessl, password, ident, realname, nickname, channels)
        continue

    irc.send(bytes("JOIN " + ",".join(channels) + "\n", "UTF-8"))

    chunk = data.split()
    if not chunk:
        time.sleep(1)
        continue

    if data.startswith(":"):
        command = chunk[1]
    else:
        command = chunk[0]

    if command == "PING":
        irc.send(bytes("PONG " + chunk[1] + "\n", "UTF-8"))
        time.sleep(1)
        continue

    if command == "ERROR":
        print("Received ERROR from server. Reconnecting...")
        time.sleep(5)
        irc = connect(server, port, usessl, password, ident, realname, nickname, channels)
        continue

    if command in ("471", "473", "474", "475"):
        print("Unable to join " + (chunk[3] if len(chunk) > 3 else "") + ": Channel may be full, invite-only, banned or require a key.")
        time.sleep(1)
        continue

    if command == "KICK" and len(chunk) > 3 and chunk[3] == nickname:
        irc.send(bytes("JOIN " + chunk[2] + "\n", "UTF-8"))
        print("Kicked from channel " + chunk[2] + ". Rejoining...")
        time.sleep(1)
        continue

    if command == "INVITE":
        target = data.split(" :")[1].strip() if " :" in data else ""
        if target in channels:
            irc.send(bytes("JOIN " + target + "\n", "UTF-8"))
            print("Invited into channel " + target + ". Joining...")
        time.sleep(1)
        continue

    if command == "PRIVMSG" and len(chunk) >= 4 and chunk[2].startswith("#") and chunk[3] == ":" + nickname + ":":
        channel = chunk[2].strip()
        try:
            question = data.split(nickname + ":")[1].strip()
        except Exception:
            question = ""
        try:
            if model in chatcompletion_models:
                answer_text = generate_with_web_search(question)
                answer_with_lines(irc, channel, answer_text)
            elif model in completion_models:
                answer_text = generate_legacy_completion(question)
                answer_with_lines(irc, channel, answer_text)
            elif model in images_models:
                info = generate_image_url(question)
                answer_with_lines(irc, channel, info)
            else:
                answer_with_lines(irc, channel, "Invalid model.")
        except openai.APITimeoutError:
            answer_with_lines(irc, channel, "API call timed out. Try again later.")
        except openai.BadRequestError as e:
            answer_with_lines(irc, channel, f"Bad request: {e.message}")
        except openai.RateLimitError:
            answer_with_lines(irc, channel, "Rate-limited. Please slow down.")
        except openai.APIError as e:
            answer_with_lines(irc, channel, f"API error: {e}")
        except Exception as e:
            traceback.print_exc()
            answer_with_lines(irc, channel, f"An unexpected error occurred. {str(e)}")

    time.sleep(1)
