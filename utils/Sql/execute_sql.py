# -*- coding: utf-8 -*-
# @Time    : 2021-12-08 19:50
# @Author  : 十三
# @Email   : 2429120006@qq.com
# @File    : execute_sql.py
# @Software: PyCharm
from utils.Sql.base_sql import DataBase
from utils.crypto._MD5 import SM4Utils

"""
数据操作基类
"""


class executeDB:
    def __init__(self):
        self.db = DataBase()  # 实例化
        self.SM4 = SM4Utils()

    """
    根据体检条码查询基本体检详情
    身高、体重、体温、心率
    """

    def queryBasicPhysicalExamRes(self, Rid=None, mark=None) -> dict:
        """
        在不知道条码情况下，将根据个人序号查询
        """
        newRid = Rid
        res = {"status": 0, "msg": ''}  # 返回数据
        if not newRid:
            if not mark:
                res.update(status=1304, msg="个人序号有误")
                return res
            queryRid = self.db.getRidByPersonMark(mark)
            if queryRid.get('status') == 200:
                newRid = queryRid.get('result').get('RequisitionId')
            else:
                res.update(status=queryRid.get('status'), msg="无法为您查询到相关体检记录")
                return res
        try:
            GBPS = f"""
                    SELECT 
                            pc.Height,pc.Weight,pc.BMI,
                            pc.RequisitionId,pc.LSBP,pc.LDBP,pc.RSBP,pc.RDBP,pc.ProjectName,
                            pc.Status,pc.ReviewDoctor,CONVERT(pc.ReviewDate,CHAR(19)) ReviewDate
                            from pat_test_checklist pc 
                            WHERE 
                            pc.RequisitionId='{newRid}'
            
            """
            _RES = self.db.SqlSelectByOneOrList(GBPS)
            if _RES.get('status') == 200:
                res.update(status=200, msg='查询成功', result=_RES.get('result'))
            else:
                res.update(status=_RES.get("status"),
                           msg=_RES.get("msg"))
            return res
        except Exception as e:
            res.update(status=13203, msg='查询出错')
            print(f"queryBasicPhysicalExamRes:{e}")
            return res

    """
    根据条码及编码大类查询心电图
    """

    def getEcgDetails(self, RequisitionId: str, FeeItemCode: str):

        res = {"status": 0, "msg": ''}  # 返回数据
        try:
            _SqlGetEcg = f"""
                            SELECT 
                            pf.ECG_ExaminationsConlc,pf.ECG_ExaminationsFind,pf.ECG_Reportopter,
                            pf.RequisitionId,pf.FeeItemCode,
                            CONVERT(pf.ECG_ReportTime,CHAR(19)) 'ECG_ReportTime'
                            from pat_test_result pf 
                            WHERE 
                            pf.RequisitionId='{RequisitionId}' and pf.FeeItemCode='{FeeItemCode}'
                           """
            _RES = self.db.SqlSelectByOneOrList(_SqlGetEcg)
            if _RES.get("status") == 200:
                res.update(status=200, msg='查询成功', result=_RES.get('result'))
            else:
                res.update(status=_RES.get("status"),
                           msg=_RES.get("msg"))
            return res

        except Exception as e:
            res.update(status=13203, msg='查询出错')
            print(f"getUltrasoundDetails:{e}")
            return res

    """
    Ultrasound
    根据条码及编码大类查询腹部超声
    """

    def getAbdomenDetails(self, RequisitionId: str, FeeItemCode: str):

        res = {"status": 0, "msg": ''}  # 返回数据
        try:
            _SqlGetUltrasound = f"""
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
            _RES = self.db.SqlSelectByOneOrList(_SqlGetUltrasound)
            if _RES.get("status") == 200:
                res.update(status=200, msg='查询成功', result=_RES.get('result'))
            else:
                res.update(status=_RES.get("status"),
                           msg=_RES.get("msg"))
            return res

        except Exception as e:
            res.update(status=13203, msg='查询出错')
            print(f"getUltrasoundDetails:{e}")
            return res

    """
    根据条码及编码大类查询尿检细项
    """

    def getUrineTestDetailsByRidAndFic(self, Rid=None, Fic=None) -> dict:
        """
        :param Rid: 条码
        :param Fic: 体检编码大类
        :return:
        """
        res = {"status": 0, "msg": ''}  # 返回数据
        try:
            _SqlGetUrineTestItemListByClass = f"""
                SELECT 
                pf.ItemCode,pf.ItemName,pf.RequisitionId,pf.Lis_RangeState,pf.FeeItemCode,
                pf.Lis_Result,pf.Lis_ResultUnit,pf.Lis_RangeHighValue,pf.Lis_RangeLowValue,
                CONVERT(pf.ReceivedTime,CHAR(19)) 'ReceivedTime'
                from pat_test_result pf 
                WHERE 
                pf.RequisitionId='{Rid}' and pf.FeeItemCode='{Fic}'

               """
            _RES = self.db.SqlSelectByOneOrList(_SqlGetUrineTestItemListByClass)
            if _RES.get("status") == 200:
                res.update(status=200, msg='查询成功', result=_RES.get('result'))
            else:
                res.update(status=_RES.get("status"),
                           msg=_RES.get("msg"))
            return res
        except Exception as e:
            res.update(status=13203, msg='查询出错')
            print(f"getUrineTestItemListByRequisitionId:{e}")
            return res

    """
    根据体检条码查询尿检项目及基本项目
    """

    def getUrineTestItemListByRequisitionId(self, RequisitionId=None, mark=None) -> dict:
        """
        :param mark: 是否知道体检条码，如果没有传入条码，则根据个人序号进行取当前年最新一条条码记录
        :param RequisitionId: 体检条码
        :return:
        """
        res = {"status": 0, "msg": ''}  # 返回数据
        Rid = RequisitionId
        if Rid is None or not Rid:
            if mark is None or not mark:
                res.update(status=13204, msg="个人序号有误")
                return res
            queryRid = self.db.getRidByPersonMark(mark)
            if queryRid.get('status') == 200:
                Rid = queryRid.get('result').get('RequisitionId')
            else:
                res.update(status=queryRid.get('status'), msg="无法为您查询到相关体检记录")
                return res

        try:
            _SqlGetUrineTestItemList = f"""
               SELECT pf.RequisitionId,pf.BarCode,pf.ApplyDoctorName,
               pf.ApplyDoctorNo,pf.FeeItemCode,pf.FeeItemName,CONVERT(pf.ApplyDate,CHAR(19)) 'ApplyDate'
                from pat_test_form  pf WHERE pf.RequisitionId='{Rid}'
               """
            _SqlGetUrineTestItemListRes = self.db.SqlSelectByOneOrList(_SqlGetUrineTestItemList)
            if _SqlGetUrineTestItemListRes.get("status") == 200:
                data = _SqlGetUrineTestItemListRes.get('result')
                if not mark:
                    data.insert(0, {"RequisitionId": RequisitionId, "FeeItemName": "基本情况", "FeeItemCode": 0})
                res.update(status=200, msg='查询成功', result=data)
            else:
                res.update(status=_SqlGetUrineTestItemListRes.get("status"),
                           msg=_SqlGetUrineTestItemListRes.get("msg"))
            return res
        except Exception as e:
            res.update(status=13203, msg='查询出错')
            print(f"getUrineTestItemListByRequisitionId:{e}")
            return res

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
    #            SELECT pc.Height,pc.Weight,pc.BMI,pc.RDBP,pc.RSBP,pc.LDBP,pc.LSBP,pc.Temperature,
    #            pc.tcm_identifier,pc.ini_identifier,pc.test_identifier,
    #            pc.adl_identifier,pc.Status,CONVERT (pc.ReviewDate,CHAR (19)) 'ReviewDate',pc.ReviewDoctor
    #             from pat_test_checklist  pc WHERE pc.RequisitionId='{RequisitionId}'
    #            """
    #         _SqlGetBasicPhysicalDetailsRes = self.db.SqlSelectByOneOrList(_SqlGetBasicPhysicalDetails)
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

    """
    根据个人序号获取体检列表记录
    """

    def getPhysicalExamListSql(self, personMark: str, page: int, limitNum: int) -> dict:
        """
        :param personMark: 个人序号
        :param page: 分页获取
        :param limitNum: 每页条目
        :return:
        """
        res = {"status": 0, "msg": ''}  # 返回数据
        if page < 1:
            page = 1
        try:
            _SqlGetPhysicalExamList = f"""
               select c.RequisitionId,c.empi,c.org_code,c.ProjectName,c.ProjectNo,
               CONVERT(c.VisitingDate,CHAR(19)) 'VisitingDate',c.Operator
               from pat_test_checklist c where  empi='{personMark}'  order by c.Did desc 
               limit {(page - 1) * limitNum},{limitNum} 
               """
            _SqlGetPhysicalExamListRes = self.db.SqlSelectByOneOrList(_SqlGetPhysicalExamList)
            if _SqlGetPhysicalExamListRes.get('status') == 200:
                res.update(status=200, msg="获取成功", result=_SqlGetPhysicalExamListRes.get('result'))
            else:
                res.update(status=_SqlGetPhysicalExamListRes.get('status'), msg=_SqlGetPhysicalExamListRes.get('msg'))
            return res
        except Exception as e:
            print(f"getPhysicalExamListSql:{e}")
            res.update(status=13203, msg='获取出错')
            return res

    """
    登录验证函数
    """

    def LoginSql(self, u_name: str, pwd: str) -> dict:  # 登录验证
        """
        :param u_name: 账号
        :param pwd: 密码
        :return: 返回数据类型为json格式，status=200
                表示返回成功，13201表示账号存在，但密码不正确
                13204表示没该账号
                13203 异常错误
        """
        # De_crypto = self.SM4.decryptData_ECB(u_name)
        res = {"status": 0, "msg": ''}  # 返回数据
        EnString = self.SM4.encryptData_ECB(pwd)  # 加密密码
        try:
            SqlUserinfo = f"""
                       SELECT u.userAccount,u.name,u.userPassword,u.authority,u.status,u.relation,u.nickName,
                               fp.age,fp.org_name,fp.org_code,fp.gender,fp.userId
                       from 
                       userinfo u join fh_personbasics fp on u.relation = fp.id 
                        where u.userAccount='{u_name}' AND fp.status=0
                       """
            _res = self.db.SqlSelectByOneOrList(SqlUserinfo)
            if _res.get("status") == 200 and _res.get('result')[0].get("status") in [0, '0']:
                if _res.get('result')[0].get("password") == EnString:
                    result = _res.get('result')[0]
                    result.pop('password', None)  # 删除密码键值，注意：如果pop删除，key不存在会报错，可以设置不存在时返回的值
                    result.pop('status', None)
                    res.update(status=_res.get('status', 200), msg='验证通过', result=result)
                else:
                    res.update(status=13201, msg='密码错误')
            elif _res["status"] == 200 and _res.get('result')[0].get("status") in [1, '1']:
                res.update(status=13204, msg='账号已注销')
            elif _res.get('status') == 13204:
                res.update(status=_res.get('status', 13204), msg='账号不存在')
            else:
                res.update(status=_res.get('status', 13203), msg='未知错误')
            return res
        except Exception as e:
            res.update(status=13203, msg='抱歉，验证出错')
            print(e)
            return res

    """
    注册函数
    """

    def RegisterSql(self, pwd: str, nick: str, idCard: str) -> dict:  # 注册验证
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
               SELECT id,idcard,name from fh_personbasics where idcard='{idCardDe}'
               """
            _queryRes = self.db.SqlSelectByOneOrList(_queryIsExistByIdCard)
            RESULT = _queryRes.get("result")
            if _queryRes.get('status') == 200:  # 查询身份证成功
                _queryIsRegistered = f"""
                    SELECT a.idcard from fh_personbasics a 
                    join userinfo b on a.id = b.relation where a.idcard='{idCardDe}'
                   """
                _queryIsRegisteredRes = self.db.SqlSelectByOne(_queryIsRegistered)[0]
                if _queryIsRegisteredRes.get("status") == 200:  # 此时能查询到，说明已经注册过
                    res.update(status=13205, msg="已开通，无需重复")
                elif _queryIsRegisteredRes.get("status") == 13204:  # 此时没能查询到，说明未注册过，可以注册
                    if nick == '':
                        nick = RESULT.get('name')
                    _sqlInsertByRegister = """
                       INSERT INTO userinfo 
                       ( username,name, relation,password,nickName,status,authority,Isuse) 
                       VALUES ('{}','{}','{}','{}','{}','0',0,0
                       )

                       """.format(RESULT.get('idcard')[-8:], RESULT.get('name'), RESULT.get('id'), pwd, nick)
                    _res = self.db.SqlInsertOrUpdateByOne(_sqlInsertByRegister)
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
            print(e)
            res.update(status=13203, msg=e)
            return res

    def UpdateSql(self):  # 修改信息
        pass

    def DelSql(self):  # 注销账号
        pass
