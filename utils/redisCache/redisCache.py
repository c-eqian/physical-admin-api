# -*- coding: utf-8 -*-
# @Time    : 2022-02-06 19:08
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : redisCache.py
# @Software: PyCharm

from django_redis import get_redis_connection


class Redis:
    def __init__(self):
        try:
            self.conn = get_redis_connection('default')
        except Exception as e:
            print(e)

    def deleteKeys(self, key):
        keys = self.keys(key=key)
        self.conn.delete(*keys)

    def keys(self, key):
        return self.conn.keys(key)

    def get(self, key):
        data = self.conn.get(key)
        return data

    def set(self, key, value, timeout=60 * 5) -> bool:
        set_status = self.conn.set(key, value, timeout)
        return set_status

    def delete(self, key):
        self.conn.delete(key)
