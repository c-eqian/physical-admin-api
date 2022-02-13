# -*- coding: utf-8 -*-
# @Time    : 2021/7/22 17:54
# @Author  : 十三
# @Email   : 2429120006@qq.com
# @File    : base_sql.py
# @Software: PyCharm
import configparser
import random
import time

import pymysql
from DBUtils.PooledDB import PooledDB

"""
数据库初始基类

"""


class DataBase:
    def __init__(self):
        # self.cf = configparser.ConfigParser()
        self.DbConnect_Pool = self.init()

    def init(self):  # 初始化数据库
        # self.cf.read('../../config.ini')
        # print(f"信息{ self.cf.sections()}")
        # host = self.cf.get('DbConnect', 'DB_HOST')  # 远程主机
        # port = self.cf.get('DbConnect', 'DB_PORT')  # 端口号
        # user = self.cf.get('DbConnect', 'DB_USER')  # 用户
        # password = self.cf.get('DbConnect', 'DB_PASSWORD')  # 密码
        # db_name = self.cf.get('DbConnect', 'DB_NAME')  # 数据库
        # charset = self.cf.get('DbConnect', 'DB_CHARSET')  # 字符集
        # print(host, port, user, password, db_name, charset)
        DB_HOST = "rm-wz99r85cwf7sk18ge3o.mysql.rds.aliyuncs.com"
        DB_PORT = 3306
        DB_USER = "cyqmysql"
        DB_PASSWORD = "Cyq990127"
        DB_NAME = "physical"
        DB_CHARSET = "utf8"
        DbConnect_Pool = PooledDB(pymysql,
                                  5,
                                  charset=DB_CHARSET,
                                  host=DB_HOST,
                                  user=DB_USER,
                                  passwd=DB_PASSWORD,
                                  db=DB_NAME,
                                  port=int(DB_PORT)
                                  )
        return DbConnect_Pool

    def init_conn_cur_index(self):
        try:
            if self.DbConnect_Pool:
                conn = self.DbConnect_Pool.connection()
                conn.ping(reconnect=True)
                cur = conn.cursor()  # 获取游标
                return 200, conn, cur
            else:
                return 13203, None, None
        except Exception as e:
            return 13203, None, None

    def GetPresentDate(self):  # 获取当前日期
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return dt

    def getRidByPersonMark(self, mark):
        """
        通过个人序号查询当前年最新一条的体检条码
        :param mark: 个人序号
        :return:
        """
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        t = self.GetPresentDate()[:4]
        try:
            _getRid = f"""
                SELECT b.RequisitionId FROM
                 (
                SELECT  
                a.RequisitionId,CONVERT(a.VisitingDate,CHAR(4)) VisitingDate 
                FROM 
                pat_test_checklist a 
                WHERE 
                a.empi='{mark}' 
                ORDER BY 
                a.VisitingDate 
                DESC LIMIT 1
                ) b WHERE b.VisitingDate='{t}'

            """
            _RES = self.SqlSelectByOneOrList(_getRid)
            if _RES.get('status') == 200:
                _sqlRes.update(status=200, msg='查询成功', result=_RES.get('result')[0])
            else:
                _sqlRes.update(status=_RES.get('status'), msg=_RES.get('msg'))
        except Exception as e:
            _sqlRes.update(status=13203, msg=e)
        finally:
            return _sqlRes

    def getInsertId(self, cur):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        cur.execute("SELECT @@IDENTITY AS id")
        result = cur.fetchall()
        _dist = result[0]
        return _dist[0]

    """
    通过单条语句新增或修改
    """

    def SqlInsertOrUpdateByOne(self, sql):

        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                _sqlRes.update(status=200, msg='操作成功')
        except Exception as e:
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    """
    通过单条语句查询
    """

    def SqlSelectByOneOrList(self, sql) -> dict:
        """
        功能：通过一条语句查询
        :param sql: 操作语句
        :return:
        (('202020', '哈哈', 'Z9U5CMDmkJoIGv7uJJoB6w==', 0),)
        (('username', 253, None, 50, 50, 0, True),
        ('name', 253, None, 20, 20, 0, True),
         ('password', 253, None, 50, 50, 0, True),
         ('authority', 3, None, 2, 2, 0, True))

        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                rows = cur.fetchall()
                index = cur.description
                _result = []
                if len(rows) != 0:
                    for row in rows:
                        res = {}
                        for i in range(len(index)):
                            res[index[i][0]] = row[i]
                        _result.append(res)
                    _sqlRes.update(status=200, msg='获取成功', result=_result)
                else:
                    _sqlRes.update(status=13204, msg='无数据')
            else:
                _sqlRes.update(status=status, msg='数据库连接错误')
        except Exception as e:
            print(e)
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    # """
    # 根据体检条码查询尿检项目类
    # """
    #
    # def getUrineTestItemListByRequisitionId(self, RequisitionId: str) -> dict:
    #     """
    #     :param RequisitionId: 体检条码
    #     :return:
    #     """
    #     res = {"status": 0, "msg": ''}  # 返回数据
    #     try:
    #         _SqlGetUrineTestItemList = f"""
    #         SELECT pf.RequisitionId,pf.BarCode,pf.ApplyDoctorName,
    #         pf.ApplyDoctorNo,pf.FeeItemCode,pf.FeeItemName,CONVERT(pf.ApplyDate,CHAR(19)) 'ApplyDate'
    #          from pat_test_form  pf WHERE pf.RequisitionId='{RequisitionId}'
    #         """
    #         _SqlGetUrineTestItemListRes = self._SqlSelectByOneOrList(_SqlGetUrineTestItemList)
    #         if _SqlGetUrineTestItemListRes.get("status") == 200:
    #             res.update(status=200, msg='查询成功', result=_SqlGetUrineTestItemListRes.get('result'))
    #         else:
    #             res.update(status=_SqlGetUrineTestItemListRes.get("status"),
    #                        msg=_SqlGetUrineTestItemListRes.get("msg"))
    #         return res
    #     except Exception as e:
    #         res.update(status=13203, msg='查询出错')
    #         print(f"getUrineTestItemListByRequisitionId:{e}")
    #         return res
    #
    # """
    # 根据体检条码查询基本体检详情
    # 身高、体重、体温、心率
    # """
    #
    # def getBasicPhysicalDetailsByRequisitionId(self, RequisitionId: str) -> dict:
    #     """
    #     :param RequisitionId: 体检条码
    #     :return:
    #     """
    #     res = {"status": 0, "msg": ''}  # 返回数据
    #     try:
    #         _SqlGetBasicPhysicalDetails = f"""
    #         SELECT pc.Height,pc.Weight,pc.BMI,pc.RDBP,pc.RSBP,pc.LDBP,pc.LSBP,pc.Temperature,
    #         pc.tcm_identifier,pc.ini_identifier,pc.test_identifier,
    #         pc.adl_identifier,pc.Status,CONVERT (pc.ReviewDate,CHAR (19)) 'ReviewDate',pc.ReviewDoctor
    #          from pat_test_checklist  pc WHERE pc.RequisitionId='{RequisitionId}'
    #         """
    #         _SqlGetBasicPhysicalDetailsRes = self._SqlSelectByOneOrList(_SqlGetBasicPhysicalDetails)
    #         if _SqlGetBasicPhysicalDetailsRes.get("status") == 200:
    #             res.update(status=200, msg='查询成功', result=_SqlGetBasicPhysicalDetailsRes.get('result'))
    #         else:
    #             res.update(status=_SqlGetBasicPhysicalDetailsRes.get("status"),
    #                        msg=_SqlGetBasicPhysicalDetailsRes.get("msg"))
    #         return res
    #     except Exception as e:
    #         res.update(status=13203, msg='查询出错')
    #         print(f"getPhysicalDetailsByRequisitionId:{e}")
    #         return res
    #
    # """
    # 根据个人序号获取体检列表记录
    # """
    #
    # def getPhysicalExamListSql(self, personMark: str, page: int, limitNum: int) -> dict:
    #     """
    #     :param personMark: 个人序号
    #     :param page: 分页获取
    #     :param limitNum: 每页条目
    #     :return:
    #     """
    #     res = {"status": 0, "msg": ''}  # 返回数据
    #     if page < 1:
    #         page = 1
    #     try:
    #         _SqlGetPhysicalExamList = f"""
    #         select c.RequisitionId,c.empi,c.org_code,c.ProjectName,c.ProjectNo,
    #         CONVERT(c.VisitingDate,CHAR(19)) 'VisitingDate',c.Operator
    #         from pat_test_checklist c where  empi='{personMark}'  order by c.Did desc
    #         limit {(page - 1) * limitNum},{limitNum}
    #         """
    #         _SqlGetPhysicalExamListRes = self._SqlSelectByOneOrList(_SqlGetPhysicalExamList)
    #         if _SqlGetPhysicalExamListRes.get('status') == 200:
    #             res.update(status=200, msg="获取成功", result=_SqlGetPhysicalExamListRes.get('result'))
    #         else:
    #             res.update(status=_SqlGetPhysicalExamListRes.get('status'), msg=_SqlGetPhysicalExamListRes.get('msg'))
    #         return res
    #     except Exception as e:
    #         print(f"getPhysicalExamListSql:{e}")
    #         res.update(status=13203, msg='获取出错')
    #         return res
    #
    # """
    # 登录验证函数
    # """
    #
    # def LoginSql(self, u_name: str, pwd: str) -> dict:  # 登录验证
    #     """
    #     :param u_name: 账号
    #     :param pwd: 密码
    #     :return: 返回数据类型为json格式，status=200
    #             表示返回成功，13201表示账号存在，但密码不正确
    #             13204表示没该账号
    #             13203 异常错误
    #     """
    #     # De_crypto = self.SM4.decryptData_ECB(u_name)
    #     res = {"status": 0, "msg": ''}  # 返回数据
    #     EnString = self.SM4.encryptData_ECB(pwd)  # 加密密码
    #     try:
    #         SqlUserinfo = f"""
    #                 SELECT u.username,u.name,u.password,u.authority,u.Isuse,u.relation,u.nickName,
    #                         fp.age,fp.org_name,fp.org_code,fp.gender,fp.empi
    #                 from
    #                 userinfo u join fh_personbasics fp on u.relation = fp.id where username='{u_name}'
    #                 """
    #         _res = self._SqlSelectByOneOrList(SqlUserinfo)
    #         if _res.get("status") == 200 and _res.get('result')[0].get("Isuse") in [0, '0']:
    #             if _res.get('result')[0].get("password") == EnString:
    #                 result = _res.get('result')[0]
    #                 result.pop('password', None)  # 删除密码键值，注意：如果pop删除，key不存在会报错，可以设置不存在时返回的值
    #                 result.pop('Isuse', None)
    #                 res.update(status=_res.get('status', 200), msg='验证通过', result=result)
    #             else:
    #                 res.update(status=13201, msg='密码错误')
    #         elif _res["status"] == 200 and _res.get('result')[0].get("Isuse") in [1, '1']:
    #             res.update(status=13204, msg='账号已注销')
    #         elif _res.get('status') == 13204:
    #             res.update(status=_res.get('status', 13204), msg='账号不存在')
    #         else:
    #             res.update(status=_res.get('status', 13203), msg='未知错误')
    #         return res
    #     except Exception as e:
    #         res.update(status=13203, msg='抱歉，验证出错')
    #         print(e)
    #         return res
    #
    # """
    # 注册函数
    # """
    #
    # def RegisterSql(self, pwd: str, nick: str, idCard: str) -> dict:  # 注册验证
    #     """
    #     :param pwd: 密码
    #     :param nick: 昵称
    #     :param idCard: 有效证件
    #     :return:
    #     """
    #     res = {"status": 0, "msg": ''}  # 返回数据
    #     idCardDe = self.SM4.decryptData_ECB(idCard)  # 身份证解密
    #     try:
    #         _queryIsExistByIdCard = f"""
    #         SELECT id,idcard,name from fh_personbasics where idcard='{idCardDe}'
    #         """
    #         _queryRes = self._SqlSelectByOneOrList(_queryIsExistByIdCard)
    #         RESULT = _queryRes.get("result")
    #         if _queryRes.get('status') == 200:  # 查询身份证成功
    #             _queryIsRegistered = f"""
    #              SELECT a.idcard from fh_personbasics a
    #              join userinfo b on a.id = b.relation where a.idcard='{idCardDe}'
    #             """
    #             _queryIsRegisteredRes = self._SqlSelectByOne(_queryIsRegistered)[0]
    #             if _queryIsRegisteredRes.get("status") == 200:  # 此时能查询到，说明已经注册过
    #                 res.update(status=13205, msg="已开通，无需重复")
    #             elif _queryIsRegisteredRes.get("status") == 13204:  # 此时没能查询到，说明未注册过，可以注册
    #                 if nick == '':
    #                     nick = RESULT.get('name')
    #                 _sqlInsertByRegister = """
    #                 INSERT INTO userinfo
    #                 ( username,name, relation,password,nickName,status,authority,Isuse)
    #                 VALUES ('{}','{}','{}','{}','{}','0',0,0
    #                 )
    #
    #                 """.format(RESULT.get('idcard')[-8:], RESULT.get('name'), RESULT.get('id'), pwd, nick)
    #                 _res = self._SqlInsertOrUpdateByOne(_sqlInsertByRegister)
    #                 if _res.get('status') == 200:
    #                     res.update(status=_res.get('status'), msg="开通成功")
    #                 else:
    #                     res.update(status=_res.get('status'), msg=_res.get('msg'))
    #         elif _queryRes.get('status') == 13204:
    #             res.update(status=_queryRes.get('status'), msg="用户不存在")
    #         else:
    #             res.update(status=_queryRes.get('status'), msg="操作失败")
    #         return res
    #     except Exception as e:
    #         print(e)
    #         res.update(status=13203, msg=e)
    #         return res
    #
    # def UpdateSql(self):  # 修改信息
    #     pass
    #
    # def DelSql(self):  # 注销账号
    #     pass

#
# if __name__ == '__main__':
#     db = DataBase()
