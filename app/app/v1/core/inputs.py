# -*- coding: utf-8 -*-
# @Time    : 2022/5/10 22:36
# @Author  : HuangSir
# @FileName: inputs.py
# @Software: PyCharm
# @Desc: 输入参数校验

from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from .example import ex_base_info, ex_add_book, ex_app_list


class AppList(BaseModel):
    """appList"""
    app_name: str = Field(title='APP名', description='app名称,原始值')
    app_pack_name: str = Field(title='包名', description='app包名,,原始值')
    first_install_time: str = Field(title='首次安装时间', description='首次安装时间,需要转成%Y-%m-%d时间格式,精确到日')
    last_update_time: str = Field(title='最近更新时间', description='最近更新时间戳,需要转成%Y-%m-%d时间格式,精确到日')


class AddBook(BaseModel):
    """通讯录"""
    phone: str = Field(title='电话号码', description='电话号码,原始值')
    name: str = Field(title='姓名', description='姓名,原始值')
    last_update: str = Field(title='最近更新时间', description='最近更新时间戳,需要转成%Y-%m-%d时间格式,精确到日')


class SexEnum(int, Enum):
    __doc__ = '性别枚举'
    Male = 1
    Female = 0


class MarryEnum(int, Enum):
    __doc__ = '婚姻枚举'
    Married = 0
    Unmarried = 1
    Widowed = 2
    Divorced = 3


class BrandsEnum(int, Enum):
    __doc__ = '手机品牌'
    oppo = 0
    samsung = 1
    vivo = 2
    realme = 3
    huawei = 4
    xiaomi = 5
    redmi = 6
    other = -999


class BaseInfo(BaseModel):
    """基础信息"""
    sex: SexEnum = Field(title='性别', description="{'Female':0,'Male':1}")
    age: int = Field(title='年龄', ge=18, lt=60, description='年龄')
    brands: BrandsEnum = Field(title='手机品牌',
                               description="{'oppo':0,'samsung':1,'vivo':2,'realme':3,'huawei':4,'xiaomi':5,'redmi':6,'other':-999}")
    marry: MarryEnum = Field(title='婚姻', description="{'Married':0,'Unmarried':1,'Widowed':2,'Divorced':3}")
    usable_ram: float = Field(title='剩余可用内存,/GB', description='剩余可用内存大小, 单位GB,若是 MB 请预先转化成 GB')
    usable_memory: float = Field(title='剩余可用存储,/GB', description='剩余可用存储, 单位GB,若是 MB 请预先转化成 GB')
    resolution: str = Field(title='设备分辨率', description='设备分辨率,x_y_z')


class InputData(BaseModel):
    """模型入参"""
    __doc__ = "模型接口入参"
    busi_id: str = Field(title='交易订单号', description='唯一标识符', example='1020220323184936000134038')

    base_info: BaseInfo = Field(default=..., title='客户基本信息', example=ex_base_info)
    app_list: List[AppList] = Field(default=..., title='app列表', example=ex_app_list)
    add_book: List[AddBook] = Field(default=..., title='通讯录', example=ex_add_book)

    apply_date: str = Field(title='申请日期,需要转成 %Y-%m-%d 时间格式,精确到日', example='2022-03-23')
