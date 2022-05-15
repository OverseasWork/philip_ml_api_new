# -*- coding: utf-8 -*-
# @Time    : 2021/12/14 12:08 上午
# @Author  : HuangSir
# @FileName: log_config.py
# @Software: PyCharm
# @Desc: 日志配置

# interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
# S 秒
# M 分
# H 小时、
# D 天、
# W 每星期（interval==0时代表星期一）
# midnight 每天凌晨

from utils.log_utils import Logger

log = Logger(filename='log/log', level='info', when='D', backCount=90)
