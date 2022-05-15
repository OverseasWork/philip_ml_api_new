# -*- coding: utf-8 -*-
# @Time    : 2022/5/14 17:23
# @Author  : HuangSir
# @FileName: api.py
# @Software: PyCharm
# @Desc: 模型主程序

import sys
sys.path.append('..')

import warnings
warnings.filterwarnings('ignore')

from conf.log_config import log

from .lgb_predict import LgbModel

lgbMl = LgbModel()

def ml_score_v1(data:dict):
    log.logger.info(f"starting run busi_id  {data['busi_id']} -------------------------------------")
    res = lgbMl.predict(data)
    log.logger.info(f"end  busi_id  {data['busi_id']} ---------------------------------------------")
    return res