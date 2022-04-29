"""Applets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.views import static

from pc_api import views
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^add-sys-user', views.add_sys_user_view.as_view()),  # 新增系统机构用户
    url(r'^creat-user-info', views.creat_user_info_view.as_view()),  # 随机生成用户信息
    url(r'^sys-org-list', views.query_sys_org_list_view.as_view()),  # 查询系统机构列表
    url(r'^query_sys_user-list', views.query_sys_user_view.as_view()),  # 查询系统用户列表
    url(r'^add-apply-list', views.apply_by_userId_view.as_view()),  # 体检预约申请列表
    url(r'^query_user_details_by_idCard', views.query_user_details_by_idCard_view.as_view()),  # 通过身份证查询用户基本信息与体检项目类型
    url(r'^exam_result_audit_by_rid', views.exam_result_audit_by_rid_view.as_view()),  # 医生审核体检结果
    url(r'^query_exam_base_and_urine_by_rid', views.query_exam_base_and_urine_by_rid_view.as_view()),  # 根据体检编码新增尿检结果
    url(r'^check_exam_type_btn_by_rid', views.check_exam_type_btn_by_rid_view.as_view()),  # 根据体检编码新增尿检结果
    url(r'^insert-exam-urine-by-rid', views.insert_exam_urine_by_rid_view.as_view()),  # 根据体检编码新增尿检结果
    url(r'^query-exam-base-by-rid', views.query_exam_base_by_rid_view.as_view()),  # 通过体检编码查询基本体检结果
    url(r'^query_exam_upload', views.query_exam_upload_by_org_code_view.as_view()),  # 搜根据机构编码查询体检上传
    url(r'^get-cache-base-exam', views.get_cache_base_exam.as_view()),  # 获取缓存基本结果记录
    url(r'^cache-base-exam', views.cache_base_exam.as_view()),  # 新增缓存基本结果记录
    url(r'^insertbaseexam', views.insert_base_exam.as_view()),  # 新增基本结果记录
    #    根据当次体检编码查询当前用户需要体检的项目大类
    url(r'^current-exam-list', views.select_person_physical_list_by_RequisitionId_view.as_view()),
    url(r'^update-apply-status', views.update_apply_by_id_view.as_view()),  # 更新申请状态
    url(r'^item-list-detail', views.select_itemCode_list_by_feeItemCode_view.as_view()),  # 编码大类下的细项编码列表
    url(r'^fee-item-list', views.select_feeItemCode_list_view.as_view()),  # 查询体检编码大类列表
    url(r'^searchApply', views.query_apply_by_text_view.as_view()),  # 搜索申请列表
    url(r'^applyList', views.select_apply_by_org_code_view.as_view()),  # 申请列表
    url(r'^searchSuggestion', views.like_search_suggestion_view.as_view()),  # 搜索建议
    url(r'^likeSearch', views.likeSearchView.as_view()),  # 关键词搜索
    url(r'^SearchTotal', views.likeSearchTotalView.as_view()),  # 关键词搜索总数
    url(r'^user_details_by_idCard', views.user_details_by_idCard_view.as_view()),  # 用户详情
    url(r'^userDetails', views.userDetailsView.as_view()),  # 用户详情
    url(r'^userTotal', views.userTotalView.as_view()),  # 当前机构的用户数
    url(r'^userList', views.getUserListView.as_view()),  # 登录
    url(r'^login', views.loginView.as_view()),  # 登录
    url(r'^test', views.test.as_view()),
    url(r'^docs', include_docs_urls(title='接口文档')),



]
