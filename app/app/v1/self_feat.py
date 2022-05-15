# -*- coding: utf-8 -*-
# @Time    : 2022/5/14 01:20
# @Author  : HuangSir
# @FileName: feat.py
# @Software: PyCharm
# @Desc: 特征工程

import sys
sys.path.append('..')

import warnings

warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from conf.log_config import log
from typing import List
import copy
from utils.load_utils import load_data
from utils.decorator import log_run_time


class SelfFeat:
    def __init__(self):
        super(SelfFeat, self).__init__()
        # 入模变量
        self.path_data = 'app/app/V1/data/'
        self.MlFeat = load_data(f'{self.path_data}feat.txt')
        # 通讯录
        self.seq_var_add = 'updateADD_tday'
        self.seq_group_add = 'operator'
        self.seq_bins_add = [0, 7, 45, 180, np.inf]
        self.self_feat_add = [i for i in self.MlFeat if '_'.join([self.seq_var_add,self.seq_group_add])+'_' in i]

        # appList1
        self.seq_var_app1='updateAPP_tday'
        self.seq_group_app1='app_type'
        self.seq_bins_app1 = [0, 1, 3, 7, 10, 15, 30, 60, 150, 360, np.inf]
        self.self_feat_app1 = [i for i in self.MlFeat if '_'.join([self.seq_var_app1,self.seq_group_app1])+'_' in i]

        # appList2
        self.seq_var_app2='installAPP_tday'
        self.seq_group_app2='app_type'
        self.seq_bins_app2 = [0, 5, 15, 30, 90, 150, 240, 450, 650, 1080, np.inf]
        self.self_feat_app2 = [i for i in self.MlFeat if '_'.join([self.seq_var_app2, self.seq_group_app2]) + '_' in i]

    def __cal_seq_varbins(self, df: pd.DataFrame, seq_bins: List[int], seq_var: str, seq_group: str = None):
        """
        时间切片及类型
        df: 数据框
        seq_bins:序列切片，[0,1,5,15,30,60,120,180,360,np.inf]
        seq_var:序列变量,必须是数值类型
        seq_group:分组变量， 类别变量，能穷举
        """
        if df.empty:
            return pd.DataFrame()
        labels = seq_bins[1:]
        # total 每个切片
        total_cut = pd.cut(x=df[seq_var], bins=seq_bins, include_lowest=True, labels=labels)
        total_df = pd.value_counts(total_cut)  # 每个切片总数
        cols = ['total']
        if seq_group:
            # 序列组别
            df[seq_group] = df[seq_group].astype('str')
            for seq_type in df[seq_group].unique():
                cols.append(seq_type)
                tmp_df = df.loc[df[seq_group] == seq_type, seq_var]
                tmp_cut = pd.cut(x=tmp_df, bins=seq_bins, include_lowest=True, labels=labels)
                tmp_df = pd.value_counts(tmp_cut)  # 统计每个组别的样本量
                total_df = pd.concat([total_df, tmp_df], axis=1)
            # 重置表头
            total_df.columns = cols
        else:
            total_df = pd.DataFrame(total_df)
            total_df.columns = ['total']
        # 索引并排序
        total_df.sort_index(inplace=True)
        # 累计求和
        total_cumsum = total_df.cumsum()
        total_cumsum.columns = ['sum_' + str(i) for i in total_df.columns]

        result_df = pd.concat([total_df, total_cumsum], axis=1)
        # 总占比,累计占比
        cols = copy.deepcopy(result_df.columns.tolist())
        for col in cols:
            if col == 'sum_total':
                result_df['sum_total_rate'] = round(result_df['sum_total'] / max(result_df['sum_total']), 2)
            elif col != 'total' and 'sum' not in str(col):
                # 组别切片与总切片比
                result_df[col + '_rate'] = result_df.apply(lambda row: -999 if row['total'] == 0
                else round(row[col] / row['total'], 2), axis=1)
                # 组别切片比率 与 组别平均比率 比
                avg_rate = max(result_df['sum_' + col]) / max(result_df['sum_total'])
                result_df[col + '_lift'] = result_df.apply(lambda row: round(row[col + '_rate'] / avg_rate, 2
                                                                             ) if row[col + '_rate'] != -999 else -999,
                                                           axis=1)

            elif 'sum' in str(col) and col != 'sum_total':
                # 组别累计增率与总增率 比
                result_df[col + '_total_rate'] = result_df.apply(lambda row: -999 if row['sum_total'] == 0
                else round(row[col] / row['sum_total'], 2), axis=1)
                # 组别增率
                result_df[col + '_rate'] = result_df.apply(lambda row: -999 if max(result_df[col]) == 0
                else round(row[col] / max(result_df[col]), 2), axis=1)
                # 组别增率 与 总增率差异
                result_df[col + '_ks'] = result_df.apply(
                    lambda row: round(row[col + '_rate'] - row['sum_total_rate'], 2)
                    if row[col + '_rate'] != -999 else -999, axis=1)
                # 拉平宽表 -------------------------------
        result_df.index = [str(i) + 'D' for i in result_df.index]
        res = result_df.stack().reset_index()
        res['cols'] = seq_var + '_' + seq_group + '_' + res['level_0'].astype('str') + '_' + res['level_1'].astype(
            'str')
        res = res[['cols', 0]].T
        res.columns = [i.replace('.0', '').replace('inf', 'all') for i in res[res.index == 'cols'].values.tolist()[0]]
        res = res[res.index == 0]
        return res


    @log_run_time
    def __self_add_feat(self,add_df:pd.DataFrame):
        '''
        通讯录自定义衍生变量
        Args:
            add_df:
            seq_bins:
            seq_var:
            seq_group:

        Returns:

        '''
        df = self.__cal_seq_varbins(df=add_df, seq_bins=self.seq_bins_add, seq_var=self.seq_var_add,
                                  seq_group=self.seq_group_add)
        # 缺失填充
        fill_col = list(set(self.self_feat_add) - set(df.columns))
        if fill_col:
            df.loc[:,fill_col] = -999
        return df

    @log_run_time
    def __self_app_feat(self,app_df:pd.DataFrame):
        '''appList自定义衍生变量'''
        # 剔除无效app,检查是否删除
        log.logger.info(f'appList of origin size {app_df.shape}')
        app_df = app_df[app_df.validAPP == 1]
        log.logger.info(f'drop invalid appList of size {app_df.shape}')
        # -------------------
        df1 = self.__cal_seq_varbins(df=app_df, seq_bins=self.seq_bins_app1, seq_var=self.seq_var_app1,
                                   seq_group=self.seq_group_app1)
        # 缺失填充
        fill_col = list(set(self.self_feat_app1) - set(df1.columns))
        if fill_col:
            df1.loc[:, fill_col] = -999

        df2 = self.__cal_seq_varbins(df=app_df, seq_bins=self.seq_bins_app2, seq_var=self.seq_var_app2,
                                   seq_group=self.seq_group_app2)
        # 缺失填充
        fill_col = list(set(self.self_feat_app2) - set(df2.columns))
        if fill_col:
            df2.loc[:, fill_col] = -999

        df = pd.concat([df1,df2],axis=1)

        return df

    # @log_run_time
    def self_feat(self,add_df:pd.DataFrame,app_df:pd.DataFrame):
        add_feat_df = self.__self_add_feat(add_df)
        app_feat_df = self.__self_app_feat(app_df)
        feat_df = pd.concat([add_feat_df,app_feat_df],axis=1)
        # 类型更改
        feat_df = feat_df.astype('float')
        # print(list(feat_df[self.self_feat_app2].to_dict(orient='index').values())[0])
        return feat_df
