#!/usr/bin/python
# coding=utf-8

__author__ = 'testerzhang'

from sqlalchemy import Column, String, Integer, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_NAME

# 创建对象的基类:
Base = declarative_base()


# 定义对象:
class FundDays(Base):
    # 指定本类映射到users表
    __tablename__ = 'fund_days'
    id = Column(Integer, primary_key=True, autoincrement=True)

    fund_code = Column(String(20))
    fund_name = Column(String(10))
    jz_date = Column(String(10))
    jz = Column(String(10))
    gsz = Column(String(10))
    gsz_date = Column(String(10))
    gsz_time = Column(String(10), nullable=False)
    zhang_die = Column(String(10))

    UniqueConstraint('fund_code', 'gsz_time', name='idx_code_time')


class FundEveryDay(Base):
    # 指定本类映射到users表
    __tablename__ = 'fund_every_day'
    id = Column(Integer, primary_key=True, autoincrement=True)

    fund_code = Column(String(20))
    fund_name = Column(String(10))
    jz_date = Column(String(10))
    jz = Column(String(10))
    gsz = Column(String(10))
    gsz_date = Column(String(10))
    gsz_time = Column(String(10), nullable=False)
    zhang_die = Column(String(10))

    UniqueConstraint('fund_code', 'gsz_time', name='idx_code_time')


class DBAPI(object):
    def __init__(self):
        # 初始化数据库连接:
        self.engine = create_engine(f'sqlite:///{DB_NAME}', echo=True)

        # engine是2.2中创建的连接
        Session = sessionmaker(bind=self.engine)

        # 创建Session类实例
        self.session = Session()

    def create(self):
        Base.metadata.create_all(self.engine)

    def drop(self):
        Base.metadata.drop_all(self.engine)

    def getsession(self):
        return self.session

    def add(self, record):
        # 将该实例插入到表
        self.session.add(record)

        # 当前更改只是在session中，需要使用commit确认更改才会写入数据库
        self.session.commit()

    def query(self, table, fund_code):
        result = self.session.query(table).filter_by(fund_code=fund_code).first()

        return result

    def delete(self, record):
        # 将ed用户记录删除
        self.session.delete(record)

        # 确认删除
        self.session.commit()


def create_table():
    dbapi = DBAPI()
    dbapi.create()


def drop_table():
    dbapi = DBAPI()
    dbapi.drop()


def main():
    # drop_table()
    create_table()


if __name__ == '__main__':
    main()
