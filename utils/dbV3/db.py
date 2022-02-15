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
from utils.redisCache.redisCache import Redis
from utils.log.log import Logger

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

    def login(self, userAccount, userPassword):
        """
        用户登录
        @param userAccount:
        @param userPassword:
        @return:
        """
        # 检查账号是否存在
        sql = f"""
                SELECT uf.userAccount,uf.name,uf.authority,uf.userPassword,uf.status
                FROM userinfo uf 
                where uf.userAccount='{userAccount}'
                """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            if _res.get('result').get('status') in [1, '1']:
                password = self.SM4.encryptData_ECB(plain_text=userPassword)
                if _res.get('result').get('userPassword') == password:
                    resultDict = {}
                    authority = _res.get('result').get('authority')
                    menuList = self.menuList(authority=authority)
                    resultDict['username'] = _res.get('result').get('userAccount')
                    resultDict['name'] = _res.get('result').get('name')
                    resultDict['password'] = _res.get('result').get('userPassword')
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
                print(rows)
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
