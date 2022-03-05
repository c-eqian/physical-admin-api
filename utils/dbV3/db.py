# -*- coding: utf-8 -*-
# @Time    : 2022-01-15 15:32
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : db.py
# @Software: PyCharm
import re
import time
from configparser import ConfigParser
import pymysql
from DBUtils.PooledDB import PooledDB
from api.path import DB_CONFIG_PATH
from utils.crypto._MD5 import SM4Utils
import random
from utils.log.log import Logger
from utils.redisCache.redisCache import Redis

_redis = Redis()
log = Logger()


def getTodayTime():
    a = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return a


def random_id():
    a = ""
    for j in range(6):
        a += str((random.randint(0, 9)))
    return a


def returnJson(result=None, status=200, msg='操作成功'):
    """
    作为字典的形式返回数据响应
    @param result: 返回结果
    @param status: 返回状态码
    @param msg: 提示信息
    @return:
    """
    if result is None:
        return {'status': status, 'msg': msg}
    else:
        return {'status': status, 'msg': msg, 'result': result}


def handleLeaveContent(data):
    ...


class database:
    def __init__(self):
        self.DbConnect_Pool = self.db_init()
        self.SM4 = SM4Utils()

    def query_apply_by_text(self, searchText, page=1, limit=50):
        """
        搜索。支持姓名，机构名称，身份证
        @param searchText: 搜索内容
        @param page:
        @param limit:
        @return:
        """
        sql = f"""
             SELECT COUNT(*) `total`
             FROM
                 apply_table
                 AT JOIN fh_personbasics fp ON AT.userId = fp.userId 
             WHERE
                 fp.name = '%{searchText}%' OR fp.idCard='%{searchText}%' 
                OR fp.org_name='%{searchText}%' AND fp.status=0
             """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = {}
            total = res.get('result').get('total')
            _res.update(total=total)
            sql = f"""
                  SELECT AT
                      .id,AT.org_code,AT.apply_type,CONVERT(AT.apply_time,CHAR(19)) `apply_time`,
                            CONVERT(AT.complete_time,CHAR(19)) `complete_time`,AT.apply_status,
                            AT.apply_reason,AT.operator_id,AT.userId
                        ,fp.org_name,fp.gender,CONVERT(fp.birthday,CHAR(10))
                  FROM
                      apply_table
                      AT JOIN fh_personbasics fp ON AT.userId = fp.userId 
                  WHERE
                     fp.name = '%{searchText}%' OR fp.idCard='%{searchText}%' 
                    OR fp.org_name='%{searchText}%' AND fp.status=0
                  ORDER BY
                     AT.apply_time desc limit {(page - 1) * limit},{limit}
                  """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get("status") == 200:
                data = res.get('result')
                _res.update(lt=data)
                res.update(result=_res)
                _redis.set(key=f"{searchText}{page}{limit}", value=str(res), timeout=60)
        return res

    def select_apply_by_org_code(self, org_code, page=1, limit=50):
        """
        通过机代码查询用户申请列表
        @param org_code: 机构代码
        @param page: 页
        @param limit: 大小
        @return:
        """
        sql = f"""
            SELECT COUNT(*) `total`
            FROM
                apply_table
                AT JOIN fh_personbasics fp ON AT.userId = fp.userId 
            WHERE
                AT.org_code = '{org_code}' AND fp.status=0
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = {}
            total = res.get('result').get('total')
            _res.update(total=total)
            sql = f"""
                  SELECT AT
                      .id,AT.org_code,AT.apply_type,CONVERT(AT.apply_time,CHAR(19)) `apply_time`,
                            CONVERT(AT.complete_time,CHAR(19)) `complete_time`,AT.apply_status,
                            AT.apply_reason,AT.operator_id,AT.userId
                        ,fp.org_name,fp.gender,CONVERT(fp.birthday,CHAR(10))
                FROM
                    apply_table
                    AT JOIN fh_personbasics fp ON AT.userId = fp.userId 
                WHERE
                    AT.org_code = '{org_code}' AND fp.status=0
                ORDER BY
                   AT.apply_time desc limit {(page - 1) * limit},{limit}
                """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get('status') == 200:
                data = res.get('result')
                _res.update(lt=data)
                res.update(result=_res)
                _redis.set(key=f"{org_code}{page}{limit}", value=str(res), timeout=60)
        return res

    def we_queryBasicPhysicalExamRes(self, Rid=None) -> dict:
        """
           根据体检条码查询基本体检详情
            身高、体重、体温、心率
        @param Rid: 查询基本体检数据
        @return:
        """
        sql = f"""
                SELECT 
                        pc.Height,pc.Weight,pc.BMI,
                        pc.RequisitionId,pc.LSBP,pc.LDBP,pc.RSBP,pc.RDBP,pc.ProjectName,
                        pc.Status,pc.ReviewDoctor,CONVERT(pc.ReviewDate,CHAR(19)) ReviewDate
                        from pat_test_checklist pc 
                        WHERE 
                        pc.RequisitionId='{Rid}'
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def we_getUrineTestDetailsByRidAndFic(self, Rid=None, Fic=None) -> dict:
        """
        根据条码及编码大类查询尿检细项
        :param Rid: 条码
        :param Fic: 体检编码大类
        :return:
        """
        sql = f"""
            SELECT 
            pf.ItemCode,pf.ItemName,pf.RequisitionId,pf.Lis_RangeState,pf.FeeItemCode,
            pf.Lis_Result,pf.Lis_ResultUnit,pf.Lis_RangeHighValue,pf.Lis_RangeLowValue,
            CONVERT(pf.ReceivedTime,CHAR(19)) 'ReceivedTime'
            from pat_test_result pf 
            WHERE 
            pf.RequisitionId='{Rid}' and pf.FeeItemCode='{Fic}'

           """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def we_getEcgDetails(self, RequisitionId: str, FeeItemCode: str):
        """
        根据条码及编码大类查询心电图
        @param RequisitionId:
        @param FeeItemCode:
        @return:
        """
        sql = f"""
                        SELECT 
                        pf.ECG_ExaminationsConlc,pf.ECG_ExaminationsFind,pf.ECG_Reportopter,
                        pf.RequisitionId,pf.FeeItemCode,
                        CONVERT(pf.ECG_ReportTime,CHAR(19)) 'ECG_ReportTime'
                        from pat_test_result pf 
                        WHERE 
                        pf.RequisitionId='{RequisitionId}' and pf.FeeItemCode='{FeeItemCode}'
                       """
        _RES = self.SqlSelectByOneOrList(sql=sql, type=1)
        return _RES

    def we_getAbdomenDetails(self, RequisitionId: str, FeeItemCode: str):
        """
        根据条码及编码大类查询腹部超声
        @param RequisitionId: 体检条码
        @param FeeItemCode: 项目编码
        @return:
        """
        sql = f"""
                        SELECT 
                        pf.PACS_Auditopter,pf.PACS_ExaminationsConlc,pf.PACS_ExaminationsFind,
                        pf.PACS_PhotoUID,pf.PACS_ExaminationsParts,pf.RequisitionId,pf.FeeItemCode,
                        pf.PACS_Auditopter,pf.PACS_Positive,
                        CONVERT(pf.PACS_AuditTime,CHAR(19)) 'PACS_AuditTime',
                        CONVERT(pf.PACS_CheckTime,CHAR(19)) 'PACS_CheckTime',
                        CONVERT(pf.PACS_RegistTime,CHAR(19)) 'PACS_RegistTime',
                        CONVERT(pf.PACS_ReportTime,CHAR(19)) 'PACS_ReportTime'
                        from pat_test_result pf WHERE 
                        pf.RequisitionId='{RequisitionId}' and pf.FeeItemCode='{FeeItemCode}'
                       """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def we_getUrineTestItemListByRequisitionId(self, RequisitionId=None, userId=None) -> dict:
        """
        :param userId: 是否知道体检条码，如果没有传入条码，则根据个人序号进行取当前年最新一条条码记录
        :param RequisitionId: 体检条码
        :return:
        """
        try:
            sql = f"""
                SELECT pf.RequisitionId,pf.BarCode,pf.ApplyDoctorName,
                pf.ApplyDoctorNo,pf.FeeItemCode,pf.FeeItemName,CONVERT(pf.ApplyDate,CHAR(19)) 'ApplyDate'
                 from pat_test_form  pf WHERE pf.RequisitionId='{RequisitionId}'
                """
            _res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if _res.get('status') == 200:
                _res.get('result').insert(0, {"RequisitionId": RequisitionId, "FeeItemName": "基本情况", "FeeItemCode": 0})
            return _res
        except Exception as e:
            print(f"getUrineTestItemListByRequisitionId:{e}")

    def we_getPhysicalExamListSql(self, userId, page=1, limit=50) -> dict:
        """
        :param userId: 用户ID
        :param page: 分页获取
        :param limit: 每页条目
        :return:
        """
        try:
            _SqlGetPhysicalExamList = f"""
               select c.RequisitionId,c.userId,c.org_code,c.ProjectName,c.ProjectNo,
               CONVERT(c.VisitingDate,CHAR(19)) 'VisitingDate',c.Operator
               from pat_test_checklist c where userId ={userId}  order by c.Did desc 
               limit {(page - 1) * limit},{limit} 
               """
            _res = self.SqlSelectByOneOrList(sql=_SqlGetPhysicalExamList, type=1)
            return _res
        except Exception as e:
            print(f"getPhysicalExamListSql:{e}")

    def we_registerSql(self, pwd: str, nick: str, idCard: str) -> dict:  # 注册验证
        """
        :param pwd: 密码
        :param nick: 昵称
        :param idCard: 有效证件
        :return:
        """
        res = {"status": 0, "msg": ''}  # 返回数据
        idCardDe = self.SM4.decryptData_ECB(idCard)  # 身份证解密
        try:
            _queryIsExistByIdCard = f"""
               SELECT id,idCard,name from fh_personbasics where idCard='{idCardDe}'
               """
            _queryRes = self.SqlSelectByOneOrList(sql=_queryIsExistByIdCard)
            RESULT = _queryRes.get("result")
            if _queryRes.get('status') == 200:  # 查询身份证成功
                _queryIsRegistered = f"""
                    SELECT a.idCard from fh_personbasics a 
                    join userinfo b on a.id = b.relation where a.idCard='{idCardDe}'
                   """
                _queryIsRegisteredRes = self.SqlSelectByOneOrList(sql=_queryIsRegistered)
                if _queryIsRegisteredRes.get("status") == 200:  # 此时能查询到，说明已经注册过
                    res.update(status=13205, msg="已开通，无需重复")
                elif _queryIsRegisteredRes.get("status") == 13204:  # 此时没能查询到，说明未注册过，可以注册
                    if nick == '':
                        nick = RESULT.get('name')
                    _sqlInsertByRegister = """
                       INSERT INTO userinfo 
                       ( userAccount,name, relation,userPassword,nickName,authority,status) 
                       VALUES ('{}','{}','{}','{}','{}',1,0
                       )

                       """.format(RESULT.get('idCard')[-8:], RESULT.get('name'), RESULT.get('id'), pwd, nick)
                    _res = self.insertSqlReturnId(sql=_sqlInsertByRegister)
                    if _res.get('status') == 200:
                        res.update(status=_res.get('status'), msg="开通成功")
                    else:
                        res.update(status=_res.get('status'), msg=_res.get('msg'))
            elif _queryRes.get('status') == 13204:
                res.update(status=_queryRes.get('status'), msg="用户不存在")
            else:
                res.update(status=_queryRes.get('status'), msg="操作失败")
            return res
        except Exception as e:
            log.logger.error(str(e))
            res.update(status=13203, msg="操作失败，请联系管理员")
            return res

    def we_LoginSql(self, u_name: str, pwd: str) -> dict:  # 登录验证
        """
        @param u_name: 账号
        @param pwd: 密码
        @return: 返回数据类型为json格式，status=200
                表示返回成功，13201表示账号存在，但密码不正确
                13204表示没该账号
                13203 异常错误
        """
        # De_crypto = self.SM4.decryptData_ECB(u_name)
        res = {}  # 返回数据
        EnString = self.SM4.encryptData_ECB(pwd)  # 加密密码
        try:
            SqlUserinfo = f"""
                          SELECT u.userAccount,u.name,u.userPassword,u.authority,u.status,u.relation,u.nickName,
                                  fp.age,fp.org_name,fp.org_code,fp.gender,fp.userId
                          from 
                          userinfo u join fh_personbasics fp on u.relation = fp.id 
                           where u.userAccount='{u_name}' AND fp.status=0
                          """
            _res = self.SqlSelectByOneOrList(sql=SqlUserinfo)
            if _res.get("status") == 200 and _res.get('result').get("status") in [0, '0']:
                if _res.get('result').get("userPassword") == EnString:
                    result = _res.get('result')
                    result.pop('userPassword', None)  # 删除密码键值，注意：如果pop删除，key不存在会报错，可以设置不存在时返回的值
                    result.pop('status', None)
                    res.update(status=_res.get('status', 200), msg='验证通过', result=result)
                else:
                    res.update(status=13201, msg='密码错误')
            elif _res["status"] == 200 and _res.get('result').get("status") in [1, '1']:
                res.update(status=13204, msg='账号已注销')
            elif _res.get('status') == 13204:
                res.update(status=_res.get('status', 13204), msg='账号不存在')
            else:
                res.update(status=_res.get('status', 13203), msg='未知错误')
            return res
        except Exception as e:
            res.update(status=13203, msg='抱歉，验证出错')
            log.logger.error(str(e))
            return res

    def likeSearchSuggestion(self, keyWords):
        """
        搜索建议。搜索姓名时有效，并且只返回前10条数据
        @param keyWords:
        @return:
        """
        sql = f"""
            SELECT name,userId FROM fh_personbasics 
            WHERE `name` LIKE '%{keyWords}%' ORDER BY id DESC LIMIT 10
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def likeSearch(self, searchText, page=1, limit=50):
        """
        模糊查询分页
        @param searchText: 关键字
        @param page: 页码
        @param limit: 数据量
        @return:
        """
        sql = f"""
            SELECT fp.name,fp.userId,fp.idcard,fp.org_code,fp.org_name,
                    fp.gender,CONVERT(fp.birthday,CHAR(19)) `birthday`,fp.phone,
                    fp.nation,fp.live_type,fp.creator,
                    CONVERT(fp.creatime,CHAR(19)) `creatime`
            FROM fh_personbasics fp where fp.name LIKE '%{searchText}%' 
            OR fp.org_name LIKE '%{searchText}%' 
            OR fp.idCard LIKE '%{searchText}%' and fp.status=0 
            ORDER BY fp.id DESC 
            limit {(int(page) - 1) * int(limit)},{int(limit)}
        """
        _res = self.SqlSelectByOneOrList(sql=sql, type=1)
        if _res.get('status') == 200:
            _redis.set(key=f"{searchText}{page}{limit}", value=str(_res), timeout=60)
        return _res

    def likeSearchTotal(self, searchText):
        """
        模糊查询结果总数，姓名、身份证、机构
        @param searchText: 模糊文本
        @return:
        """
        sql = f"""
            SELECT COUNT(*) `total` FROM fh_personbasics 
            WHERE `name` LIKE '%{searchText}%' 
            OR org_name LIKE '%{searchText}%' 
            OR idCard LIKE '%{searchText}%'
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def userDetailsByUserId(self, userId):
        """
        查询用户详情
        @param userId:
        @return:
        """
        sql = f"""
        select fp.id,fp.userId,fp.idCard,fp.name,
        fp.gender,fp.phone,fp.nation,fp.contact_name,
        fp.contact_phone,fp.live_type,fp.blood_type,
        fp.org_code,fp.org_name,fp.status,fp.creator,fp.last_updator,
        CONVERT(fp.creatime,CHAR(19)) `creatime` ,
            CONVERT(fp.birthday,CHAR(19)) `birthday` ,
            CONVERT(fp.last_updatime,CHAR(19)) `last_updatime`
            FROM fh_personbasics fp WHERE fp.userId='{userId}'
            """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            _redis.set(key=f"{userId}", value=str(_res), timeout=60)
        return _res

    def userTotal(self, org_id):
        """
        查询当前机构的用户总数
        @param org_id: 机构代码
        @return:
        """
        sql = f"""
            select COUNT(*) `total` FROM fh_personbasics WHERE org_code='{org_id}'
            """
        return self.SqlSelectByOneOrList(sql=sql)

    def getUserListByOrgId(self, org_id, page=1, limit=50):
        """
        查询当前机构的用户信息
        @param limit:
        @param page:
        @param org_id:
        @return:
        """
        sql = f"""
            SELECT fp.name,fp.userId,fp.idcard,fp.org_code,fp.org_name,
                    fp.gender,CONVERT(fp.birthday,CHAR(19)) `birthday`,fp.phone,
                    fp.nation,fp.live_type,fp.creator,
                    CONVERT(fp.creatime,CHAR(19)) `creatime`
            FROM fh_personbasics fp where fp.status=0 and fp.org_code='{org_id}'
            ORDER BY fp.id DESC 
            limit {(int(page) - 1) * int(limit)},{int(limit)}
        """
        _res = self.SqlSelectByOneOrList(sql=sql, type=1)
        if _res.get('status') == 200:
            _redis.set(key=f"{org_id}{page}{limit}", value=str(_res), timeout=60)
        return _res

    def login(self, userAccount, userPassword):
        """
        用户登录
        @param userAccount:
        @param userPassword:
        @return:
        """
        # 检查账号是否存在
        sql = f"""
                SELECT su.sys_user_account,su.user_id,su.org_id,
                su.sys_user_name,su.authority,su.sys_user_password,su.status
                FROM sys_user su 
                where su.sys_user_account='{userAccount}'
                """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            if _res.get('result').get('status') in [1, '1']:
                password = self.SM4.encryptData_ECB(plain_text=userPassword)
                if _res.get('result').get('sys_user_password') == password:
                    resultDict = {}
                    authority = _res.get('result').get('authority')
                    menuList = self.menuList(authority=authority)
                    resultDict['username'] = _res.get('result').get('sys_user_account')
                    resultDict['name'] = _res.get('result').get('sys_user_name')
                    resultDict['user_id'] = _res.get('result').get('user_id')
                    resultDict['org_id'] = _res.get('result').get('org_id')
                    # resultDict['password'] = _res.get('result').get('userPassword')
                    resultDict['menu'] = menuList
                    _res.update(status=200, msg='登录成功', result=resultDict)
                else:
                    _res.update(msg="密码错误", status=13201)
                    _res.pop('result')
            else:
                _res.update(status=13202, msg='用户已被禁用')
                _res.pop('result')
        elif _res.get('status') == 13204:
            _res.update(msg=f"账号{userAccount}不存在")
        else:
            _res.update(msg="登录失败，请稍后重试")
        return _res

    def menuList(self, authority):
        # 获得数据库连接池
        conn = self.DbConnect_Pool.connection()
        conn.ping(reconnect=True)
        cur = conn.cursor()
        col = """SHOW COLUMNS FROM menulist"""
        cur.execute(col)
        conn.commit()
        index = cur.fetchall()  # 返回字段
        _index = [x[0] for x in index]
        try:
            SqlMenuList = """
                           SELECT * from menulist
                           """
            cur.execute(SqlMenuList)
            conn.commit()
            result = cur.fetchall()
            Menu = []
            resultList = []
            if result:  # 返回不为空
                for item in result:
                    resultDict = {}
                    for i in range(len(_index)):
                        resultDict[_index[i]] = item[i]
                    authorityNum = resultDict['authority'].replace("'", '')
                    pattern = re.compile('\d+')
                    itemResult = pattern.findall(authorityNum)
                    if str(authority) in itemResult:
                        resultList.append(resultDict)
                        resultDict.pop('authority', None)
                        # del resultDict['authority']  # 删除权限的键值
                for item in resultList:
                    lst = []
                    ite = item['children'].replace("'", '')
                    pattern = re.compile('\d+')
                    itemResult = pattern.findall(ite)
                    for it in itemResult:
                        for items in resultList:
                            if items['menuid'] == int(it):
                                lst.append(items)
                                item['children'] = lst
                                # del item['path']
                                # del item['name']
                                # del item['component']
                                if item not in Menu:
                                    Menu.append(item)
            return Menu
        except Exception as e:
            log.logger.error(str(e))
            conn.close()
            cur.close()
            print(e)

    def test(self):

        sql = """
        SELECT uf.* FROM userinfo uf  where uf.id=25 limit 1
        """
        return self.SqlSelectByOneOrList(sql=sql)

    @staticmethod
    def getInsertId(cur):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        cur.execute("SELECT @@IDENTITY AS id")
        result = cur.fetchall()
        _dist = result[0]
        return _dist[0]

    def insertSqlReturnId(self, sql) -> dict:

        """
        新增，并且返回当前新增的id
        @param sql: 操作语句
        @return: id
        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                insertId = self.getInsertId(cur=cur)
                if insertId not in [0, '0', None]:
                    _sqlRes.update(status=200, msg='操作成功', insertId=insertId)
                else:
                    _sqlRes.update(status=13203, msg='操作失败')
                    conn.rollback()
            else:
                _sqlRes.update(status=status, msg='数据库连接错误')
        except Exception as e:
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def insertOrUpdateOrDeleteBySql(self, sql):
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                _sqlRes.update(status=200, msg='操作成功', row=cur.rowcount)
            else:
                _sqlRes.update(status=status, msg='数据库连接错误')
        except Exception as e:
            print(e)
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def getLastUserId(self):
        """
        查询最大的用户ID进行自增
        @return:
        """
        Sql = """
        SELECT userId FROM user_list ORDER BY userId DESC LIMIT 1
        """
        res = self.SqlSelectByOneOrList(sql=Sql)
        if res.get('status') == 200:
            userId = res.get('result').get('userId')
            if userId:
                return int(userId) + 1
        else:
            return 13204

    def db_init(self):
        try:
            cfg = ConfigParser()
            cfg.read(DB_CONFIG_PATH)
            DB_HOST = cfg.get('database', 'DB_HOST')
            DB_PORT = 3306
            DB_USER = cfg.get('database', 'DB_USER')
            DB_PASSWORD = cfg.get('database', 'DB_PASSWORD')
            DB_NAME = cfg.get('database', 'DB_NAME')
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
        except Exception as e:
            log.logger.error(str(e))
            print(f"初始化V3数据库失败：{e}")

    def init_conn_cur_index(self):
        try:
            if self.DbConnect_Pool:
                conn = self.DbConnect_Pool.connection()
                conn.ping(reconnect=True)
                cur = conn.cursor(pymysql.cursors.DictCursor)  # 获取游标,pymysql.cursors.DictCursor设置返回结果为字典类型
                return 200, conn, cur
            else:
                return 13203, None, None
        except Exception as e:
            log.logger.error(str(e))
            return 13203, None, None

    def selectByFaceId(self, faceId) -> dict:
        sql = f"""
         SELECT userName,faceStatus FROM user_list WHERE faceId={faceId}
        """
        return self.SqlSelectByOneOrList(sql)

    def SqlSelectByOneOrList(self, sql, type=0) -> dict:
        """
        功能：通过一条语句查询
        @param sql: 操作语句
        @param type: 0 返回一条，1返回多条
        @return:
        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                rows = cur.fetchall()
                if rows:
                    _sqlRes.update(status=200, msg='获取成功', result=rows[0] if type == 0 else rows)
                else:
                    _sqlRes.update(status=13204, msg='无数据')
            else:
                _sqlRes.update(status=status, msg='操作失败')
        except Exception as e:
            log.logger.error(str(e))
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes
