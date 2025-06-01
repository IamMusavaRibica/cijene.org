#!/bin/bash

cd /home/musava/cijene_org
source .venv/bin/activate
exec uvicorn main:app --port 16163