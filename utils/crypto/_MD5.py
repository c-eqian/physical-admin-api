# -*- coding: utf-8 -*-
# @Time    : 2021/7/18 20:40
# @Author  : 十三
# @Email   : 2429120006@qq.com
# @File    : _MD5.py
# @Software: PyCharm
import configparser

import json

from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
import base64
import os


class SM4Utils:
    def __init__(self, ):
        # cf = configparser.ConfigParser()
        # cf.read('../../config/config.ini')
        # 转bytes类型
        self.secret_key = bytes("JeF38U9wT9wldfdfdbbbfgs5255hhhhhMfp82", encoding='utf-8')

    # 加密方法
    def encryptData_ECB(self, plain_text: str):
        # 创建 SM4对象
        crypt_sm4 = CryptSM4()
        # 定义key值
        # self.secret_key = b"JeF38U9wT9wldfdfdbbbfgs5255hhhhhMfp82"
        # 设置key
        crypt_sm4.set_key(self.secret_key, SM4_ENCRYPT)

        # 调用加密方法加密(十六进制的bytes类型)
        encrypt_value = crypt_sm4.crypt_ecb(plain_text.encode())
        # 用base64.b64encode转码（编码后的bytes）
        cipher_text = base64.b64encode(encrypt_value)
        # 返回加密后的字符串
        return cipher_text.decode('utf-8', 'ignore')

    def decryptData_ECB(self, cipher_text):
        crypt_sm4 = CryptSM4()
        # secret_key = b"JeF38U9wT9wldfdfdbbbfgs5255hhhhhMfp82"
        # print(secret_key)
        crypt_sm4.set_key(self.secret_key, SM4_DECRYPT)
        # 将转入参数base64.b64decode解码成十六进制的bytes类型
        byt_cipher_text = base64.b64decode(cipher_text)
        # 调用加密方法解密，解密后为bytes类型
        decrypt_value = crypt_sm4.crypt_ecb(byt_cipher_text)
        return decrypt_value.decode('utf-8', 'ignore')

