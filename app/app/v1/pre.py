# -*- coding: utf-8 -*-
# @Time    : 2022/5/13 11:28
# @Author  : HuangSir
# @FileName: pre.py
# @Software: PyCharm
# @Desc:数据预处理

import warnings

warnings.filterwarnings('ignore')

import sys

sys.path.append('..')

import re
import pandas as pd
import numpy as np

from conf.log_config import log
from utils.load_utils import load_data
from utils.decorator import log_run_time
from typing import List
from datetime import datetime
from utils.pre_utils import split_rom_ram,split_screen

class BaseInfoPre:
    def __init__(self):
        super().__init__()
        pass

    def base_info_pre(self,base_info:dict):
        # 可用内存
        # usable_ram, _ = split_rom_ram(base_info['ram'])
        # 可用存储
        # usable_memory, _ = split_rom_ram(base_info['rom'])
        # 分辨率
        _, RESOLUTION_Y = split_screen(base_info['resolution'])

        res = {
            'sex':base_info['sex'],'age':base_info['age'],'BRANDS':base_info['brands'],
            'marry':base_info['marry'],'usable_ram':base_info['usable_ram'],
            'usable_memory':base_info['usable_memory'],
            'RESOLUTION_Y':RESOLUTION_Y
        }
        return res

class AddPre:
    def __init__(self):
        """通讯录预处理"""
        super(AddPre, self).__init__()
        self.path_db = 'app/app/v1/db/'
        self.dito_seg = load_data(self.path_db + 'DITO.txt')
        self.dito_seg = '|'.join(self.dito_seg)

        self.globe_seg = load_data(self.path_db + 'GLOBE.txt')
        self.globe_seg = '|'.join(self.globe_seg)

        self.smart_seg = load_data(self.path_db + 'SMART.txt')
        self.smart_seg = '|'.join(self.smart_seg)

        self.sun_seg = load_data(self.path_db + 'SUN.txt')
        self.sun_seg = '|'.join(self.sun_seg)

        self.total_seg = '|'.join([self.dito_seg, self.globe_seg, self.smart_seg, self.sun_seg])

    def __add_valid(self, row):
        '''
        通讯录有效验证
        Args:
            row:dataFrame
            tday: 下单日期

        Returns:tuple

        '''
        # 通讯录号码清洗
        phone, name, updateADD_tday = row['phone'], row['name'], row['updateADD_tday']

        name = ''.join(filter(str.isalpha, name))
        phone = ''.join(filter(str.isdigit, phone.lstrip('+63|0')))

        # 昵称为空，或中文
        if not name or bool(re.search(r'([\u4e00-\u9fa5]+)', name)):
            return name, phone, 0
        # 号码为空 或长度不为10
        elif not phone or len(phone) != 10:
            return name, phone, 0
        # 创建时间异常
        elif updateADD_tday > 1080 or updateADD_tday < 0:
            return name, phone, 0
        # 号码符合运营商
        elif bool(re.search(self.total_seg, phone[:3])):
            return name, phone, 1
        else:
            return name, phone, 0

    def __add_operator(self, row):
        '''
        添加运营商
        Args:
            row: addbook dataFrame

        Returns:

        '''
        phone, valid = row['phone'], row['validADD']
        # 添加运营商
        if valid == 0:
            return 'OTHER'
        elif bool(re.search(self.dito_seg, phone[:3])):
            return 'DITO'
        elif bool(re.search(self.globe_seg, phone[:3])):
            return 'GLOBE'
        elif bool(re.search(self.smart_seg, phone[:3])):
            return 'SMART'
        elif bool(re.search(self.sun_seg, phone[:3])):
            return 'SUN'
        else:
            return 'OTHER'

    def __add_pre(self, addBook: List[dict], apply_date: str):
        '''
        通讯录预处理
        Args:
            addBook: addbook origin
            apply_date: str

        Returns: addbook clear

        '''
        try:
            apply_date = pd.to_datetime(apply_date)
        except:
            apply_date = pd.to_datetime(datetime.now()).date()

        if addBook:
            try:
                add_df = pd.DataFrame(addBook)
            except Exception as err:
                raise_str = f'when {addBook} convert to dataframe happen {err}'
                log.logger.error(raise_str)
                raise ValueError(raise_str)

             # 更新距今天数
            add_df['last_update'] = add_df['last_update'].astype('datetime64')
            add_df['updateADD_tday'] = (apply_date - add_df['last_update']).dt.days
            # 有效检验
            add_df[['name', 'phone', 'validADD']] = add_df.apply(lambda row: self.__add_valid(row),
                                                                 axis=1,result_type='expand')
            # 添加运营商
            add_df['operator'] = add_df.apply(self.__add_operator, axis=1)
            # 通讯录去重
            add_df.drop_duplicates(subset='phone', inplace=True, ignore_index=False)
            return add_df
        else:
            log.logger.warning(f'{addBook} is empty')
            return pd.DataFrame()

    def __drop_invalid(self,add_df:pd.DataFrame):
        '''
        删除无效通讯录
        Args:
            add_df:

        Returns:

        '''
        # 剔除无效通讯录
        log.logger.info(f'addBook of origin size {add_df.shape}')
        add_df = add_df[add_df.validADD == 1]
        log.logger.info(f'drop invalid addBook of size {add_df.shape}')

        add_df = add_df[add_df.name.notnull()]
        # log.logger.info(f'drop empty name of size {add_df.shape}')

        add_df = add_df[add_df.updateADD_tday.notnull()]
        # log.logger.info(f'drop empty updateADD_tday of size {add_df.shape}')
        return add_df

    @log_run_time
    def add_pre(self,addBook: List[dict], apply_date: str):
        '''
        通讯录预处理
        Args:
            addBook:
            apply_date:

        Returns:

        '''
        add_df = self.__add_pre(addBook,apply_date)
        add_df = self.__drop_invalid(add_df)
        return add_df



