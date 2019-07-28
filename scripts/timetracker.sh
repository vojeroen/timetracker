#!/usr/bin/env bash

cd /app

PYTHONPATH=.:${PYTHONPATH} alembic upgrade head
gunicorn --workers=4 --bind=0.0.0.0:8000 --pid=pid app.timer:app 
