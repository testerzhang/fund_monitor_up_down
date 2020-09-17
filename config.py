#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

# 存储基金数据库
DB_NAME = "fund.db"

# 配置基金代码
FUND_CODE_LIST = [
    '000215'
]

#基金上涨阈值
MONITOR_UP_VALUE = 5
#基金下降阈值
MONITOR_DOWN_VALUE = -5


# 邮件配置
MAIL_HOST = ""  # smtp server
MAIL_PORT = 25
MAIL_USER = ""  # email sender
MAIL_PASS = ""  # email password
MAIL_DEBUG = 1

# 收件人邮箱
MAILTO_LIST = ["xxx@qq.com"]
