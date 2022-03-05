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
