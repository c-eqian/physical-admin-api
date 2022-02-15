from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.crypto import _MD5
from utils.dbV3.db import database
import ast

sm4 = _MD5.SM4Utils()  # 实例化sm4加密
db = database()  # 实例化数据库


def errorRes(status=13203, msg='请求错误'):
    """
    返回请求错误
    """
    return {'status': status, 'msg': msg}


class loginView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            login = sm4.decryptData_ECB(request.query_params.get("login"))
            login = ast.literal_eval(login)
            account = login['name']
            password = login['password']
            return Response(db.login(userAccount=account, userPassword=password))
        except Exception as e:
            print(e)

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


class test(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.test())
