#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

import copy
import sqlite3 as sl
import traceback

import arrow
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from config import DB_NAME
from config import MAILTO_LIST
from config import MONITOR_DOWN_VALUE
from config import MONITOR_UP_VALUE
from emailapi import send_mail

logger.add('fund_monitor.log')


class Fund(object):
    def __init__(self):
        self.email_templatename = "fund_monitor_tmpl.html"
        self.output_htmlname = "fund_monitor.html"

        self.monitor_up_value = MONITOR_UP_VALUE
        self.monitor_down_value = MONITOR_DOWN_VALUE

        self.title = '基金数据告警报告'
        self.to_list = MAILTO_LIST

        self.db = DB_NAME

        self.con = sl.connect(self.db)

    # 基金开放时间判断
    def limit_time(self):
        now_time = arrow.now()

        # format_sec_time = now_time.format("YYYY-MM-DD HH:mm:ss")
        week = int(now_time.format("d"))
        hour = int(now_time.format("HH"))
        min = int(now_time.format("mm"))

        if week == 0 or week == 6:
            logger.debug(f"基金周末不开放，退出")
            return True

        if hour < 9 or (hour == 11 and min > 30) or (12 <= hour < 13):
            logger.debug(f"基金未到开放时间，退出")
            return True

        if hour > 15 or (hour == 15 and min > 5):
            logger.debug(f"基金今天结束了")
            return True

        return False

    # 生成HTML数据
    def gen_html_file(self, filename, title, content):
        s = ['<HTML>']
        s.append(f'<HEAD><TITLE>{title}</TITLE><meta charset="UTF-8"></HEAD>')
        s.append('<BODY>')
        s.append(content)
        s.append('</BODY></HTML>')
        html = ''.join(s)

        html_file = open(filename, 'w')
        html_file.write(html)
        html_file.close()

    # 生成HTML文件
    def output_email_html(self, fund_lists):

        new_fund_lists = copy.deepcopy(fund_lists)

        try:
            env = Environment(loader=FileSystemLoader('./'))  # 加载模板
            template = env.get_template(self.email_templatename)

            html_content = template.render(fund_lists=new_fund_lists)
        except:
            logger.error(traceback.print_exc())
            html_content = ""

        return html_content

    # 发送邮件
    def email_notify(self):
        logger.debug(f"发送邮件")
        is_success = False

        now_time = arrow.now()
        today = now_time.format("YYYY-MM-DD")

        sub = f"{today}{self.title}"

        # 邮件正文
        body = ""
        with open(self.output_htmlname) as f:
            for line in f.readlines():
                line = line.strip('\n')
                body = f"{body}{line}"

        body = body.replace("\n", "")

        attachments = None

        try:
            send_mail(self.to_list, sub, body, attachments)
            logger.debug("send mail success")
            is_success = True
        except:
            logger.error(traceback.print_exc())

        return is_success

    # 获取基金数据，并发送告警
    def fetch_fund_records(self):
        if self.limit_time():
            return

        now_time = arrow.now()
        today = now_time.format("YYYY-MM-DD")
        # today = '2020-09-16'

        sql = f'''SELECT fund_code,fund_name,gsz,jz,zhang_die,gsz_time,id
        FROM fund_every_day
        where 
            gsz_date = '{today}'
            and 
        (
                ( (zhang_die + 0) <0  and  (zhang_die +0) < {self.monitor_down_value})
                or
                ( (zhang_die + 0) >0  and  (zhang_die +0) > {self.monitor_up_value})
        )
        '''

        logger.debug(f"sql=[{sql}]")

        monitor_list = []
        with self.con:
            data = self.con.execute(sql)
            for row in data:
                row_dict = {}
                # print(row)
                row_dict['fund_code'] = row[0]
                row_dict['fund_name'] = row[1]
                row_dict['gsz'] = row[2]
                row_dict['jz'] = row[3]
                row_dict['zhang_die'] = row[4]
                row_dict['gsz_time'] = row[5]

                monitor_list.append(row_dict)

        logger.debug(f'monitor_list={monitor_list}')

        if len(monitor_list) != 0:
            html_content = self.output_email_html(monitor_list)
            # print(html_content)

            if len(html_content) != 0:
                filename = self.output_htmlname
                self.gen_html_file(filename, self.title, html_content)
                self.email_notify()


def main():
    fund = Fund()
    fund.fetch_fund_records()


if __name__ == '__main__':
    main()
