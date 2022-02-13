# -*- coding: utf-8 -*-
# @Time    : 2022-01-15 15:24
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : viewsV3.py
# @Software: PyCharm
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from utils.crypto import _MD5
from utils.dbV3.db import database
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import ast
import os
from utils.uploadImg.uploadImg import Storage
import random
import shutil
# from django_redis import get_redis_connection
from utils.redisCache.redisCache import Redis
from utils.sms.sms import registerSms

_redis = Redis()
sm4 = _MD5.SM4Utils()  # 实例化sm4加密
db = database()  # 实例化数据库


def regPhoneNum(phone: str):
    import re
    reg = '^(13[0-9]|14[01456879]|15[0-35-9]' \
          '|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$'
    pattern = re.compile(reg)
    return pattern.match(phone)


class test(APIView):
    def get(self, request, *args, **kwargs):
        try:
            data = request.query_params.get("test")
            # 获取redis的conn对象
            if data in [1, '1']:
                res = _redis.keys("520*")
                print(res)
                _res = _redis.deleteKeys('520*')
                res = _redis.keys("520*")
                print(res)
            elif data in [2, '2']:
                res = _redis.delete('520')
            return Response({"status": 200, 'msg': 1122})
        except Exception as e:
            print(e)
            return Response({"status": 500, 'msg': "失败"})


"""
发布留言
1.请求方式：POST
2.参数：userId,content
3.返回：
"""


class publishContentView(APIView):
    def post(self, request, *args, **kwargs):
        userId = request.data.get("userId")
        content = request.data.get("content")
        if userId and content:
            return Response(db.publishContent(userId=userId, content=content))
        return Response(errorRes(msg='参数错误'))

    def get(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
评论留言
1.请求方式：POST
2.参数：userId,contentId,commentText
3.返回：
"""


class addCommentView(APIView):
    def post(self, request, *args, **kwargs):
        userId = request.data.get("userId")
        contentId = request.data.get("contentId")
        commentText = request.data.get("commentText")
        if userId and contentId and commentText:
            return Response(db.addComment(userId=userId,
                                          contentId=int(contentId), commentText=commentText))
        return Response(errorRes(msg='参数错误'))

    def get(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
取消点赞
1.请求方式：get
2.参数：userId,contentId
3.返回：
"""


class cancelLikeView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            contentId = request.query_params.get("contentId")
            if userId and contentId:
                return Response(db.cancelLike(userId=userId, contentId=int(contentId)))
            return Response(errorRes(msg='参数错误'))
        except Exception as e:
            print(e)

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
点赞留言
1.请求方式：get
2.参数：userId,contentId
3.返回：
"""


class addLikeView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get("userId")
        contentId = request.query_params.get("contentId")
        if userId and contentId:
            return Response(db.addLike(userId=userId, contentId=int(contentId)))
        return Response(errorRes(msg='参数错误'))

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
获取留言内容
1.请求方式：get
2.参数：userId,page,limit
3.返回：
"""


class getContentView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            page = request.query_params.get("page", 1)
            limit = request.query_params.get("limit")
            data = _redis.get(key=str(userId) + '-' + str(page))  # 查询缓存数据，有直接返回，没有查询数据库
            if data:
                data = bytes.decode(data)
                return Response(ast.literal_eval(data))
            elif not page and not limit:
                return Response(db.getLeaveContent(userId=userId))
            elif not page:
                return Response(db.getLeaveContent(userId=userId, limit=limit))
            elif not limit:
                return Response(db.getLeaveContent(userId=userId, page=page))
            elif page and limit:
                return Response(db.getLeaveContent(userId=userId, page=page, limit=limit))
        except Exception as e:
            print(e)
            return Response(errorRes(msg='服务出错，请联系管理员'))

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
查询今日告警记录
1.请求方式：get
2.参数：无
3.返回：

"""


class todayPassWaringView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.todayWaringTotal())

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
查询今日访客记录
1.请求方式：get
2.参数：无
3.返回：

"""


class todayPassTotalView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.todayPassTotal())

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
是否开启短信验证
1.请求方式：get
2.参数：无
3.返回：

"""


class isSmsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.isSms())

    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
校验验证码
1.请求方式：get
2.参数：code,phoneNum
3.返回：

"""


class checkVerCodeView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            _res = {}
            phoneNum = request.query_params.get("phoneNum")
            code = request.query_params.get("code")
            # 校验手机号与验证码是否正确
            if str(code) == bytes.decode(_redis.get(str(phoneNum))):
                _res.update(status=200, msg="验证成功")

            else:
                _res.update(status=13204, msg="验证码错误")
            return Response(_res)
        except Exception as e:
            print(e)
            return Response({"status": 13203, 'msg': "验证失败"})


