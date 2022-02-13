from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.crypto import _MD5
from utils.Sql.execute_sql import executeDB

import ast

sm4 = _MD5.SM4Utils()  # 实例化sm4加密
db = executeDB()  # 实例化数据库

"""
登录验证
"""


class loginView(APIView):
    def post(self, request, *args, **kwargs):
        """
        :param request:post请求
        :param args:
        :param kwargs:
        :return:
        """
        INFO = ast.literal_eval(sm4.decryptData_ECB(request.data.get("lg")))

        return Response(db.LoginSql(u_name=INFO.get('username', 0), pwd=INFO.get('password', 0)))

    def get(self, request, *args, **kwargs):
        INFO = ast.literal_eval(sm4.decryptData_ECB(request.query_params.get('lg', 0)))
        return Response(db.LoginSql(u_name=INFO.get('username', 0), pwd=INFO.get('password', 0)))

    """
    根据条码及项目大类编码查询结果
    
    """


class getUltrasoundByFeeItemCode(APIView):
    def get(self, request, *args, **kwargs):
        ...

    def post(self, request, *args, **kwargs):
        ...

    """
    根据体检条码查询基本体检数据
    身高、体重、心率、体温
    """


class getBasicDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        personMark = request.data.get('personMark', 0)
        RequisitionId = request.data.get('RequisitionId', 0)
        res = db.queryBasicPhysicalExamRes(mark=personMark, Rid=RequisitionId)
        return Response(res)

    def get(self, request, *args, **kwargs):
        personMark = request.query_params.get('personMark', 0)
        RequisitionId = request.query_params.get('RequisitionId', 0)
        print(personMark, RequisitionId)
        res = db.queryBasicPhysicalExamRes(mark=personMark, Rid=RequisitionId)
        return Response(res)

    """
    根据体检条码及编码大类查询心电图
    """


class getEcgDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        FeeItemCode = request.data.get('FeeItemCode', 0)
        res = db.getEcgDetails(RequisitionId=RequisitionId, FeeItemCode=FeeItemCode)
        return Response(res)

    """
    根据体检条码及编码大类查询腹部超声
    """


class getAbdomenDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        FeeItemCode = request.data.get('FeeItemCode', 0)
        res = db.getAbdomenDetails(RequisitionId=RequisitionId, FeeItemCode=FeeItemCode)
        return Response(res)

    """
    根据体检条码及编码大类查询尿检细项
    """


class getUrineTestItemDetailsView(APIView):
    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        FeeItemCode = request.data.get('FeeItemCode', 0)
        res = db.getUrineTestDetailsByRidAndFic(Rid=RequisitionId, Fic=FeeItemCode)
        return Response(res)

    """
    根据个人序号获取体检条码查询尿检项目类
    """


class getUrineTestItemByRidListView(APIView):
    def post(self, request, *args, **kwargs):
        personMark = request.data.get('personMark', 0)
        res = db.getUrineTestItemListByRequisitionId(mark=personMark)
        return Response(res)

    def get(self, request, *args, **kwargs):
        personMark = request.query_params.get('personMark', 0)
        res = db.getUrineTestItemListByRequisitionId(mark=personMark)
        return Response(res)

    """
    根据体检条码查询尿检项目类
    """


class getUrineTestItemListView(APIView):
    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        res = db.getUrineTestItemListByRequisitionId(RequisitionId=RequisitionId)
        return Response(res)

    def get(self, request, *args, **kwargs):
        RequisitionId = request.query_params.get('RequisitionId', 0)
        res = db.getUrineTestItemListByRequisitionId(RequisitionId=RequisitionId)
        return Response(res)

    #     """
    #     根据体检条码查询基本体检详情
    #     """
    #
    #
    # class getBasicPhysicalDetailsView(APIView):
    #     def post(self, request, *args, **kwargs):
    #         RequisitionId = request.data.get('RequisitionId', 0)
    #         res = db.queryBasicPhysicalExamRes(Rid=RequisitionId)
    #         return Response(res)
    #
    #     def get(self, request, *args, **kwargs):
    #         RequisitionId = request.query_params.get('RequisitionId', 0)
    #         res = db.queryBasicPhysicalExamRes(Rid=RequisitionId)
    #         return Response(res)

    """
    开通账号
    """


class registerView(APIView):
    def post(self, request, *args, **kwargs):
        password = request.data.get('password', 0)
        name = request.data.get('name', 0)
        idCard = request.data.get('idCard', 0)
        res = db.RegisterSql(pwd=password, nick=name, idCard=idCard)
        return Response(res)

    """
    获取体检列表
    """


class getPhysicalExamListView(APIView):
    def post(self, request, *args, **kwargs):
        personMark = request.data.get('personMark', 0)
        page = request.data.get('page', 0)
        limitNum = request.data.get('limitNum', 0)
        res = db.getPhysicalExamListSql(personMark=personMark, page=int(page), limitNum=int(limitNum))
        return Response(res)

    def get(self, request, *args, **kwargs):
        personMark = request.query_params.get('personMark', 0)
        page = request.query_params.get('page', 0)
        limitNum = request.query_params.get('limitNum', 0)
        res = db.getPhysicalExamListSql(personMark=personMark, page=int(page), limitNum=int(limitNum))
        return Response(res)
