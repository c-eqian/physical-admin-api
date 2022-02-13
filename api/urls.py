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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^login', views.loginView.as_view()),  # 登录
    url(r'^register', views.registerView.as_view()),  # 注册开通
    url(r'^physicalList', views.getPhysicalExamListView.as_view()),  # 获取体检列表
    # url(r'^physicalBasicDetails', views.getBasicPhysicalDetailsView.as_view()),  # 查询基本体检数据
    url(r'^urineTestItemList', views.getUrineTestItemListView.as_view()),  # 查询尿检项目类
    url(r'^urineTestItemDetails', views.getUrineTestItemDetailsView.as_view()),  # 查询尿检细项
    url(r'^EcgDetails', views.getEcgDetailsView.as_view()),  # 查询心电图
    url(r'^abdomenDetails', views.getAbdomenDetailsView.as_view()),  # 查询腹部超声
    url(r'^basicDetails', views.getBasicDetailsView.as_view()),  # 查询基本体检数据
    url(r'^zcurineTestItemList', views.getUrineTestItemByRidListView.as_view()),  # 未知体检条码，根据个人序号查询最新体条码
]
