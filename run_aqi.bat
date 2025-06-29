@echo off
cd /d F:\SmartCityAI
call venv\Scripts\activate
python data_pipeline\fetch_air_quality.py > log.txt 2>&1
