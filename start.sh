#!/bin/bash

# 后台启动 Scrapyd
scrapyd &

# 后台部署 Scrapyd
sleep 2
scrapyd-deploy &

# 启动 Flask 应用作为主进程
python flask_app.py
