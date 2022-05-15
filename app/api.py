# -*- coding: utf-8 -*-
# @Time    : 2020/10/29 8:49 下午
# @Author  : HuangSir
# @FileName: api.py
# @Software: PyCharm
# @Desc:

import warnings
warnings.filterwarnings('ignore')

from .routers import risk_router_init
from fastapi import FastAPI


description = """
* 客户评分越高风险越低,评分范围:\t300~850, <br> **--999**:\t表示无法评分或程序BUG
* 模型接口入参详情见:\t**InputData**
"""


def create_app():
    app = FastAPI(title='新客风险评分评级模型',
                  description=description)
    risk_router_init(app)
    return app
