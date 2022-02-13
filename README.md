安装库文件
安装requirement.txt

pip install -r requirements.txt

生成requirement.txt

pip freeze > requirements.txt

python manage.py startapp filename

python manage.py runserver 13209

### api/V3请求

|    请求方式     | 方法 | 接口说明                                                     | 参数                                                         | 参数说明                                                     |
| :-------------: | ---- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
|  passUserTotal  | GET  | 查询访客总数                                                 | 无                                                           |                                                              |
|  passUserList   | GET  | 查询访客记录，返回list                                       | page，limit                                                  | 请求页数，默认50条数据                                       |
| passUserSearch  | GET  | 搜索                                                         | content                                                      | 查询关键字，支持用户名，用户Id及其关键字                     |
|   deleteUser    | GET  | 删除用户                                                     | userId                                                       | 用户Id                                                       |
|   verifyUser    | GET  | 验证用户是否存在                                             | userName                                                     | 用户名验证用户是否存在                                       |
|   enableUser    | GET  | 通过用户id启用                                               | userId                                                       | 用户id                                                       |
|   enableFace    | GET  | 通过用户id启用刷脸                                           | userId                                                       | 用户id                                                       |
|  enableIdCard   | GET  | 通过用户id启用刷卡                                           | userId                                                       | 用户id                                                       |
|   disableUser   | GET  | 通过用户禁用                                                 | userId                                                       | 用户id                                                       |
|   disableFace   | GET  | 通过用户id禁用刷脸                                           | userId                                                       | 用户id                                                       |
|  disableIdCard  | GET  | 通过用户id禁用刷卡                                           | userId                                                       | 用户id                                                       |
|   searchUser    | GET  | 通过用户名或者用户ID关键字查询                               | content                                                      | 搜索关键字                                                   |
|    userTotal    | GET  | 查询用户总数                                                 |                                                              |                                                              |
|    userList     | GET  | 查询登记的用户数据                                           | page，limit                                                  | 页码,条数                                                    |
|    addIdCard    | GET  | 1.先根据用户ID查询，如果数据库中已经存在，就更新当前的门卡ID 2.如果不存在该用户的ID，则就新增该数据 | userName,idCard                                              | 用户名，门卡号                                               |
|    addFaceId    | GET  | 1.先根据用户ID查询，如果数据库中已经存在，就更新当前的人脸ID 2.如果不存在该用户的ID，则就新增该数据 | userName，faceId                                             | 用户名，特征ID                                               |
|  verifyFaceId   | GET  | 通过faceId校验用户名                                         | faceId                                                       | 特征ID                                                       |
|    register     | GET  | 用户开通账号登录（**只有录入信息的用户才能开通**）           | {rg:username=用户名，account=登录账号，password=登录密码}    | **该接口需要SM4加密发送至服务器如：{rg:O5On9uPN624X8RnoYnBliw==}** |
| userDetailInfo  | GET  | 通过用户id查询详细信息                                       | userId                                                       | 用户信息                                                     |
|  uploadAvatar   | POST | 上传/修改头像                                                | userId，image                                                | 用户名，图片名称，注意：**仅限小程序使用**                   |
|     logout      | GET  | 用户注销账号                                                 | userId,userPassWord                                          | 用户id,密码                                                  |
|   passRecord    | GET  | 查询用户的通信记录                                           | **userId[必选]**，limit,page                                 | 用户id为必选参数，默认limit=30,page=1                        |
| updatePassword  | POST | 用户修改密码                                                 | userId，newPassWord，oldPassWord                             | 用户id，用户新密码与旧密码                                   |
|     addUser     | POST | 新增用户                                                     | userName, sex, birthday, contactNumber, [userAccount, userPassWord] |                                                              |
|  findPassWord   | POST | 找回密码                                                     | userName, userAccount, newUserPassword                       |                                                              |
|   sendVerCode   | GET  | 新增用户发送验证码                                           | phoneNum：string                                             |                                                              |
|  checkVerCode   | GET  | 校验验证码是否正确                                           | code,phoneNum                                                |                                                              |
|      isSms      | GET  | 检查是否开启短信验证                                         |                                                              |                                                              |
| todayPassTotal  | GET  | 获取当天访客总数                                             |                                                              |                                                              |
| todayPassWaring | GET  | 获取当天告警总数                                             |                                                              |                                                              |
|   getContent    | GET  | 获取留言                                                     | userId,limit=20,page=1                                       |                                                              |
|     addLike     | GET  | 点赞留言                                                     | userId,contentId                                             |                                                              |
|   cancelLike    | GET  | 取消点赞                                                     | 同上                                                         |                                                              |
|   addComment    | POST | 评论留言                                                     | userId,contentId,commentText                                 |                                                              |
| publishContent  | POST | 发布留言                                                     | userId,content                                               |                                                              |

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

