#!/usr/bin/env bash

ps -ef | grep python | grep -v grep | grep openai | awk '{print $2}' | xargs kill  -9
cd /data/code/openai/ && git pull
nohup python3 /data/code/openai/app.py > /data/code/openai/nohup.log 2>&1 &
