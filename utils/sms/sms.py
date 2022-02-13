# -*- coding: utf-8 -*-
# @Time    : 2022-02-06 10:41
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : sms.py
# @Software: PyCharm
import ast
import json
import random

# from django.core.cache import cache
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models


# 生成6位随意验证码
def verification_code():
    code = random.randint(100000, 999999)
    return str(code)


def smsConfig(params: dict):
    try:
        cred = credential.Credential("AKIDPedLo1way5vUmoZ2EBrGOGyTheLlwsZ0",
                                     "C9rJVS9ZiaBWaNt99sMbbLp30g4B2cvx")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sms.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = sms_client.SmsClient(cred, "", clientProfile)
        phones = "+86" + params.get('phone')
        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": [phones],
            "TemplateID": params.get('TemplateID'),
            "SmsSdkAppid": params.get('appId'),
            "TemplateParamSet": [params.get('code'), params.get('timeout')]
            if params.get('timeout') else [params.get('code')],
            "Sign": params.get('Sign') if params.get('Sign') else "七七八八门禁小程序"
        }
        req.from_json_string(json.dumps(params))
        resp = client.SendSms(req)
        print(resp)
        return ast.literal_eval(resp.to_json_string())
        # 将验证码放在缓存中
        # cache.set(phone, code, 60 * 5)
    except TencentCloudSDKException as err:
        print(err)


def registerSms(phone) -> dict:
    """
    发送注册验证码
    @param phone: 手机号
    @return: 成功返回 code
    """
    _res = {}
    code = verification_code()
    params = {
        "phone": phone,
        "TemplateID": '1297192',
        "appId": '1400630089',
        "code": code,
        "timeout": "5",
        "Sign": "卿布小程序"
    }
    res = smsConfig(params=params)
    if res.get("SendStatusSet")[0].get("Code") == 'Ok':
        _res.update(status=200, code=code)
    else:
        _res.update(status=13203)
        # cache.set(phone, code, 60 * 5)
    # print(res)
    return _res

# registerSms("19994402296")
