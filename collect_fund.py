#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

import copy
import json
import random
import traceback

import arrow
import requests
from loguru import logger

from config import FUND_CODE_LIST
from dbapi import DBAPI
from dbapi import FundDays
from dbapi import FundEveryDay

logger.add('collect_fund.log')

# user_agent列表
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36'
]

# referer列表
REFERER_LIST = [
    'http://fund.eastmoney.com/110022.html',
    'http://fund.eastmoney.com/110023.html',
    'http://fund.eastmoney.com/110024.html',
    'http://fund.eastmoney.com/110025.html'
]


class Fund(object):
    def __init__(self):
        self.base_url = "http://fundgz.1234567.com.cn/js/"

        self.mydbapi = DBAPI()
        self.mydbapi.create()

    # 基金开放时间判断
    def limit_time(self, fund_code):
        now_time = arrow.now()

        # format_sec_time = now_time.format("YYYY-MM-DD HH:mm:ss")
        week = int(now_time.format("d"))
        hour = int(now_time.format("HH"))
        min = int(now_time.format("mm"))

        if week == 0 or week == 6:
            logger.debug(f"基金={fund_code}周末不开放，退出")
            return True

        if hour < 9 or (hour == 11 and min > 30) or (12 <= hour < 13):
            logger.debug(f"基金={fund_code}未到开放时间，退出")
            return True

        if hour > 15 or (hour == 15 and min > 5):
            logger.debug(f"基金={fund_code}今天结束了")
            return True

        return False

    def write_db(self, ys_dict):

        data_dict = copy.deepcopy(ys_dict)

        try:

            fund_code = data_dict.get('基金代码')
            fund_name = data_dict.get('基金名称')
            jz_date = data_dict.get('净值日期')
            jz = data_dict.get('单位净值')
            gsz_time = data_dict.get('估值时间')
            gsz = data_dict.get('估算值')
            zhang_die = data_dict.get('估算值涨跌')
            gsz_date = data_dict.get('估值日期')

            # print("没有符合的记录")
            record = FundDays(
                fund_code=fund_code, fund_name=fund_name,
                jz_date=jz_date, jz=jz,
                gsz_date=gsz_date, gsz=gsz,
                gsz_time=gsz_time, zhang_die=zhang_die
            )
            self.mydbapi.add(record)
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                pass
            else:
                logger.error(traceback.print_exc())

        try:

            fund_code = data_dict.get('基金代码')
            fund_name = data_dict.get('基金名称')
            jz_date = data_dict.get('净值日期')
            jz = data_dict.get('单位净值')
            gsz_time = data_dict.get('估值时间')
            gsz = data_dict.get('估算值')
            zhang_die = data_dict.get('估算值涨跌')
            gsz_date = data_dict.get('估值日期')

            result = self.mydbapi.query(FundEveryDay, fund_code)

            if result is not None:
                self.mydbapi.delete(result)

            # print("没有符合的记录")
            record = FundEveryDay(
                fund_code=fund_code, fund_name=fund_name,
                jz_date=jz_date, jz=jz,
                gsz_date=gsz_date, gsz=gsz,
                gsz_time=gsz_time, zhang_die=zhang_die
            )
            self.mydbapi.add(record)

        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                pass
            else:
                logger.error(traceback.print_exc())

    # 获取基金数据并入库
    def fetch_fund_data(self, fund_code):

        if self.limit_time(fund_code):
            return

        # 获取一个随机user_agent和Referer
        header = {'User-Agent': random.choice(USER_AGENT_LIST),
                  'Referer': random.choice(REFERER_LIST)
                  }

        url = f"{self.base_url}{str(fund_code)}.js"

        try:
            req = requests.get(url, timeout=3, headers=header)

            data = (req.content.decode()).replace("jsonpgz(", "").replace(");", "").replace("'", "\"")
            # logger.debug(len(data))
        except:
            logger.error(traceback.format_exc())
            data = ""

        if len(data) == 0:
            return

        data_dict = json.loads(data)

        logger.debug(f"data={data_dict}")

        new_data_dict = {}
        new_data_dict['基金代码'] = data_dict.get('fundcode')
        new_data_dict['基金名称'] = data_dict.get('name')
        new_data_dict['净值日期'] = data_dict.get('jzrq')
        new_data_dict['单位净值'] = data_dict.get('dwjz')
        new_data_dict['估算值'] = data_dict.get('gsz')
        new_data_dict['估算值涨跌'] = data_dict.get('gszzl')
        new_data_dict['估值时间'] = data_dict.get('gztime')
        new_data_dict['估值日期'] = data_dict.get('gztime').split(' ')[0]
        # logger.debug(type(new_data_dict['估值日期']))

        logger.debug(f"new_data_dict={new_data_dict}")

        self.write_db(new_data_dict)


def main():
    fund = Fund()

    for fund_code in FUND_CODE_LIST:
        fund.fetch_fund_data(fund_code)


if __name__ == '__main__':
    main()
