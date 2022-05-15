#!/bin/bash
conda create -n venv python=3.8
source activate venv
echo "完成虚拟环境venv创建"
target=$(dirname "$PWD")
echo "$target"
cd $target
pip install -r requirements.txt
echo "完成依赖安装"