class AppPre:
    def __init__(self):
        """appList 预处理"""
        super(AppPre, self).__init__()
        self.path_db = 'app/app/v1/db/'
        self.business = load_data(self.path_db + 'business.xlsx')
        self.business['app_type'] = 'business'

        self.contact = load_data(self.path_db + 'contact.xlsx')
        self.contact['app_type'] = 'contact'

        self.finance = load_data(self.path_db + 'finance.xlsx')
        self.finance['app_type'] = 'finance'

        self.games = load_data(self.path_db + 'games.xlsx')
        self.games['app_type'] = 'games'

        self.loans = load_data(self.path_db + 'loans.xlsx')
        self.loans['app_type'] = 'loans'

        self.type_df = pd.concat([self.loans, self.finance, self.games, self.business, self.contact], ignore_index=True)
        self.type_df = self.type_df.drop_duplicates(subset='package', ignore_index=True)
        self.type_df = self.type_df[self.type_df.columns.difference(['name'])]
        self.type_df = self.type_df.rename(columns={'package': 'app_pack_name'})

        self.loan_app_keys = load_data(self.path_db + 'K-loan.txt')
        self.loan_app_keys = '|'.join(self.loan_app_keys)

    def __search_loans(self, row):
        # 关键词APP标签
        name, package = row['app_name'], row['app_pack_name']
        t1 = re.search(self.loan_app_keys, name.lower().replace(' ', ''))
        t2 = re.search(self.loan_app_keys, package.lower().replace(' ', ''))
        if bool(t1) or bool(t2):
            return 'Kloan'
        else:
            return 'other'

    def __app_valid(self, row):
        # 有效app验证
        if str(row['updateAPP_tday']) == 'nan' or str(row['install_updateday']) == 'nan':
            return 0

        elif row['updateAPP_tday'] < 0 or row['updateAPP_tday'] > 720 or \
                row['installAPP_tday'] < 0 or row['installAPP_tday'] > 1800:
            return 0

        elif (row['app_name'] == row['app_pack_name']
        ) or (str(row['app_name']) == 'nan'
        ) or (str(row['app_pack_name']) == 'nan'
        ) or (str(row['app_name']).replace(' ', '') == ''):
            return 0

        elif bool(re.search(r'([\u4e00-\u9fa5]+)', row['app_name'])):
            return 0

        elif bool(re.search(r'^com\.|^android\.|\.com$|\.product$', row['app_name'])):
            return 0

        elif str(row['app_name']).count('.') >= 2:
            return 0

        else:
            return 1

    def __app_pre(self, appList: List[dict], apply_date: str):
        '''
        appList预处理
        Args:
            app_df:appList origin

        Returns: app_clear_df

        '''
        try:
            apply_date = pd.to_datetime(apply_date)
        except:
            apply_date = pd.to_datetime(datetime.now()).date()

        if appList:
            try:
                app_df = pd.DataFrame(appList)
            except Exception as err:
                raise_str = f'when {appList} convert to dataframe happen {err}'
                log.logger.error(raise_str)
                raise ValueError(raise_str)

            cols = ['last_update_time', 'first_install_time']
            app_df[cols] = app_df[cols].astype('datetime64')
            # 标记
            app_df = pd.merge(app_df, self.type_df, on='app_pack_name', how='left')
            app_df['app_type'] = app_df.apply(lambda row: row['app_type'] if str(row['app_type']) != 'nan' \
                else self.__search_loans(row), axis=1)
            # 更新距今天数
            app_df['updateAPP_tday'] = (apply_date - app_df['last_update_time']).dt.days
            # 安装距今天数
            app_df['installAPP_tday'] = (apply_date - app_df['first_install_time']).dt.days
            # 安装到更新日期差
            app_df['install_updateday'] = (app_df['last_update_time'] - app_df['first_install_time']).dt.days
            # 有效app valid
            app_df['validAPP'] = app_df.apply(lambda row: self.__app_valid(row), axis=1)
            # 根据包名去重
            app_df.drop_duplicates(subset='app_pack_name', inplace=True, ignore_index=False)
            return app_df
        else:
            log.logger.error(f'{appList} is empty')
            return pd.DataFrame()

    def __drop_invalid(self,app_df:pd.DataFrame):
        '''
        删除无效applist
        Args:
            app_df:

        Returns:

        '''
        # 剔除无效app
        log.logger.info(f'appList of origin size {app_df.shape}')
        # app_df = app_df[app_df.validAPP == 1]
        # log.logger.info(f'drop invalid appList of size {app_df.shape}')

        app_df = app_df[app_df.app_name.notnull()]
        log.logger.info(f'drop empty name of size {app_df.shape}')

        app_df = app_df[app_df.updateAPP_tday.notnull()]
        log.logger.info(f'drop empty updateAPP_tday of size {app_df.shape}')

        app_df = app_df[app_df.installAPP_tday.notnull()]
        log.logger.info(f'drop empty installAPP_tday of size  {app_df.shape}')

        return app_df

    @log_run_time
    def app_pre(self,appList: List[dict], apply_date: str):
        '''
        appList 预处理
        Args:
            appList:
            apply_date:

        Returns:

        '''
        app_df = self.__app_pre(appList,apply_date)
        app_df = self.__drop_invalid(app_df)
        # 去重
        app_df = app_df.drop_duplicates(subset=['app_pack_name'], ignore_index=True)
        return app_df