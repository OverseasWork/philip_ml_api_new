# -*- coding: utf-8 -*-
# @Time    : 2022/5/14 16:53
# @Author  : HuangSir
# @FileName: lgb_predict.py
# @Software: PyCharm
# @Desc: 模型预测

import sys
sys.path.append('..')

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from datetime import datetime

from conf.log_config import log
from utils.load_utils import load_data
from utils.ml_utils import prob2score

from .pre import BaseInfoPre,AddPre,AppPre
from .self_feat import SelfFeat
from .dfs_feat import DFSFeat
from .tf_vec import TF2Vec

class LgbModel(BaseInfoPre,AddPre,AppPre,SelfFeat,DFSFeat,TF2Vec):
    def __init__(self):
        super(LgbModel, self).__init__()
        # self.path_data = 'app/app/ v1/data/'
        self.tf_w2vec_Model = load_data(f'{self.path_data }tf_w2vec_lgb.pkl')
        self.tf_w2vec_ml_feat = load_data(f'{self.path_data}tf_w2vec_lgb_feat.txt')

        self.newModel = load_data(f'{self.path_data }newModel.pkl')
        self.MlFeat = load_data(f'{self.path_data }feat.txt')

    def tf2vec_predict(self,tf2vec_df:pd.DataFrame):
        df = tf2vec_df[self.tf_w2vec_ml_feat]
        tf_w2vec_prob = np.nanmean([m.predict(df) for m in self.tf_w2vec_Model],axis=0)
        return tf_w2vec_prob

    def new_model_predict(self,df:pd.DataFrame):
        df = df[self.MlFeat]
        prob = np.nanmean([m.predict(df) for m in self.newModel],axis=0)
        prob = round(float(prob),5)

        score = prob2score(prob,basePoint=600,PDO=50,odds=1)
        score = int(float(score))

        return prob,score

    def predict(self,data:dict):
        '''模型预测'''
        busi_id = data['busi_id']
        apply_date = data['apply_date']

        base_info = data['base_info']
        appList = data['app_list']
        addBook = data['add_book']

        t0 = datetime.now()

        # --------------------------------------------------
        # base info 预处理
        base_info = self.base_info_pre(base_info=base_info)
        base_info_df = pd.DataFrame({k:[v] for k,v in base_info.items()})
        # print(base_info_df)
        base_info_df['BUSI_ID'] = busi_id

        # 通讯录 预处理
        add_df = self.add_pre(addBook=addBook,apply_date=apply_date)
        add_df['BUSI_ID'] = busi_id

        # appList 预处理
        app_df = self.app_pre(appList=appList,apply_date=apply_date)
        app_df['BUSI_ID']  = busi_id
        # --------------------------------------------------
        # 人工特征衍生
        self_feat_df = self.self_feat(add_df=add_df,app_df=app_df)

        # dfs特征衍生
        dfs_feat_df  = self.dfs_feat(add_df=add_df,app_df=app_df,base_df=base_info_df)

        # tf-idf,app2vec 特征衍生
        tf2vec_df = self.tf2vec_feat(app_df=app_df)

        # tf-idf+app2vec 子模型
        tf_w2vec_prob = self.tf2vec_predict(tf2vec_df=tf2vec_df)
        # print(busi_id,tf_w2vec_prob)
        # 入模变量
        dt_df = pd.concat([base_info_df,self_feat_df,dfs_feat_df],axis=1)
        dt_df['tf_w2vec_prob'] = tf_w2vec_prob

        # 模型预测
        prob,score = self.new_model_predict(df=dt_df)
        # print(busi_id,score)
        res = {'busi_id': busi_id,'prob':prob,'score':score, 'start': str(t0),'end':str(datetime.now())}
        return res




