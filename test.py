# -*- coding: utf-8 -*-
# @Time    : 2022-02-06 13:19
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : test.py
# @Software: PyCharm
import django
from django.core.cache import cache
django.setup()
cache.set("1", 22, 30)
a = cache.get('1')
print(a)
