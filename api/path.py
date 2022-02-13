# -*- coding: utf-8 -*-
# @Time    : 2022-01-15 15:35
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : path.py
# @Software: PyCharm
# MODE 路径模式 =1 相对路径 =0 绝对路径
import os

MODE = 0
# 数据库配置文件路径
DB_CONFIG_PATH = "./config/config.ini" if MODE == 0 else os.path.abspath("/config/config.ini")
