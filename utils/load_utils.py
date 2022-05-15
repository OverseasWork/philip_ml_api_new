# -*- coding: utf-8 -*-
# @Time    : 2021/3/24 9:47 上午
# @Author  : HuangSir
# @FileName: load_utils.py
# @Software: PyCharm
# @Desc:

import sys
sys.path.append('..')
import joblib
import pandas as pd

def load_data(filename:str):
    if '.txt' in filename:
        with open(filename,'r') as f:
            dt = f.read().split('\n')
            dt = [i for i in dt if i]
        return dt
    elif '.pkl' in filename:
        dt = joblib.load(filename)
        return dt
    elif '.xlsx' in filename:
        dt = pd.read_excel(filename)
        return dt
    elif '.csv' in filename:
        dt = pd.read_csv(filename)
        return dt
    else:
        raise ValueError(f'{filename} fail identify filename types')
