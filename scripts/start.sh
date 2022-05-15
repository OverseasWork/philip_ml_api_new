#!/bin/bash
conda activate ml_app
app_path=$(dirname "$PWD")
cd $app_path
nohup  gunicorn --conf=gconfig.py main:app >> nohup.out 2>&1 &
echo "starting finish"