# -*- coding: utf-8 -*-
# @Time    : 2021/11/6 11:35 下午
# @Author  : HuangSir
# @FileName: ml_router.py
# @Software: PyCharm
# @Desc: 模型路由

from fastapi import APIRouter

from app.app.v1.api import ml_score_v1
from app.app.v1.core.inputs import InputData

ml_router = APIRouter()

@ml_router.post('/app/v1/score',tags=['v1.0'])
async def score_v1(data:InputData):
    data = data.dict()
    res = ml_score_v1(data)
    return res
