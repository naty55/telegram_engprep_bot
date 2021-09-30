#!bin/bash
echo "[INFO] change directory to telegram_engprep_bot"
cd telegram_engprep_bot
echo "[INFO] pulling latest updates from github.com"
git pull
echo "[INFO] starting the bot"
python main.py


