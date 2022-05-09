# -*- coding: utf-8 -*-
# @Time    : 2022-05-08 11:49
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : mqtt.py
# @Software: PyCharm
# 为了能在外部脚本中调用Django ORM模型，必须配置脚本环境变量，将脚本注册到Django的环境变量中
import ast
import os

import django

# 第一个参数固定，第二个参数是工程名称.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AppletInterface.settings')
django.setup()

# 引入mqtt包
import paho.mqtt.client as mqtt
# 使用独立线程运行
from threading import Thread
from utils.redisCache.redisCache import Redis
import json

_redis = Redis()

import time


class Mqtt:
    client = mqtt.Client(client_id=f"test{time.time()}", clean_session=False, transport='tcp')

    # 建立mqtt连接
    def on_connect(self, client, userdata, flag, rc):
        """
        @param client: 客户端
        @param userdata:
        @param flag:
        @param rc:
        @return:
        """
        print("Connect with the result code " + str(rc))
        self.client.subscribe('toServer', qos=0)

    # 接收、处理mqtt消息
    def on_message(self, client, userdata, msg):
        """
        @param client: 客户端
        @param userdata: 数据
        @param msg: 信息
        @return:
        """
        out = str(msg.payload.decode('utf-8'))
        print(msg.topic)
        data = json.loads(out)
        if msg.topic == "toServer":
            _id = data.get('id')
            if _id:
                # 获取缓存数据
                cache_data = _redis.get(key=_id)
                if cache_data:  # 有缓存，更新
                    new_data = {}
                    cache_data = bytes.decode(cache_data)
                    res = ast.literal_eval(cache_data)
                    height = res.get('Height', 0)
                    HR = res.get('heart_rate', 0)
                    Spo2 = res.get('Spo2', 0)
                    temperature = res.get('Temperature', 0)
                    weight = res.get('Weight', 0)
                    _data = data.get('params', 0)
                    if _data:
                        height = height if _data.get('height') <= 0.0 else _data.get('height')
                        HR = height if _data.get('HR') <= 0.0 else _data.get('HR')
                        Spo2 = height if _data.get('Spo2') == 0.0 else _data.get('Spo2')
                        temperature = height if _data.get('temperature') <= 0.0 else _data.get('temperature')
                    new_data.update(RequisitionId=_id, Height=height, Weight=weight,
                                    Temperature=temperature, heart_rate=HR,Spo2=Spo2)
                    # new_data.update(height=height, HR=HR, Spo2=Spo2, temperature=temperature, weight=weight)
                    _redis.set(_id, str(new_data), timeout=60 * 10)
                else:
                    _redis.set(data.get('id'), str(data.get('params', 0)), timeout=60 * 10)

        # 收到消息后执行任务

    # mqtt客户端启动函数
    def mqtt_run(self):
        # 使用loop_start 可以避免阻塞Django进程，使用loop_forever()可能会阻塞系统进程
        # client.loop_start()
        # client.loop_forever() 有掉线重连功能
        self.client.loop_forever(retry_first_connection=True)

    # 启动函数
    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # 绑定 MQTT 服务器地址
        broker = '43.138.188.22'
        # MQTT服务器的端口号
        self.client.connect(broker, 1883, 62)
        self.client.username_pw_set('user', 'user')
        self.client.reconnect_delay_set(min_delay=1, max_delay=2000)
        # 启动
        mqtt_thread = Thread(target=self.mqtt_run)
        mqtt_thread.start()

# 启动 MQTT
# mqtt_run()


# if __name__ == "__main__":
#     run()
