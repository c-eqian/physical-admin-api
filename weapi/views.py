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


class we_insert_apply_by_userId_view(APIView):
    """
    添加用户申请
    请求方式：GET
    参数：userId, apply_type
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId')
            apply_type = request.query_params.get('apply_type')
            res = db.we_insert_apply_by_userId(userId=userId, apply_type=apply_type)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_feeItemCode_list_view(APIView):
    """
    查询编码大类列表
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            res = db.select_feeItemCode_list()
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class weGetBasicDetailsView(APIView):
    """
    根据体检条码查询基本体检数据
    身高、体重、心率、体温
     1.请求方式：get
     2.参数：RequisitionId，FeeItemCode
     3.返回：
    """

    def get(self, request, *args, **kwargs):
        RequisitionId = request.query_params.get('RequisitionId', 0)
        res = db.we_queryBasicPhysicalExamRes(Rid=RequisitionId)
        return Response(res)


class weGetUrineTestItemDetailsView(APIView):
    """
    根据体检条码及编码大类查询尿检细项
     1.请求方式：post
     2.参数：RequisitionId，FeeItemCode
     3.返回：
    """

    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        FeeItemCode = request.data.get('FeeItemCode', 0)
        res = db.we_getUrineTestDetailsByRidAndFic(Rid=RequisitionId, Fic=FeeItemCode)
        return Response(res)


class weGetEcgDetailsView(APIView):
    """
    根据体检条码及编码大类查询心电图
     1.请求方式：post
     2.参数：RequisitionId，FeeItemCode
     3.返回：
    """

    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        FeeItemCode = request.data.get('FeeItemCode', 0)
        res = db.we_getEcgDetails(RequisitionId=RequisitionId, FeeItemCode=FeeItemCode)
        return Response(res)


class weGetAbdomenDetailsView(APIView):
    """
    根据体检条码及编码大类查询腹部超声
     1.请求方式：post
     2.参数：RequisitionId，FeeItemCode
     3.返回：
    """

    def post(self, request, *args, **kwargs):
        RequisitionId = request.data.get('RequisitionId', 0)
        FeeItemCode = request.data.get('FeeItemCode', 0)
        res = db.we_getAbdomenDetails(RequisitionId=RequisitionId, FeeItemCode=FeeItemCode)
        return Response(res)


class weGetUrineTestItemListView(APIView):
    """
     根据体检条码查询尿检项目类
     1.请求方式：get
     2.参数：RequisitionId
     3.返回：
     """

    def get(self, request, *args, **kwargs):
        RequisitionId = request.query_params.get('RequisitionId', 0)
        res = db.we_getUrineTestItemListByRequisitionId(RequisitionId=RequisitionId)
        return Response(res)


class weGetPhysicalExamListView(APIView):
    """
    获取体检列表
    1.请求方式：get
    2.参数：userId，[page=1,limit=50]
    3.返回：
    """

    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId')
        page = request.query_params.get('page')
        limit = request.query_params.get('limit')
        if page and userId and limit:
            res = db.we_getPhysicalExamListSql(userId=userId, page=int(page), limit=int(limit))
        elif page and userId:
            res = db.we_getPhysicalExamListSql(userId=userId, page=int(page))
        elif limit and userId:
            res = db.we_getPhysicalExamListSql(userId=userId, limit=int(limit))
        elif userId:
            res = db.we_getPhysicalExamListSql(userId=userId)
        else:
            res = errorRes(status=13207, msg='参数错误')
        print(res)
        return Response(res)


class weLoginView(APIView):
    """
    小程序用户登录
    1.请求方式：get
    2.参数：lg:{username:'',password:''}
    3.返回：
    """

    def get(self, request, *args, **kwargs):
        INFO = ast.literal_eval(sm4.decryptData_ECB(request.query_params.get('lg', 0)))
        return Response(db.we_LoginSql(u_name=INFO.get('username', 0), pwd=INFO.get('password', 0)))
