#!/bin/sh

pip install --no-cache-dir pipenv 
pipenv install --system --deploy --clear

python3 subscriber.py

uvicorn main:app --reload