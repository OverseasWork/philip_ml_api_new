# -*- coding: utf-8 -*-
# @Time    : 2022/5/14 23:42
# @Author  : HuangSir
# @FileName: decorator.py
# @Software: PyCharm
# @Desc:

from functools import wraps

from conf.log_config import log

from datetime import datetime

def log_run_time(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        t0 = datetime.now()
        res = func(*args,**kwargs)
        t1 = datetime.now()
        log.logger.info(f'current function {func.__name__} cost time is {(t1-t0).seconds}')
        return res
    return wrapper