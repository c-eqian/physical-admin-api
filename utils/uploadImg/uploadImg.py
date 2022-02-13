# -*- coding: utf-8 -*-
# @Time    : 2022-01-26 18:46
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : uploadImg.py
# @Software: PyCharm

import oss2

import os


class Storage:
    """
    将采集的图像进行上传阿里云oss对象存储
    """

    def __init__(self):
        """
        阿里云三剑客
        """
        self.accessKeyId = "LTAI5tNSmVX22MiPb8QtZN6T"
        self.accessKeySecret = "VESu9qYX0dqqWR6MOBJZtv1fHMTmDQ"
        self.bucketName = "save0127"
        self.endPoint = "http://oss-cn-beijing.aliyuncs.com"
        self.auth = oss2.Auth(self.accessKeyId, self.accessKeySecret)
        self.bucket = oss2.Bucket(self.auth, self.endPoint, self.bucketName)

    def upload_one_img(self, userImgPath) ->dict:
        """
        当注册新用户时，根据注册的用户ID进行上传
        @param userId: 用户ID
        @return:
        """
        remoteName = f'userAvatar/'
        if os.path.exists(userImgPath):
            result = self.bucket.put_object_from_file(remoteName + os.path.basename(userImgPath), userImgPath)
            newUrl = self.bucket.sign_url('GET', remoteName + os.path.basename(userImgPath), 60 * 60 * 10 * 24)
            # 返回值为链接，参数依次为，方法/oss上文件路径/过期时间(s)
            print(result.status)
            if result.status == 200:
                return {"status": 200, "url": newUrl}
            else:
                return {"status": 13203}
        else:
            print(f'抱歉，无法找到相关文件')
            return {"status": 13203}

# a = Storage()
# a.get_img_one_path('100008')
