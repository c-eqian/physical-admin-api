# -*- coding: utf-8 -*-
# @Time    : 2022-02-06 13:19
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : test.py
# @Software: PyCharm
# random
import time
import random
import re
# 导入某个模块的部分类或方法
from datetime import datetime, timedelta

# 导入常量并重命名
import constant as const
from utils.dbV3.db import database

db = database()


def insertSql(listData):
    for item in listData:
        sql = f"""
            INSERT INTO fh_personbasics(
            `userId`,`idCard`,`name`,`gender`,`birthday`,`phone`,`nation`,`live_type`,
            `blood_type`,`org_code`,`org_name`,`status`,`creator`,`creatime`,
            `last_updator`,`last_updatime`) VALUES (
            '{item.get("userId")}',{item.get("idCard")},'{item.get("name")}',
            {item.get("gender")},'{item.get("birthday")}',{item.get("phone")},
            '{item.get("nation")}',{item.get("live_type")},{item.get("blood_type")},
            '{item.get("org_code")}','{item.get("org_name")}',{item.get("status")},
            {item.get("creator")},NOW(),{item.get("creator")},NOW())
            """
        db.insertSqlReturnId(sql=sql)


class IdNumber(str):

    def __init__(self, id_number):
        super(IdNumber, self).__init__()
        self.id = id_number
        self.area_id = int(self.id[0:6])
        self.birth_year = int(self.id[6:10])
        self.birth_month = int(self.id[10:12])
        self.birth_day = int(self.id[12:14])

    def get_area_name(self):
        """根据区域编号取出区域名称"""
        return const.AREA_INFO[self.area_id]

    def get_birthday(self):
        """通过身份证号获取出生日期"""
        return "{0}-{1}-{2}".format(self.birth_year, self.birth_month, self.birth_day)

    def get_age(self):
        """通过身份证号获取年龄"""
        now = (datetime.now() + timedelta(days=1))
        year, month, day = now.year, now.month, now.day

        if year == self.birth_year:
            return 0
        else:
            if self.birth_month > month or (self.birth_month == month and self.birth_day > day):
                return year - self.birth_year - 1
            else:
                return year - self.birth_year

    def get_sex(self):
        """通过身份证号获取性别， 女生：0，男生：1"""
        return int(self.id[16:17]) % 2

    def get_check_digit(self):
        """通过身份证号获取校验码"""
        check_sum = 0
        for i in range(0, 17):
            check_sum += ((1 << (17 - i)) % 11) * int(self.id[i])
        check_digit = (12 - (check_sum % 11)) % 11
        return check_digit if check_digit < 10 else 'X'

    @classmethod
    def verify_id(cls, id_number):
        """校验身份证是否正确"""
        if re.match(const.ID_NUMBER_18_REGEX, id_number):
            check_digit = cls(id_number).get_check_digit()
            return str(check_digit) == id_number[-1]
        else:
            return bool(re.match(const.ID_NUMBER_15_REGEX, id_number))

    @classmethod
    def generate_id(cls, sex=0):
        """随机生成身份证号，sex = 0表示女性，sex = 1表示男性"""

        # 随机生成一个区域码(6位数)
        id_number = str(random.choice(list(const.AREA_INFO.keys())))
        # 限定出生日期范围(8位数)
        start, end = datetime.strptime("1960-01-01", "%Y-%m-%d"), datetime.strptime("2000-12-30", "%Y-%m-%d")
        birth_days = datetime.strftime(start + timedelta(random.randint(0, (end - start).days + 1)), "%Y%m%d")
        id_number += str(birth_days)
        # 顺序码(2位数)
        id_number += str(random.randint(10, 99))
        # 性别码(1位数)
        id_number += str(random.randrange(sex, 10, step=2))
        # 校验码(1位数)
        return id_number + str(cls(id_number).get_check_digit())


class AutomaticUsers:
    def __init__(self):

        # self.idCard = IdNumber()
        self.userInfoList = []
        self.userInfo = {}
        self.userId = 0
        self.lastUserId()
        # print(IdNumber.generate_id(self.random_sex))  # 随机生成身份证号

    def appendUser(self):
        self.userInfoList.append(self.userInfo)

    def returnUsers(self):
        return self.userInfoList

    def lastUserId(self):
        sql = f"""
                select fp.userId  from fh_personbasics fp order by fp.userId desc limit 1
            """
        res = db.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            self.userId = int(res.get('result').get('userId'))

    def randomStatus(self):
        """
        随机状态
        @return:
        """
        statusList = [0, 0, 0, 20, 0, 0]
        self.userInfo.update(status=random.choice(statusList))

    def randomUserId(self):
        """
        随机empi
        @return:
        """
        self.userId += 1
        self.userInfo.update(userId=self.userId)

    def randomOrgCode(self):
        """
        随机机构代码/名称
        @return:
        """
        orgCode = ['45060001', '45060002']
        orgName = {
            '45060001': "测试机构1",
            '45060002': "测试机构2",
            '45060003': "测试机构3",
            '45060004': "测试机构4",
            '45060005': "测试机构5",
            '45060006': "测试机构6"
        }
        creator = {
            '45060001': 100000,
            '45060002': 100001,
            '45060003': 100002,
            '45060004': 100003,
            '45060005': 100004,
            '45060006': 100005
        }
        org_code = random.choice(orgCode)
        self.userInfo.update(org_code=org_code)
        self.userInfo.update(org_name=orgName.get(org_code))
        self.userInfo.update(creator=creator.get(org_code))

    def randomBloodType(self):
        """
        随机血型
        @return:
        """
        bloodType = ['1', '2', '3', '4', '5']
        self.userInfo.update(blood_type=random.choice(bloodType))

    def randomLiveType(self):
        """
        随机常驻类型
        @return:
        """
        liveType = ['1', '2']
        self.userInfo.update(live_type=random.choice(liveType))

    def randomNation(self):
        """
        随机民族
        @return:
        """
        nationList = [
            '汉族', '蒙古族', '回族', '藏族', '维吾尔族', '苗族',
            '彝族', '壮族', '布依族', '朝鲜族', '满族', '侗族', '瑶族'
        ]
        nation = random.choice(nationList)
        self.userInfo.update(nation=nation)

    def randomPhone(self):
        """
        随机电话号码
        @return:
        """
        '''
        中国电信号段：133，153， 180，181，189，173， 177，149
        中国联通号段：130，131，132，155，156，185，186，145，176，185
        中国移动号段：134，135，136，137，138，139，150，151，152，158，159，182，183，184，147，178
        11位
        第一位 ：1
        第二位：3，4，5，7，8
        第三位：根据第二位来确定
            3 + 【0-9】
            4 + 【5，7，9】
            5 + 【0-9】 ！4
            7 + 【0-9】！ 4and9
            8 + 【0-9】
        后8位： 随机生成8个数字
        '''
        import random

        # creat_phone()
        # 生成电话号
        def creat_phone():
            # 第二位
            second = [3, 4, 5, 7, 8][random.randint(0, 4)]

            # 第三位的值根据第二位来确定
            third = {
                3: random.randint(0, 9),
                4: [5, 7, 9][random.randint(0, 2)],
                5: [i for i in range(10) if i != 4][random.randint(0, 8)],
                7: [i for i in range(10) if i not in [4, 9]][random.randint(0, 7)],
                8: random.randint(0, 9)
            }[second]
            # 后8位随机抽取
            suffix = ''
            for x in range(8):
                suffix = suffix + str(random.randint(0, 9))
            # 拼接
            return "1{}{}{}".format(second, third, suffix)

        phone = creat_phone()
        self.userInfo.update(phone=phone)

    def randomName(self):
        """
        随机名
        @return:
        """
        xing = '赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛' \
               '奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康' \
               '伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵' \
               '席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗' \
               '丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫' \
               '乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄' \
               '印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴鬱胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂' \
               '濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘' \
               '匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相' \
               '查后荆红游竺权逯盖益桓公万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳' \
               '淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空丌官司寇仉督子车颛孙端木' \
               '巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁晋楚闫法汝鄢涂钦段干百里东郭南门呼延归海羊舌微生' \
               '岳帅缑亢况郈有琴梁丘左丘东门西门商牟佘佴伯赏南宫墨哈谯笪年爱阳佟第五言福'
        ming = '伟刚勇毅俊峰强军平保东文辉力明永健世广志义兴良海山仁波宁贵福生龙元全国胜学祥才发武新利清' \
               '飞彬富顺信子杰涛昌成康星光天达安岩中茂进林有坚和彪博诚先敬震振壮会思群豪心邦承乐绍功松善' \
               '厚庆磊民友裕河哲江超浩亮政谦亨奇固之轮翰朗伯宏言若鸣朋斌梁栋维启克伦翔旭鹏泽晨辰士以建家' \
               '致树炎德行时泰盛秀娟英华慧巧美娜静淑惠珠翠雅芝玉萍红娥玲芬芳燕彩春菊兰凤洁梅琳素云莲真环' \
               '雪荣爱妹霞香月莺媛艳瑞凡佳嘉琼勤珍贞莉桂娣叶璧璐娅琦晶妍茜秋珊莎锦黛青倩婷姣婉娴瑾颖露瑶' \
               '怡婵雁蓓纨仪荷丹蓉眉君琴蕊薇菁梦岚苑筠柔竹霭凝晓欢霄枫芸菲寒欣滢伊亚宜可姬舒影荔枝思丽秀' \
               '飘育馥琦晶妍茜秋珊莎锦黛青倩婷宁蓓纨苑婕馨瑗琰韵融园艺咏卿聪澜纯毓悦昭冰爽琬茗羽希'
        X = random.choice(xing)
        nameLength = random.choice([2])  # 名字长度
        M = "".join(random.choice(ming) for i in range(nameLength))
        uName = X + M
        self.userInfo.update(name=uName)

    def randomBirthday(self):
        """
        随机出生日期
        @return:
        """

        random_sex = random.randint(0, 1)  # 随机生成男(1)或女(0)
        idCard = IdNumber.generate_id(random_sex)
        self.userInfo.update(idCard=idCard)
        birthday = idCard[6:10] + '-' + idCard[10:12] + '-' + idCard[12:14]
        self.userInfo.update(birthday=birthday)
        gender = idCard[-1]
        if gender == 'X':
            gender = '2'
        elif int(gender) % 2:
            gender = '1'
        else:
            gender = '2'
        self.userInfo.update(gender=gender)


a = AutomaticUsers()
a.lastUserId()
if a.userId != 0:
    print("生成数据中...")
    for i in range(1, 3000):
        a.randomName()
        a.randomPhone()
        a.randomNation()
        a.randomOrgCode()
        a.randomBirthday()
        a.randomLiveType()
        a.randomStatus()
        a.randomBloodType()
        a.randomUserId()
        a.appendUser()
        a.userInfo = {}
        time.sleep(0.1)
        print(f"生成数据第{i}条已完成")
        userList = a.returnUsers()
        insertSql(listData=[userList[-1]])
        a.userInfoList = []
# print()
