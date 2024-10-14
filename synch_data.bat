@echo off
call .venv\scripts\activate
python load_data.py
git add .\data\*.*
git commit -m "Data synch"
git push
call .venv\scripts\deactivate