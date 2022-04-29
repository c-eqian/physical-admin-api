# -*- coding: utf-8 -*-
# @Time    : 2022-04-28 21:30
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : creatInfo.py
# @Software: PyCharm
from faker import Faker


def creat_user_info():
    """
    随机生成用户信息
    idCard:18位身份证
    @return:
    """
    info = {}
    result = {}
    try:
        fake = Faker(locale='zh_CN')
        idCard = fake.ssn(min_age=10, max_age=70)  # 身份证
        flag = idCard[-2]
        birthday = f"{idCard[6:10]}-{idCard[10:12]}-{idCard[12:14]}"
        phone = fake.phone_number()
        address = fake.address().split(" ")[0]
        email = fake.ascii_company_email()
        userAccount = idCard[-8:]
        if userAccount[0] in [0, '0']:
            a = list(userAccount)
            a[0] = '1'
            userAccount = ''.join(a)
        userPassword = userAccount
        job = fake.job()
        info.update(userAccount=userAccount, userPassword=userPassword)
        info.update(idCard=idCard, birthday=birthday, phone=phone, address=address, email=email, job=job)
        if int(flag) % 2 == 0:  # 如果是身份证最后一位是奇数，生成男名，反之，女名
            gender = 2
            userName = fake.name_male()
        else:
            gender = 1
            userName = fake.name_female()
        info.update(userName=userName, gender=gender)
        result.update(status=200, msg='操作成功', result=info)
    except Exception as e:
        result.update(status=13203, msg='操作失败')
        print(e)
    return result

# creat_user_info()