"""
注册验证码发送
1.请求方式：get
2.参数：phoneNum
3.返回：

"""


class sendVerCodeView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            _res = {}
            phoneNum = request.query_params.get("phoneNum")
            # 校验手机号是否正确
            if regPhoneNum(str(phoneNum)):
                sendSmsRes = registerSms(phone=phoneNum)
                if sendSmsRes.get('status') == 200:
                    _res.update(status=200, msg="发送成功")
                    _redis.set(str(phoneNum), value=sendSmsRes.get('code'))
                else:
                    _res.update(status=13203, msg="发送失败")
            else:
                _res.update(status=13204, msg="手机号格式不正确")
            return Response(_res)
        except Exception as e:
            return Response({"status": 13203, 'msg': "发送失败,服务器繁忙"})


"""
用户查询通行方式状态
1.请求方式：get
2.参数：userId
3.返回：

"""


class passStatusView(APIView):
    def post(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))

    def get(self, request, *args, **kwargs):

        try:
            userId = request.query_params.get('userId')
            if userId:
                return Response(
                    db.findPassWayByUserId(userId=userId))
            else:
                return Response(errorRes(status=13207, msg='参数错误'))
        except Exception as e:
            return Response(errorRes(msg=f'服务器出错:{e}'))


"""
用户找回密码
1.请求方式：POST
2.参数：userName, userAccount, newUserPassword
3.返回：

"""


