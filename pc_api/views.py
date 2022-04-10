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


class apply_by_userId_view(APIView):
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


class query_user_details_by_idCard_view(APIView):
    """
       通过身份证查询用户基本信息与体检项目类型
    请求方式：get
    参数：idCard,org_code
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            idCard = request.query_params.get('idCard')
            org_code = request.query_params.get('org_code')
            res = db.query_user_details_by_idCard(idCard=idCard,org_code=org_code)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class exam_result_audit_by_rid_view(APIView):
    """
   医生审核体检结果
    请求方式：get
    参数：RequisitionId, status: 0-未审核，1-已审核，-1-不通过，[remark: 不通过原因]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            remark = request.query_params.get('remark')
            status = request.query_params.get('status')
            res = db.exam_result_audit_by_rid(rid=RequisitionId, status=status, remark=remark)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_feeItemCode_list_view(APIView):
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


class query_exam_base_and_urine_by_rid_view(APIView):
    """
   通过体检编码查询体检结果
    请求方式：get
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            res = db.query_exam_base_and_urine_by_rid(rid=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class check_exam_type_btn_by_rid_view(APIView):
    """
   根据体检编码校验是否前端可以生成数据，要与选择体检的项目一致
    请求方式：get
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            res = db.check_exam_type_btn_by_rid(rid=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class insert_exam_urine_by_rid_view(APIView):
    """
    根据体检编码新增尿检结果
    请求方式：get
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            data = ast.literal_eval(request.query_params.get('data'))
            res = db.insert_exam_urine_by_rid(rid=RequisitionId, params=data.get('data'))
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_exam_base_by_rid_view(APIView):
    """
    通过体检编码查询基本体检结果
    请求方式：GET
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get("RequisitionId")
            res = db.query_exam_base_by_rid(rid=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_exam_upload_by_org_code_view(APIView):
    """
    搜根据机构编码查询体检上传
    请求方式：GET
    参数：org_code, [page=1, limit=20]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            if page and org_code and limit:
                res = db.query_exam_upload_by_org_code(org_code=org_code, page=int(page), limit=int(limit))
            elif page and org_code:
                res = db.query_exam_upload_by_org_code(org_code=org_code, page=int(page))
            elif limit and org_code:
                res = db.query_exam_upload_by_org_code(org_code=org_code, limit=int(limit))
            elif org_code:
                res = db.query_exam_upload_by_org_code(org_code=org_code)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_cache_base_exam(APIView):
    """
    获取缓存中的体检数据
    请求方式：GET
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            _res = db.query_user_info_by_rid(rid=RequisitionId)
            cache_data = _redis.get(key=RequisitionId)
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
                if _res.get('status') == 200:
                    result = _res.get('result')
                    res.update(result)
                data = {'status': 200, 'msg': '获取成功', 'result': res}
            else:
                data = {'status': 13204, 'msg': '无数据'}
            return Response(data)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class cache_base_exam(APIView):
    """
    新增基本体检结果
    请求方式：POST
    参数：RequisitionId,Height,Weight,BMI,Temperature,heart_rate
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            data = {}
            RequisitionId = request.data.get('RequisitionId')
            Height = request.data.get('Height')
            Weight = request.data.get('Weight')
            BMI = request.data.get('BMI')
            Temperature = request.data.get('Temperature')
            heart_rate = request.data.get('heart_rate')
            data.update(RequisitionId=RequisitionId, Height=Height, Weight=Weight, BMI=BMI,
                        Temperature=Temperature, heart_rate=heart_rate)
            key = f'{RequisitionId}'
            _redis.set(key=key, value=str(data), timeout=60 * 60 * 24 * 30)
            return Response(errorRes(msg='保存成功', status=200))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class insert_base_exam(APIView):
    """
    新增基本体检结果
    请求方式：POST
    参数：base_data:{RequisitionId, userId, org_code,
         ProjectNo,ProjectName, RSBP, RDBP,Height,
                    Weight, BMI, Temperature, Operator, VisitingDate,
                    Status,
                    LSBP, LDBP, heart_rate}
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            print(222, request.data)
            RequisitionId = request.data.get('RequisitionId')
            userId = request.data.get('userId')
            org_code = request.data.get('org_code')
            Weight = request.data.get('Weight')
            Height = request.data.get('Height')
            BMI = request.data.get('BMI')
            LSBP = request.data.get('LSBP')
            LDBP = request.data.get('LDBP')
            heart_rate = request.data.get('heart_rate')
            Temperature = request.data.get('Temperature')
            VisitingDate = request.data.get('VisitingDate')
            Operator = request.data.get('Operator')
            params.update(RequisitionId=RequisitionId, userId=userId, org_code=org_code,
                          Weight=Weight, Height=Height, BMI=BMI, LSBP=LSBP, LDBP=LDBP,
                          heart_rate=heart_rate, Temperature=Temperature, VisitingDate=VisitingDate,
                          Operator=Operator
                          )
            res = db.insert_base_exam(params=params)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_person_physical_list_by_RequisitionId_view(APIView):
    """
    根据当次体检编码查询当前用户需要体检的项目大类
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
    参数：org_code, [page=1, limit=50，timestamp-时间戳，添加时可以解决缓存问题]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            timestamp = request.query_params.get("timestamp")
            limit = request.query_params.get("limit")
            if timestamp:
                key = f"apply{org_code}{page if page else 1}{limit if limit else 50}{timestamp}"
            else:
                key = f"apply{org_code}{page if page else 1}{limit if limit else 50}"
            cache_data = _redis.get(key=key)
            print(cache_data)
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


class user_details_by_idCard_view(APIView):
    """
    通过身份证查询用户详情
    请求方式：GET
    参数：idCard
    返回：用户总数
    """

    def get(self, request, *args, **kwargs):
        try:
            idCard = request.query_params.get("idCard")
            cache_data = _redis.get(key=f"{idCard}")
            if cache_data:
                cache_data = bytes.decode(cache_data)
                return Response(ast.literal_eval(cache_data))
            return Response(db.user_details_by_idCard(idCard=idCard))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)


class userDetailsView(APIView):
    """
    通过用户ID查询用户详情
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
