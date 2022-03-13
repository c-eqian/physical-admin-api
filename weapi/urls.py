# -*- coding: utf-8 -*-
# @Time    : 2022-02-27 10:58
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : urls.py
# @Software: PyCharm
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from weapi import views

urlpatterns = [
    url(r'^add-apply-list', views.we_insert_apply_by_userId_view.as_view()),  # 预约申请列表
    url(r'^fee-item-list', views.select_feeItemCode_list_view.as_view()),  # 查询体检编码大类列表
    url(r'^login', views.weLoginView.as_view()),  # 登录
    # url(r'^register', views.registerView.as_view()),  # 注册开通
    url(r'^physicalList', views.weGetPhysicalExamListView.as_view()),  # 获取体检列表
    # # url(r'^physicalBasicDetails', views.getBasicPhysicalDetailsView.as_view()),  # 查询基本体检数据
    url(r'^urineTestItemList', views.weGetUrineTestItemListView.as_view()),  # 查询尿检项目类
    url(r'^urineTestItemDetails', views.weGetUrineTestItemDetailsView.as_view()),  # 查询尿检细项
    url(r'^EcgDetails', views.weGetEcgDetailsView.as_view()),  # 查询心电图
    url(r'^abdomenDetails', views.weGetAbdomenDetailsView.as_view()),  # 查询腹部超声
    url(r'^basicDetails', views.weGetBasicDetailsView.as_view()),  # 查询基本体检数据
    # url(r'^zcurineTestItemList', views.getUrineTestItemByRidListView.as_view()),  # 未知体检条码，根据个人序号查询最新体条码
]