class findPassWordView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            userName = request.data.get("userName")
            userAccount = request.data.get("userAccount")
            newUserPassword = request.data.get("newUserPassword")
            if userAccount and userName and newUserPassword:
                return Response(
                    db.findPassWord(userAccount=userAccount, userName=userName, newUserPassword=newUserPassword))
            else:
                return Response(errorRes(status=13207, msg='参数错误'))
        except Exception as e:
            return Response(errorRes(msg=f'服务器出错:{e}'))

    def get(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
新增用户
1.请求方式：POST
2.参数：userName, sex, age, contactNumber, [userAccount, userPassWord]
3.返回：

"""


class addUserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            userName = request.data.get("userName")
            sex = request.data.get("sex")
            birthday = request.data.get("birthday")
            contactNumber = request.data.get("contactNumber")
            userAccount = request.data.get("userAccount")
            userPassWord = request.data.get("userPassWord")
            if userName and sex and birthday and contactNumber:
                if str(contactNumber).isdigit():
                    if userPassWord and userAccount:
                        return Response(db.addUser(userName=userName, sex=sex, birthday=birthday,
                                                   contactNumber=int(contactNumber),
                                                   userAccount=userAccount, userPassWord=userPassWord))
                    return Response(
                        db.addUser(userName=userName, sex=sex, birthday=birthday, contactNumber=int(contactNumber)))
                else:
                    return Response(
                        errorRes(status=13207,
                                 msg=f"参数 contactNumber 必须是数字"))

            else:
                return Response(errorRes(status=13207, msg='参数错误'))
        except Exception as e:
            print(e)

    def get(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
修改登录密码
1.请求方式：get
2.参数：userId，newPassWord,oldPassWord
3.返回：修改信息
"""


class updateLoginPassWordView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            userId = request.data.get("userId")
            newPwd = request.data.get("newPassWord")
            oldPwd = request.data.get("oldPassWord")
            if userId and newPwd and oldPwd:
                return Response(db.updateLoginPassWord(userId=userId, newPassword=newPwd, oldPassword=oldPwd))
            else:
                return Response(errorRes(status=13207, msg="参数错误"))
        except Exception as e:
            print(e)

    def get(self, request, *args, **kwargs):
        return Response(errorRes(status=13208, msg='接口错误'))


"""
通过用户Id查询刷卡/刷脸/足迹记录
1.请求方式：get
2.参数：userId
3.返回：记录
"""


class passRecordView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            limit = request.query_params.get("limit")
            page = request.query_params.get("page")
            if not userId:
                return Response(errorRes(msg='参数错误', status=13207))
            if limit and page and str(page).isdigit() and str(limit).isdigit():
                return Response(db.passRecordByUserId(userId=userId, limit=int(limit), page=int(page)))
            elif not limit and not page:
                return Response(db.passRecordByUserId(userId=userId))
            elif not limit and page and str(page).isdigit():
                return Response(db.passRecordByUserId(userId=userId, page=int(page)))
            elif not page and limit and str(limit).isdigit():
                return Response(db.passRecordByUserId(userId=userId, limit=int(limit)))
            else:
                return Response(errorRes(msg='参数错误', status=13207))
        except Exception as e:
            return Response(errorRes(msg='参数错误', status=13207))


"""
用户注销登录
1.请求方式：get
2.参数：userId
3.返回：注销状态
"""


class logoutView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            userPassWord = request.query_params.get("userPassWord")
            if not userId or not userPassWord:
                return Response(errorRes(msg='参数错误', status=13207))
            return Response(db.logoutByUserId(userId=userId, userPassWord=userPassWord))
        except Exception as e:
            return Response(errorRes(msg='参数错误', status=13207))


"""
根据userId获取用户详细信息
1.请求方式：get
2.参数：userId
3.返回：用户信息
"""


class uploadAvatarView(APIView):
    @staticmethod
    def delete_user_photo(path):
        """
        删除用户目录图像
        @return:
        """
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
        except Exception as e:
            print(f"删除用户目录失败：{e}")

    def uploadImg(self, userPath, path, userId):
        """
        上传图片
        @param userId:
        @param userPath:
        @param path:
        @return:
        """
        store = Storage()
        _Res = {"status": 0, "msg": ''}  # 返回数据
        res = store.upload_one_img(str(userPath))
        if res.get("status") == 200 and res.get("url"):
            re = db.uploadAvatar(userId=userId, avatarUrl=res.get("url"))
            if re.get("status") == 200:
                _Res.update(status=200, avatarUrl=res.get("url"), msg="头像修改成功")
            else:
                _Res.update(status=re.get("status"), msg="头像修改失败")
            self.delete_user_photo(path=path)
        else:
            _Res.update(status=13203, msg="头像修改失败")
        return _Res

    def post(self, request, *args, **kwargs):
        try:
            userId = request.data.get("userId")
            IMAGE = request.FILES.get("image")
            if userId:
                path = os.path.abspath(f"imgPath/{str(userId)}")
            else:
                return Response(errorRes(msg='参数错误', status=13207))
            # if not os.path.exists(path):
            #     os.makedirs(path)
            childPath = f"{str(userId)}_{random.randint(0, 1000)}"
            default_storage.save(f"{path}/{childPath}.jpg", ContentFile(IMAGE.read()))
            userPath = path + "/" + childPath + ".jpg"
            res = self.uploadImg(userPath=userPath, path=path, userId=userId)
            return Response(res)
        except Exception as e:
            return Response(errorRes(msg='参数错误', status=13207))

    # def get(self, request, *args, **kwargs):
    #     try:
    #         userId = request.query_params
    #         print(userId)
    #         return Response(errorRes(msg='成功', status=200))
    #     except Exception as e:
    #         print(e)
    #         return Response(errorRes(msg='参数错误'))


"""
根据userId获取用户详细信息
1.请求方式：get
2.参数：userId
3.返回：用户信息
"""


class userDetailInfoView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            if not userId:
                return Response(errorRes(msg='参数错误', status=13207))
            return Response(db.userDetailInfo(userId=userId))
        except Exception as e:
            print(e)


"""
用户开通账号登录
1.请求方式：get
2.参数：options
3.返回：开通信息
"""


class registerView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            INFO = ast.literal_eval(sm4.decryptData_ECB(request.query_params.get("rg")))
            if not INFO:
                return Response(errorRes(msg='参数错误', status=13207))
            return Response(db.userRegister(userName=INFO.get('username', 0),
                                            loginAccount=INFO.get('account', 0),
                                            loginPwd=INFO.get('password', 0)))
        except Exception as e:
            print(e)


"""
用户登录
1.请求方式：GET
2.参数：lg
3.返回：用户信息
"""


class loginView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            INFO = ast.literal_eval(sm4.decryptData_ECB(request.query_params.get("lg")))
            if not INFO:
                return Response(errorRes(msg='参数错误', status=13207))
            return Response(db.userLogin(userAccount=INFO.get('username', 0), userPwd=INFO.get('password', 0)))
        except Exception as e:
            print(e)


"""
先根据用户ID查询，
如果数据库中已经存在，
就更新当前的人脸ID 
如果不存在该用户的ID，则就新增该数据
1.请求方式：GET
2.参数：userName、faceId
3.返回：
"""


class addFaceIdView(APIView):
    def get(self, request, *args, **kwargs):
        userName = request.query_params.get('userName', 0)
        faceId = request.query_params.get('faceId', 0)

        if not userName or not faceId:
            return Response(errorRes(msg='必须参数userName或faceId错误'))
        userId = db.getLastUserId()
        if userId == 13204:
            return Response(errorRes(msg='数据操作失败，请稍后再试', status=13205))
        return Response(db.insertUserByUserIdAndFaceId(userName=userName, userId=userId, faceId=faceId))


"""
先根据用户ID查询，
如果数据库中已经存在，
就更新当前的门卡ID 
如果不存在该用户的ID，则就新增该数据
1.请求方式：GET
2.参数：userName、idCard
3.返回：
"""


class addIdCardView(APIView):
    def get(self, request, *args, **kwargs):
        userName = request.query_params.get('userName', 0)
        idCard = request.query_params.get('idCard', 0)
        if not userName or not idCard:
            return Response(errorRes(msg='必须参数userName或idCard错误'))
        userId = db.getLastUserId()
        if userId == 13204:
            return Response(errorRes(msg='数据操作失败，请稍后再试', status=13205))
        return Response(db.insertOrUpdateIdCardByUserName(userName=userName, userId=userId, idCard=idCard))


"""
查询登记的用户数据
1.请求方式：GET
2.参数：page、limit
3.返回：
"""


class userListView(APIView):
    def get(self, request, *args, **kwargs):
        page = request.query_params.get('page', 0)
        limit = request.query_params.get('limit', 0)
        if int(page) < 1:
            return Response(errorRes(msg='必须参数page错误,或page须大于等于1'))
        if limit == 0:
            return Response(db.selectUserList(page=int(page)))
        else:
            return Response(db.selectUserList(page=int(page), limit=int(limit)))


"""
查询用户总数
1.请求方式：GET
2.参数：
3.返回：
"""


class userTotalView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.getUserCount())


