#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

import yagmail

from config import MAIL_HOST
from config import MAIL_PORT
from config import MAIL_USER
from config import MAIL_PASS
from config import MAIL_DEBUG

def send_mail(to_list, subject, body, attachments):

    # 连接邮箱服务器
    yag = yagmail.SMTP(user=MAIL_USER, password=MAIL_PASS,
                       host=MAIL_HOST, port=MAIL_PORT,
                       smtp_ssl=False,
                       smtp_starttls=False,
                       smtp_set_debuglevel=MAIL_DEBUG)

    if attachments is None:
        # 发送邮件
        yag.send(to_list, subject, contents=body)
    else:
        # 发送邮件
        yag.send(to_list, subject, contents=body, attachments=attachments)

    yag.close()

if __name__ == '__main__':
    to_list = ["xxxx@qq.com"]
    sub = "测试邮件"

    # 邮件正文
    body = "你好！这是最近工作的文件，请查收。"
    # 附件
    attachments = None

    try:
        send_mail(to_list, sub, body, attachments)
        print("send mail success")
    except Exception as e:
        print("send mail failure")
