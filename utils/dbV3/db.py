# -*- coding: utf-8 -*-
# @Time    : 2022-01-15 15:32
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : db.py
# @Software: PyCharm
import time
from configparser import ConfigParser
import pymysql
from DBUtils.PooledDB import PooledDB
from api.path import DB_CONFIG_PATH
from utils.crypto._MD5 import SM4Utils
import random
from utils.redisCache.redisCache import Redis

_redis = Redis()


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

    def publishContent(self, userId, content):
        """
        发布留言
        @param userId:
        @param content: 内容
        @return:
        """
        sql = f"""
        INSERT 
        INTO content (userId, publishTime, content)
        VALUES
        ({userId},now(),'{content}');
        """
        _res = self.insertSqlReturnId(sql=sql)
        if _res.get('status') == 200:
            _redis.deleteKeys(key=str(userId) + '-*')  # 删除缓存
            _res.update(msg='发布成功')
        else:
            _res.update(msg='发布失败')
        return _res

    def addComment(self, userId, commentText, contentId):
        """
        添加评论
        @param userId:
        @param commentText: 评论内容
        @param contentId: 评论留言的Id
        @return:
        """
        sql = f"""
        INSERT 
        INTO comment (userId, commentTime, contentId,commentText)
        VALUES
        ({userId},now(),{contentId},'{commentText}');
        """
        _res = self.insertSqlReturnId(sql=sql)
        if _res.get('status') == 200:
            sql = f"""
                SELECT ul.userName,ul.userId,ct.commentText,ct.id,CONVERT(ct.commentTime,CHAR(19)) `commentTime` FROM 
                user_list ul join comment ct on ul.userId = ct.userId where ct.id={_res.get('insertId', 0)}
            """
            _res = self.SqlSelectByOneOrList(sql=sql)
            if _res.get('status') == 200:
                _res.update(msg='评论成功')
        return _res

    def addLike(self, userId, contentId):
        """
        点赞
        @param userId:
        @param contentId: 留言Id
        @return:
        """
        sql = f"""
        INSERT 
        INTO likes (userId, likeTime, contentId)
        VALUES
        ({userId},now(),{contentId});
        """
        _res = self.insertSqlReturnId(sql=sql)
        if _res.get('status') == 200:
            print(_res.get('insertId'))
            sql = f"""
                SELECT ul.userName,ul.userId,l.id,CONVERT(l.likeTime,CHAR(19)) `likeTime` FROM 
                user_list ul join likes l on ul.userId = l.userId where l.id={_res.get('insertId', 0)}
            """
            _res = self.SqlSelectByOneOrList(sql=sql)
            if _res.get('status') == 200:
                _res.update(msg="点赞成功")
        return _res

    def cancelLike(self, userId, contentId):
        """
        取消点赞
        @param userId: 用户Id
        @param contentId: 留言Id
        @return:
        DELETE t1 , t2 FROM t1
        INNER JOIN
            t2 ON t2.ref = t1.id
        WHERE
            t1.id = 1;
        """
        sql = f"""
            SELECT id from likes where userId={userId} and contentId={contentId}
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get("status") == 200:
            ID = res.get("result").get('id')
            sql = f"""
                    DELETE FROM likes WHERE userId={userId} AND contentId={contentId}
                """
            _res = self.insertOrUpdateOrDeleteBySql(sql=sql)
            if _res.get('status') == 200:
                _res.update(msg='已取消', result={'id': ID})
            else:
                _res.update(msg='操作失败')
            return _res
        else:
            res.update(msg="操作失败")

    def getLikesAndComment(self, res, userId):
        data = res
        try:
            for index, item in enumerate(res):
                contentId = item.get('id', 0)
                sql = f"""
                SELECT ls.id,CONVERT(ls.likeTime,CHAR(19)) `likeTime` ,b.userName,b.userId
                FROM likes ls JOIN (SELECT ul.userId,ul.userName 
                FROM user_list ul) b on ls.userId = b.userId where ls.contentId={contentId} 
                group by ls.userId
                """
                _res = self.SqlSelectByOneOrList(sql=sql, type=1)
                if _res.get('status') == 200:
                    data[index].update(likes=_res.get('result'))
                    for inde, ite in enumerate(_res.get('result')):
                        if int(userId) == ite.get('userId'):
                            print(2)
                            data[index].update(isLike=True)
                        else:
                            data[index].update(isLike=False)
                else:
                    data[index].update(likes=[])
                    data[index].update(isLike=False)
                sql = f"""
                    SELECT
                        ct.id,
                        ct.commentText,
                        CONVERT (
                            ct.commentTime,
                        CHAR ( 19 )) `commentTime`,
                        b.userName 
                    FROM
                        `comment` ct
                        JOIN ( SELECT ul.userId, ul.userName FROM user_list ul ) b ON ct.userId = b.userId 
                    WHERE
                        ct.contentId ={contentId}
                    """
                _res = self.SqlSelectByOneOrList(sql=sql, type=1)
                if _res.get('status') == 200:
                    data[index].update(comment=_res.get('result'))
                else:
                    data[index].update(comment=[])
            return 200, data

        except Exception as e:
            print(e)
            return 500, None

    def getLeaveContent(self, userId, page=1, limit=20):
        """
        获取留言数据
        @param userId:
        @param page: 默认1
        @param limit: 默认20
        @return:
        """
        sql = f"""
        SELECT
        ct.id,ct.content,ct.userId,
        CONVERT (
            ct.publishTime,
        CHAR ( 19 )) `publishTime`,
        b.userName,b.avatarUrl
        FROM content ct JOIN 
        (SELECT ul.userName,us.avatarUrl,ul.userId from user_list ul JOIN user_sys us on ul.userId=us.userId) b
         ON ct.userId=b.userId  ORDER BY ct.publishTime DESC LIMIT {(int(page) - 1) * limit},{limit}
    """
        _res = self.SqlSelectByOneOrList(sql=sql, type=1)
        if _res.get('status') == 200:
            status, data = self.getLikesAndComment(_res.get('result'), userId=userId)
            print(status)
            if status == 200:
                _res.update(result=data)
            _redis.set(key=str(userId) + '-' + str(page), value=str(_res), timeout=60)
        return _res

    def todayPassTotal(self):
        """
        查询今日访客总数
        @return:
        """
        nowTime = getTodayTime()
        sql = f"""
        SELECT COUNT(*) `total` 
        FROM 
        (SELECT  DISTINCT p.userId,p.passTime from pass p 
        WHERE  CONVERT(p.passTime,CHAR(10))='{nowTime[:10]}'
        ) a 
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def todayWaringTotal(self):
        """
        查询今日告警总数
        @return:
        """
        nowTime = getTodayTime()
        sql = f"""
                SELECT COUNT(*) `total` FROM pass p 
                WHERE p.passStatus="失败" and CONVERT(p.passTime,CHAR(10))='{nowTime[:10]}'
            """
        return self.SqlSelectByOneOrList(sql=sql)

    def isSms(self):
        sql = """
        SELECT s.sms FROM sms s
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def findPassWayByUserId(self, userId):
        """
        根据用户id查询通行方式状态
        @param userId: 用户Id
        @return:
        """

        def handleData(result):
            print(result)
            dirt = {}
            lt = []
            dirt.update(title="人脸识别", faceId=result.get("faceId"), faceStatus=result.get("faceStatus"),
                        faceRegisterTime=result.get("faceRegisterTime"))
            lt.append(dirt)
            dirt = {}
            dirt.update(title="门禁门卡", idCard=result.get("idCard"), idCardStatus=result.get("idCardStatus"),
                        idCardRegisterTime=result.get("idCardRegisterTime"))
            lt.append(dirt)
            return lt

        sql = f"""
                SELECT ul.faceStatus,ul.faceId,CONVERT(ul.faceRegisterTime,CHAR(16)) "faceRegisterTime",ul.idCardStatus,
                CONVERT(ul.idCardRegisterTime,CHAR(16))  "idCardRegisterTime",ul.idCard
                FROM user_list ul 
                WHERE ul.userId={userId}
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _resList = handleData(result=res.get('result'))
            res.update(result=_resList)
        return res

    def findPassWord(self, userName, userAccount, newUserPassword):
        """
        用户找回密码
        @param userName: 用户名
        @param userAccount: 登录账号
        @param newUserPassword: 登陆密码
        @return:
        """
        _checkUserName = self.selectByUserName(userName=userName)  # 检查用户名是否存在
        if _checkUserName.get('status') == 200:
            userId = _checkUserName.get('result').get('userId')
            sql = f"""
                    UPDATE user_sys 
                    SET userPassWord='{self.SM4.encryptData_ECB(plain_text=newUserPassword)}'
                    WHERE userAccount='{userAccount}' AND userId={userId}
                    """
            _res = self.insertOrUpdateOrDeleteBySql(sql=sql)
            if _res.get('status') == 200 and int(_res.get('row', 0)) > 0:
                _res.update(status=200, msg="找回密码成功")
                _res.pop("row", None)
            elif _res.get("status") == 200 and int(_res.get("row", 0)) == 0:
                if not userId:
                    _res.update(status=13204, msg=f"账号 {userAccount} 与用户名 {userName} 信息不匹配")
                else:
                    sql = f"""
                    SELECT  userPassWord  FROM user_sys
                    WHERE userPassWord='{self.SM4.encryptData_ECB(plain_text=newUserPassword)}'
                    AND userAccount='{userAccount}'
                    """
                    res = self.SqlSelectByOneOrList(sql=sql)
                    if res.get('status') == 200:
                        _res.update(status=13204, msg="新密码不能与原密码一致")
                    else:
                        _res.update(status=13204, msg=f"账号 {userAccount} 不存在 或与用户名 {userName} 信息不匹配")
                _res.pop("row", None)
            else:
                _res.update(status=13203, msg="操作失败，请联系管理员")
            return _res

        elif _checkUserName.get('status') == 13204:
            _checkUserName.update(msg=f"用户名 {userName} 不存在")
        else:
            _checkUserName.update(msg=f"操作失败，请联系管理员")
        return _checkUserName

    def addUser(self, userName, sex, birthday, contactNumber, userAccount=None, userPassWord=None):
        """
        新增用户
        @param userName: 用户名
        @param sex: 性别
        @param birthday: 出生日期
        @param contactNumber: 联系方式
        @param userAccount: 账号--开通时使用
        @param userPassWord: 密码--开通时使用
        @return:

        """
        _check = self.selectByUserName(userName=userName)
        if _check.get('status') == 13204:
            userId = self.getLastUserId()
            if userId != 13204:
                if userAccount and userPassWord:
                    sql = f"""
                        SELECT a.userAccount 
                        FROM user_sys a 
                        where a.userAccount='{userAccount}'
                        """
                    res = self.SqlSelectByOneOrList(sql=sql)
                    if res.get('status') == 13204:
                        sql = f"""
                             INSERT INTO user_list (userName,sex,birthday,contactNumber,userId,type,status,addTime)
                            VALUES ('{userName}',{sex},'{birthday}','{contactNumber}',{userId},0,'正常',now())
                            """
                        _res = self.insertSqlReturnId(sql=sql)
                        if _res.get('status') == 200:
                            sql = f"""
                                    INSERT INTO user_sys 
                                (userAccount,
                                userPassWord,auth,userId,isUsed,registerTime,changeTime)
                                    VALUES 
                                ('{userAccount}','{self.SM4.encryptData_ECB(plain_text=userPassWord)}',0,{userId},{0},now(),now())
                                                """
                            res = self.insertSqlReturnId(sql=sql)
                            if res.get("status") == 200:
                                res.pop('insertId', None)
                                res.update(msg="注册成功且已开通账号登录")
                                _redis.delete(str(contactNumber))
                        return res
                    elif res.get("status") == 200:
                        return returnJson(status=13206, msg=f"登录名 {userAccount} 已被占用")
                    else:
                        return returnJson(status=13203, msg='服务器故障，请联系管理员')
                else:
                    sql = f"""
                         INSERT INTO user_list (userName,sex,birthday,contactNumber,userId,type,status,addTime)
                        VALUES ('{userName}',{sex},'{birthday}','{contactNumber}',{userId},0,'正常',now())
                        """
                    _res = self.insertSqlReturnId(sql=sql)
                    if _res.get('status') == 200:
                        if userAccount and userPassWord:
                            ...
                        else:
                            _res.pop('insertId', None)
                            _res.update(msg="注册成功")
                            _redis.delete(str(contactNumber))
                    return _res
            else:
                return {'status': 13203, 'msg': "服务繁忙，请稍后再试"}
        elif _check.get("status") == 200:
            _check.pop("result", None)
            _check.update(status=13206, msg="用户已存在")
        else:
            _check.update(status=13203, msg="操作失败，请联系管理员")
        return _check

    def updateLoginPassWord(self, userId, newPassword, oldPassword) -> dict:
        """
        用户修改密码
        @param userId: 用户Id
        @param newPassword: 新密码
        @param oldPassword: 旧密码
        @return:
        """
        sql = f"""
                        SELECT us.userPassWord FROM user_sys us WHERE  us.userId={userId}
                    """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get("status") == 200:
            oldPwd = _res.get('result').get('userPassWord')
            if oldPwd != self.SM4.encryptData_ECB(plain_text=newPassword):
                if self.SM4.encryptData_ECB(plain_text=oldPassword) == oldPwd:
                    sql = f"""
                                 UPDATE user_sys 
                                SET userPassWord='{self.SM4.encryptData_ECB(plain_text=newPassword)}' 
                                WHERE userId={userId} 
                            """
                    res = self.insertOrUpdateOrDeleteBySql(sql=sql)
                    if res.get('status') == 200:
                        res.update(msg="修改成功")
                    return res
                else:
                    _res.update(status=13201, msg="原密码不正确")
                    _res.pop("result", None)
            else:
                _res.update(status=13201, msg="原密码与新密码不能一样")
                _res.pop("result", None)
        elif _res.get("status") == 13204:
            _res.update(msg=f"用户ID {userId} 不存在")
        return _res

    def passRecordByUserId(self, userId, limit=30, page=1):
        """
        根据用户Id查询通行记录
        @param page: 页码
        @param limit: 记录条数
        @param userId: 用户id
        @return:
        """
        sql = f"""
            SELECT ul.userName,p.userId, p.passType,p.passStatus,p.io,p.passTime 
            FROM pass p join user_list ul on p.userId = ul.userId
            WHERE p.userId={userId} ORDER BY p.id DESC limit {(page - 1) * limit},{limit}
            """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def logoutByUserId(self, userId, userPassWord):
        """
        通过用户Id注销用户登录账号
        @param userId: 用户id
        @param userPassWord: 登录密码
        @return:
        """
        sql = f"""
             UPDATE user_sys 
            SET isUsed={-1},changeTime=now() 
            WHERE userId={userId} AND userPassWord='{self.SM4.encryptData_ECB(plain_text=userPassWord)}'
        """
        res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        if res.get('status') == 200 and int(res.get('row', 0)) == 1:
            return {"status": 200, "msg": "注销成功"}
        elif res.get('status') == 200 and int(res.get('row', 0)) == 0:
            return {"status": 13201, "msg": "密码错误"}
        else:
            return {"status": 13203, "msg": "注销失败"}

    def uploadAvatar(self, userId, avatarUrl):
        """

        @param userId:
        @param avatarUrl: 头像路径
        """
        sql = f"""
            UPDATE user_sys SET avatarUrl='{avatarUrl}' WHERE userId={userId} 
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def userDetailInfo(self, userId):
        """
        查询用户id的详细信息
        @param userId: 用户id
        @return:
        """
        sql = f"""
            SELECT us.userAccount,us.auth,us.userId,us.registerTime, 
                    ul.userName,ul.sex,CONVERT(ul.birthday,CHAR(10)) "birthday",ul.status,
                    ul.idCard,ul.faceId,ul.contactNumber,ul.idCardRegisterTime,
                    ul.faceRegisterTime,
                    ul.idCardStatus,ul.faceStatus
            FROM user_sys us 
                    join user_list ul
                    on us.userId = ul.userId
            WHERE ul.userId={userId}
            """
        return self.SqlSelectByOneOrList(sql=sql)

    def userRegister(self, userName, loginAccount, loginPwd):
        """
       用户开通登录
       @param userName: 用户名
       @param loginAccount: 登录名
       @param loginPwd: 登录密码
       @return: 开通结果信息
       """
        sql = f"""
        SELECT a.userAccount 
        FROM user_sys a 
            join user_list ul 
            on a.userId = ul.userId 
        WHERE ul.userName='{userName}'
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 13204:
            sql = f"""
                SELECT a.userAccount FROM user_sys a where a.userAccount='{loginAccount}'
                """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get('status') == 13204:
                Sql = f"""
                        INSERT INTO user_sys ( userAccount,userPassWord, userId,auth,isUsed,registerTime) SELECT
                       '{loginAccount}',
                        '{self.SM4.encryptData_ECB(plain_text=loginPwd)}',
                        a.userId,
                        0,
                        0,
                        now()
                        FROM
                            user_list a 
                        WHERE
                            EXISTS ( SELECT userName FROM user_list WHERE userName = '{userName}' ) 
                            AND a.userName = '{userName}'
                    """
                res = self.insertSqlReturnId(sql=Sql)
                if res.get('status') == 200:
                    if res.get('insertId') not in [0, '0']:
                        return returnJson(status=200, msg='开通成功')
                    else:
                        return returnJson(status=13204, msg=f"开通失败，用户名 {userName} 不存在")
                else:
                    return returnJson(status=13203, msg='服务器故障，请联系管理员')
            elif res.get('status') == 200:
                return returnJson(status=13206, msg="登录名已被占用")
            else:
                return returnJson(status=13203, msg='服务器故障，请联系管理员')
        elif res.get("status") == 200:
            return returnJson(status=13205, msg="已开通，无需重复")
        else:
            return returnJson(status=13203, msg='服务器故障，请联系管理员')

    def userLogin(self, userAccount, userPwd):
        """
        用户登录
        """
        Sql = f"""
            SELECT a.userAccount,a.userPassWord,a.auth,a.userId,a.isUsed,a.avatarUrl,ul.userName,ul.sex  
            FROM user_sys a join user_list ul on a.userId = ul.userId
            WHERE a.userAccount='{userAccount}' 
        """
        res = self.SqlSelectByOneOrList(sql=Sql)
        if res.get('status') == 200:
            if res.get('result').get('isUsed') in [0, '0']:
                EnUserPwd = self.SM4.encryptData_ECB(userPwd)  # 加密密码
                if res.get('result').get('userPassWord') == EnUserPwd:
                    result = res.get('result')
                    result.pop('userPassWord', None)
                    result.pop('isUsed', None)
                    return returnJson(status=res.get('status'), msg=res.get('msg'), result=result)
                else:
                    return returnJson(status=13201, msg='密码错误')
            elif res.get('result').get('isUsed') in [-1, '-1']:
                return returnJson(status=13202, msg='用户已注销')
            else:
                return returnJson(status=13202, msg='用户被冻结')
        elif res.get('status') == 13204:
            return returnJson(status=res.get('status'), msg='用户不存在')
        else:
            return returnJson(status=res.get('status'), msg='操作失败')

    def selectPassContent(self, content):
        if content.isdigit():
            sql = f"""
            SELECT 
            A.userName,A.userId,A.idCard, A.age,A.sex,A.faceId,B.passType,B.passStatus,B.enterTime,B.outTime 
            FROM 
            user_list A join pass B on A.userId=B.userId WHERE A.userId={content} OR A.userId LIKE '{'%' + content + '%'}' LIMIT 50
            """
        else:
            sql = f"""
            SELECT 
            A.userName,A.userId,A.idCard, A.age,A.sex,A.faceId,B.passType,B.passStatus,B.enterTime,B.outTime  
            FROM 
            user_list A join pass B on A.userId=B.userId WHERE A.userName='{content}' OR A.userName LIKE '%{content}%' LIMIT 50
            """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def selectPassUserTotal(self):
        """
        查询用户总数
        @return:
        """
        sql = """
            SELECT COUNT(*) 'total' FROM pass
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def selectPassUserList(self, page=1, limit=50):
        """
        获取访客记录
        @return:
        """
        Sql = f"""
        SELECT A.userName,A.userId,CONVERT(A.birthday,CHAR(10)) `birthday`,A.sex,A.idCard,
        A.faceId,B.passType,B.passStatus,
        B.io,CONVERT(B.passTime,CHAR(19)) `passTime`
        FROM 
        user_list A join pass B on A.userId=B.userId
        LIMIT {(page - 1) * limit},{limit}
        """
        return self.SqlSelectByOneOrList(sql=Sql, type=1)

    def deleteUserByUserId(self, userId):
        """
        通过用户id进行删除
        @param userId:用户id
        @return:
        """
        Sql = f"""
        DELETE FROM user_list WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=Sql)

    def selectByUserName(self, userName):
        """
        通过用户名查询是否已存在
        @param userName:
        @return:
        """
        sql = f"""
             SELECT userName,userId FROM user_list WHERE userName='{userName}'
         """
        return self.SqlSelectByOneOrList(sql=sql)

    def enableStatusByUserId(self, userId):
        """
        通过用户id启用
        @param userId: 用户id
        @return:
        """
        sql = f"""
        UPDATE user_list SET status='正常' WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def enableFaceByUserId(self, userId):
        """
        通过用户id启用刷脸
        @param userId: 用户id
        @return:
        """
        sql = f"""
        UPDATE user_list SET faceStatus='正常' WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def enableIdCardByUserId(self, userId):
        """
        通过用户id启用刷卡
        @param userId:用户id
        @return:
        """
        sql = f"""
        UPDATE user_list SET idCardStatus='正常' WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def disableStatusByUserId(self, userId):
        sql = f"""
        UPDATE user_list SET status='已停用' WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def disableFaceByUserId(self, userId):
        sql = f"""
        UPDATE user_list SET faceStatus='已停用' WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def disableIdCardByUserId(self, userId):
        """
        通过用户id停用刷卡刷卡
        @param userId:
        @return:
        """
        sql = f"""
        UPDATE user_list SET idCardStatus='已停用' WHERE userId={userId}
        """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def selectByUserNameOrUserId(self, content):
        """
        通过用户名或者用户ID查询
        @return:
        """
        if content.isdigit():
            sql = f"""
            SELECT 
            userName,userId,idCard, age,sex,
            faceId,contactNumber,idCardRegisterTime,
            faceRegisterTime,idCardStatus,faceStatus,
            status 
            FROM 
            user_list WHERE userId={content} OR userId LIKE '{'%' + content + '%'}' LIMIT 50
            """
        else:
            sql = f"""
            SELECT 
            userName,userId,idCard, age,sex,
            faceId,contactNumber,idCardRegisterTime,
            faceRegisterTime,idCardStatus,faceStatus,
            status 
            FROM 
            user_list WHERE userName='{content}' OR userName LIKE '%{content}%' LIMIT 50
            """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def getUserCount(self):
        """
        查询用户总数
        @return:
        """
        sql = """
            SELECT COUNT(*) 'total' FROM user_list
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def selectUserList(self, page=1, limit=50):
        """
        查询登记的用户数据
        @return:
        """
        sql = f"""
        SELECT 
        userName,userId,idCard, CONVERT(birthday,CHAR(10)) `birthday`,sex,
        faceId,contactNumber,CONVERT(idCardRegisterTime,CHAR(19)) `idCardRegisterTime`,
        CONVERT(faceRegisterTime,CHAR(19)) `faceRegisterTime`,idCardStatus,faceStatus,
        status 
        FROM 
        user_list LIMIT {(page - 1) * limit},{limit}
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def insertOrUpdateIdCardByUserName(self, userName, idCard, userId):
        """
        通过用户名进行更新或修改用户门卡
        @param userId:
        @param idCard:
        @param idCard: 卡号
        @param userName: 用户名
        @return:
        """
        selectSql = f"""
        SELECT userName FROM user_list WHERE userName='{userName}'
        """
        res = self.SqlSelectByOneOrList(selectSql)

        if res.get('status') == 200:
            Sql = f"""
              UPDATE user_list SET idCard='{idCard}',idCardRegisterTime=now() WHERE userName='{userName}'
              """
        elif res.get('status') == 13204:
            Sql = f"""
                      INSERT INTO user_list (
                                userName,
                              idCard, 
                                userId,
                              idCardRegisterTime,
                              idCardStatus,
                              status,
                              type)
                                 VALUES
                                 ( '{userName}','{idCard}', {userId},now(),'正常','正常',{0});
                  """
        else:
            return res
        return self.insertOrUpdateOrDeleteBySql(sql=Sql)

    def insertUserByUserIdAndFaceId(self, userId, faceId, userName):
        """
        1.先根据用户ID查询，如果数据库中已经存在，就更新当前的人脸ID
        2.如果不存在该用户的ID，则就新增该数据
        @param userId:用户唯一ID
        @param faceId: 用户脸部特征
        @param userName: 用户名
        @return:
        """
        selectSql = f"""
        SELECT userId FROM user_list WHERE userId={userId}
        """
        res = self.SqlSelectByOneOrList(selectSql)
        if res.get('status') == 200:
            Sql = f"""
            UPDATE user_list SET faceId={faceId},faceRegisterTime=now() WHERE userId={userId}
            """
        elif res.get('status') == 13204:
            Sql = f"""
                INSERT INTO user_list (
                        userId, 
                        faceId,
                        userName,
                        faceRegisterTime,
                        faceStatus,
                        status,
                        type)
                           VALUES
                           ( {userId}, {faceId},'{userName}',now(),'正常','正常',{0});
            """
        else:
            return res
        return self.insertOrUpdateOrDeleteBySql(sql=Sql)

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
            print(f"初始化V3数据库失败：{e}")

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
                index = cur.description
                _result = []
                if len(rows) != 0:
                    for row in rows:
                        res = {}
                        for i in range(len(index)):
                            res[index[i][0]] = row[i]
                        _result.append(res)
                    _sqlRes.update(status=200, msg='获取成功', result=_result[0] if type == 0 else _result)
                else:
                    _sqlRes.update(status=13204, msg='无数据')
            else:
                _sqlRes.update(status=status, msg='操作失败')
        except Exception as e:
            print(e)
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes
