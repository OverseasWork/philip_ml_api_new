# -*- coding: utf-8 -*-
# @Time    : 2022/5/14 16:06
# @Author  : HuangSir
# @FileName: tf_vec.py
# @Software: PyCharm
# @Desc:

import sys

sys.path.append('..')

import warnings

warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

from utils.load_utils import load_data
from utils.decorator import log_run_time
from conf.log_config import log

class TF2Vec:
    def __init__(self):
        super(TF2Vec, self).__init__()
        self.path_data = 'app/app/v1/data/'
        self.app_tf_base = load_data(f'{self.path_data}APP_TF_IDF_BASE.csv')
        self.app2vec = load_data(f'{self.path_data}app2vec.pkl')

    def __pre(self, app_df: pd.DataFrame):
        # 去除空格
        app_df['app_name'] = app_df['app_name'].apply(lambda x: x.replace(' ', ''))
        # 根据安装日期排序,从早到晚
        app_df = app_df.sort_values(by=['BUSI_ID', 'installAPP_tday'], ignore_index=True, ascending=False)
        return app_df

    def __tf_idf_feat(self, app_df: pd.DataFrame):
        # app_df = self.__pre(app_df)
        app_tf_df = pd.merge(app_df, self.app_tf_base, on='app_name')
        app_tf_df = pd.DataFrame(
            {k: [round(v, 2)] for k, v in app_tf_df.groupby('variable').tf_idf.sum().to_dict().items()}
        )
        fill_col = list(set(self.app_tf_base.variable) - set(app_tf_df.columns))
        if fill_col:
            app_tf_df.loc[:,fill_col] = -999
        return app_tf_df

    def __app2vec_feat(self, app_df: pd.DataFrame):
        # app_df = self.__pre(app_df)
        # 创建预测语料
        app_df['name_install_tday'] = app_df.apply(lambda row: [row['app_name'], str(row['installAPP_tday'])], axis=1)
        appNameSentencesDtest = app_df.groupby('BUSI_ID').name_install_tday.apply(self.__sent_ele).to_dict()
        sentences = list(appNameSentencesDtest.values())[0]
        df = self.__app2vec_transform(sentences)
        return df

    @log_run_time
    def tf2vec_feat(self, app_df: pd.DataFrame):
        app_df = self.__pre(app_df)
        app_tf_df = self.__tf_idf_feat(app_df)
        # print(app_tf_df.to_dict(orient='index')[0])
        w2vec_app_df = self.__app2vec_feat(app_df)
        # print(w2vec_app_df.to_dict(orient='index')[0])
        tf2vec_df = pd.concat([app_tf_df, w2vec_app_df], axis=1)
        return tf2vec_df

    def __app2vec_transform(self, sentences: list):
        """
        词向量特征提取
        :param app_name_sentences: list
        :param app2vec: 训练好的pkl模型
        :param size int 词向量长度
        :return: array,提取词向量
        """
        vector_list_temp = [self.app2vec.wv[k] for k in sentences if k in self.app2vec.wv]
        if not vector_list_temp:  # 遇到新文档,无一个词是在词向量模型中
            vector_list_temp = [np.zeros(self.app2vec.vector_size)]
            log.logger.warning(f'input new sentences')

        cutWord_vector = np.array(vector_list_temp).mean(axis=0)
        app2vec = {'app2vec_' + str(k): [v] for k, v in zip(range(self.app2vec.vector_size), cutWord_vector)}
        df = pd.DataFrame(app2vec)
        return df

    def __sent_ele(self, series):
        ls = []
        for i in series:
            ls.append(i[0])
            ls.append(i[1])
        return ls
