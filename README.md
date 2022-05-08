安装库文件
安装requirement.txt

pip install -r requirements.txt

生成requirement.txt

pip freeze > requirements.txt

python manage.py startapp filename

python manage.py runserver 13209

### 状态码说明

| status | 说明           |
| ------ | -------------- |
| 13201  | 登录密码错误   |
| 13202  | 用户被冻结     |
| 13203  | 服务器内部错误 |
| 13204  | 无数据         |
| 13205  | 已开通登录功能 |
| 13206  | 已存在用户     |
| 13207  | 参数错误       |
| 13208  | 接口错误       |

### 数据库操作

1. 根据rid查询表pat_test_checklist

   ```mysql
   SELECT ptc.*,sog.org_name FROM pat_test_checklist ptc LEFT JOIN sys_org sog ON ptc.org_code=sog.org_code WHERE RequisitionId='21101700011'
   ```

2. 根据用户userId查询资料

   ```
   SELECT fp.*,sog.org_name,su.sys_user_name FROM fh_personbasics fp LEFT JOIN sys_org sog ON fp.org_code=sog.org_code LEFT JOIN sys_user su ON su.user_id=fp.creator WHERE fp.userId=1015859774
   ```

   

3. 