"""
通过用户名或者用户ID关键字查询
1.请求方式：GET
2.参数：content
3.返回：
"""


class searchUserView(APIView):
    def get(self, request, *args, **kwargs):
        content = request.query_params.get('content', 0)
        if not content:
            return Response(errorRes(msg='参数content错误'))
        return Response(db.selectByUserNameOrUserId(content=content))


"""
通过用户id禁用刷卡
1.请求方式：GET
2.参数：userId
3.返回：
"""


class disableIdCardView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.disableIdCardByUserId(userId=userId))


"""
通过用户id禁用刷脸
1.请求方式：GET
2.参数：userId
3.返回：
"""


class disableFaceView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.disableFaceByUserId(userId=userId))


"""
通过用户禁用
1.请求方式：GET
2.参数：userId
3.返回：
"""


class disableUserView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.disableStatusByUserId(userId=userId))


"""
通过用户id启用刷卡
1.请求方式：GET
2.参数：userId
3.返回：
"""


class enableIdCardView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.enableIdCardByUserId(userId=userId))


"""
通过用户id启用刷脸
1.请求方式：GET
2.参数：userId
3.返回：
"""


class enableFaceView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.enableFaceByUserId(userId=userId))


"""
通过用户id启用
1.请求方式：GET
2.参数：userId
3.返回：
"""


class enableUserView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.enableStatusByUserId(userId=userId))


"""
验证用户是否存在
1.请求方式：GET
2.参数：userName
3.返回：
"""


class verifyUserView(APIView):
    def get(self, request, *args, **kwargs):
        userName = request.query_params.get('userName', 0)
        if not userName:
            return Response(errorRes(msg='参数userName错误'))
        return Response(db.selectByUserName(userName=userName))


"""
删除用户
1.请求方式：GET
2.参数：userId
3.返回：
"""


class deleteUserView(APIView):
    def get(self, request, *args, **kwargs):
        userId = request.query_params.get('userId', 0)
        if not userId:
            return Response(errorRes(msg='参数userId错误'))
        return Response(db.deleteUserByUserId(userId=userId))


"""
关键字或精确搜索访客用户
1.请求方式：GET
2.参数：content
3.返回：搜索访客记录
"""


class passUserSearchView(APIView):
    def get(self, request, *args, **kwargs):
        content = request.query_params.get('content', 0)
        if not content:
            return Response(errorRes(msg='参数content错误'))
        return Response(db.selectPassContent(content=content))


"""
获取访客记录
1.请求方式：GET
2.参数：page
3.返回：访客记录
"""


class passUserListView(APIView):
    def get(self, request, *args, **kwargs):
        page = request.query_params.get('page', 0)
        limit = request.query_params.get('limit', 0)

        if int(page) < 1 or not str(page).isdigit():
            return Response(errorRes(msg='参数page错误'))
        if limit == 0:
            return Response(db.selectPassUserList(page=int(page)))
        else:
            return Response(db.selectPassUserList(page=int(page), limit=int(limit)))


"""
获取出入总数
1.请求方式：GET
2.参数：无
3.返回：访客总人数
"""


class passUserTotalView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.selectPassUserTotal())


"""
faceId校验用户户名，人脸识别使用
1.请求方式：GET
2.参数：faceId
3.返回：用户名
"""


class verifyFaceIdlView(APIView):
    def get(self, request, *args, **kwargs):
        faceId = request.query_params.get('faceId', 0)
        return Response(db.selectByFaceId(faceId=faceId))


def errorRes(status=13203, msg='请求错误'):
    """
    返回请求错误
    """
    return {'status': status, 'msg': msg}
