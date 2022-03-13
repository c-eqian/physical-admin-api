from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.crypto import _MD5
from utils.dbV3.db import database
import ast
from utils.log.log import Logger
from utils.redisCache.redisCache import Redis

_redis = Redis()
sm4 = _MD5.SM4Utils()  # 实例化sm4加密
db = database()  # 实例化数据库
log = Logger()


def errorRes(status=13203, msg='请求错误'):
    """
    返回请求错误
    """
    return {'status': status, 'msg': msg}


class select_person_physical_list_by_RequisitionId_view(APIView):
    """
    根据当次体检编码查询当前用户需要体检的项目
    请求方式：GET
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get("RequisitionId")
            res = db.select_person_physical_list_by_RequisitionId(RequisitionId=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class update_apply_by_id_view(APIView):
    """
    更新用户的申请状态
    请求方式：GET
    参数：Id,apply_status,apply_reason,operator_id
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            Id = request.query_params.get("Id")
            apply_status = request.query_params.get("apply_status")
            apply_reason = request.query_params.get("apply_reason")
            operator_id = request.query_params.get("operator_id")
            res = db.update_apply_by_id(Id=int(Id), apply_status=int(apply_status),
                                        apply_reason=apply_reason if apply_reason else None,
                                        operator_id=operator_id)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_itemCode_list_by_feeItemCode_view(APIView):
    """
    根据大类编码查询细项编码列表
    请求方式：GET
    参数：feeItemCode
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            feeItemCode = request.query_params.get("feeItemCode")
            res = db.select_itemCode_list_by_feeItemCode(feeItemCode=feeItemCode)
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


class query_apply_by_text_view(APIView):
    """
    搜索。支持姓名，机构名称，身份证
    请求方式：GET
    参数：searchText, [page=1, limit=50]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            cache_data = _redis.get(key=f"searchApply{searchText}{page if page else 1}{limit if limit else 50}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and searchText and limit:
                res = db.query_apply_by_text(searchText=searchText, page=int(page), limit=int(limit))
            elif page and searchText:
                res = db.query_apply_by_text(searchText=searchText, page=int(page))
            elif limit and searchText:
                res = db.query_apply_by_text(searchText=searchText, limit=int(limit))
            elif searchText:
                res = db.query_apply_by_text(searchText=searchText)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_apply_by_org_code_view(APIView):
    """
    通过机代码查询用户申请列表
    请求方式：GET
    参数：org_code, [page=1, limit=50]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            cache_data = _redis.get(key=f"apply{org_code}{page if page else 1}{limit if limit else 50}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and org_code and limit:
                res = db.select_apply_by_org_code(org_code=org_code, page=int(page), limit=int(limit))
            elif page and org_code:
                res = db.select_apply_by_org_code(org_code=org_code, page=int(page))
            elif limit and org_code:
                res = db.select_apply_by_org_code(org_code=org_code, limit=int(limit))
            elif org_code:
                res = db.select_apply_by_org_code(org_code=org_code)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class like_search_suggestion_view(APIView):
    """
    搜索建议，返回前10条
    请求方式：GET
    参数：KeyWords
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            keyWords = request.query_params.get("keyWords")
            return Response(db.likeSearchSuggestion(keyWords=keyWords))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class likeSearchView(APIView):
    """
    模糊查询
    请求方式：GET
    参数：searchText，[page=1,limit=50]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            cache_data = _redis.get(key=f"{searchText}{page if page else 1}{limit if limit else 50}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and searchText and limit:
                res = db.likeSearch(searchText=searchText, page=int(page), limit=int(limit))
            elif page and searchText:
                res = db.likeSearch(searchText=searchText, page=int(page))
            elif limit and searchText:
                res = db.likeSearch(searchText=searchText, limit=int(limit))
            elif searchText:
                res = db.likeSearch(searchText=searchText)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class likeSearchTotalView(APIView):
    """
    模糊查询总数
    请求方式：GET
    参数：searchText
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            return Response(db.likeSearchTotal(searchText=searchText))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class userDetailsView(APIView):
    """
    查询用户信息
    请求方式：GET
    参数：userId
    返回：用户总数
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            cache_data = _redis.get(key=f"{userId}")
            if cache_data:
                cache_data = bytes.decode(cache_data)
                return Response(ast.literal_eval(cache_data))
            return Response(db.userDetailsByUserId(userId=userId))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)


class userTotalView(APIView):
    """
    查询机构下用户数
    请求方式：GET
    参数：org_code
    返回：用户总数
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            return Response(db.userTotal(org_id=org_code))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)


class getUserListView(APIView):
    """
    医生登录获取该机构的用户列表
    请求方式：GET
    参数：org_code
    返回：登陆人信息
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            if page and limit and org_code:
                cache_data = _redis.get(key=f"{org_code}{page}{limit}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code, page=page, limit=limit))
            elif page and org_code:
                cache_data = _redis.get(key=f"{org_code}{page}{50}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code, page=page))
            elif limit and org_code:
                cache_data = _redis.get(key=f"{org_code}{1}{limit}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code, limit=limit))
            elif org_code:
                cache_data = _redis.get(key=f"{org_code}{1}{50}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code))
            else:
                return Response(errorRes(status=13207, msg='参数错误'))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)
    #
    # def post(self, request, *args, **kwargs):
    #     return Response(errorRes(status=13208, msg='接口错误'))


class loginView(APIView):
    """
    用户登录
    请求方式：GET
    参数：
    返回：登陆人信息
    """

    def get(self, request, *args, **kwargs):
        try:
            login = sm4.decryptData_ECB(request.query_params.get("login"))
            login = ast.literal_eval(login)
            account = login['name']
            password = login['password']
            return Response(db.login(userAccount=account, userPassword=password))
        except Exception as e:
            print(e)
    #
    # def post(self, request, *args, **kwargs):
    #     return Response(errorRes(status=13208, msg='接口错误'))


class test(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.test())
