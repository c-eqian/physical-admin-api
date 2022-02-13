# -*- coding: utf-8 -*-
# @Time    : 2022-01-15 15:28
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : urlsV3.py
# @Software: PyCharm
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
# from rest_framework.documentation import include_docs_urls

from api import viewsV3

urlpatterns = [
    url(r'^publishContent', viewsV3.publishContentView.as_view()),  # 发布留言
    url(r'^cancelLike', viewsV3.cancelLikeView.as_view()),  # 取消点赞
    url(r'^addLike', viewsV3.addLikeView.as_view()),  # 点赞留言
    url(r'^addComment', viewsV3.addCommentView.as_view()),  # 评论留言
    url(r'^getContent', viewsV3.getContentView.as_view()),  # 获取留言
    url(r'^todayPassTotal', viewsV3.todayPassTotalView.as_view()),  # 今日通行人数
    url(r'^todayPassWaring', viewsV3.todayPassWaringView.as_view()),  # 今日警告数
    url(r'^isSms', viewsV3.isSmsView.as_view()),  # 新增用户验证码
    url(r'^checkVerCode', viewsV3.checkVerCodeView.as_view()),  # 新增用户验证码
    url(r'^sendVerCode', viewsV3.sendVerCodeView.as_view()),  # 新增用户验证码
    url(r'^test', viewsV3.test.as_view()),  # 找回密码
    url(r'^passStatus', viewsV3.passStatusView.as_view()),  # 找回密码
    url(r'^findPassWord', viewsV3.findPassWordView.as_view()),  # 找回密码
    url(r'^addUser', viewsV3.addUserView.as_view()),  # 添加用户
    url(r'^updatePassword', viewsV3.updateLoginPassWordView.as_view()),  # 修改密码
    url(r'^passRecord', viewsV3.passRecordView.as_view()),  # 个人用户通行记录
    url(r'^logout', viewsV3.logoutView.as_view()),  # 用户注销
    url(r'^uploadAvatar', viewsV3.uploadAvatarView.as_view()),  # 用户上传头像
    url(r'^userDetailInfo', viewsV3.userDetailInfoView.as_view()),  # 用户详细信息
    url(r'^register', viewsV3.registerView.as_view()),  # 用户开通登录
    url(r'^login', viewsV3.loginView.as_view()),  # 用户登录
    url(r'^verifyFaceId', viewsV3.verifyFaceIdlView.as_view()),  # 根据faceId校验用户名
    url(r'^passUserTotal', viewsV3.passUserTotalView.as_view()),  # 获取访客总数
    url(r'^passUserList', viewsV3.passUserListView.as_view()),  # 查询访客记录
    url(r'^passUserSearch', viewsV3.passUserSearchView.as_view()),  # 搜索访客
    url(r'^deleteUser', viewsV3.deleteUserView.as_view()),  # 删除用户
    url(r'^verifyUser', viewsV3.verifyUserView.as_view()),  # 验证用户是否存在
    url(r'^enableUser', viewsV3.enableUserView.as_view()),  # 通过用户id启用
    url(r'^enableFace', viewsV3.enableFaceView.as_view()),  # 通过用户id启用刷脸
    url(r'^enableIdCard', viewsV3.enableIdCardView.as_view()),  # 通过用户id启用刷卡
    url(r'^disableUser', viewsV3.disableUserView.as_view()),  # 通过用户禁用
    url(r'^disableFace', viewsV3.disableFaceView.as_view()),  # 通过用户id禁用刷脸
    url(r'^disableIdCard', viewsV3.disableIdCardView.as_view()),  # 通过用户id禁用刷卡
    url(r'^searchUser', viewsV3.searchUserView.as_view()),  # 通过用户名或者用户ID关键字查询
    url(r'^userTotal', viewsV3.userTotalView.as_view()),  # 查询用户总数
    url(r'^userList', viewsV3.userListView.as_view()),  # 查询登记的用户数据
    url(r'^addIdCard', viewsV3.addIdCardView.as_view()),  # 1.先根据用户ID查询，如果数据库中已经存在，就更新当前的门卡ID 2.如果不存在该用户的ID，则就新增该数据
    url(r'^addFaceId', viewsV3.addFaceIdView.as_view()),  # 1.先根据用户ID查询，如果数据库中已经存在，就更新当前的人脸ID 2.如果不存在该用户的ID，则就新增该数据
    # url(r'docs/', include_docs_urls(title='接口文档'))
]
