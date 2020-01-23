import json
import datetime
import decimal
import os

import logging
from logging.handlers import TimedRotatingFileHandler

from cmreslogging.handlers import CMRESHandler  # elk日志插件

import asyncio
import sqlalchemy
from aiomysql.sa import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
import datetime
import uuid
import asyncpg


class ServerParameters:
    # 初始化配置项目
    mysqlhost = "a10.4s188.com"
    mysqlport = 35106
    mysqluser = 'root'
    mysqlpassword = 'tongji12'
    mysqldb = "jt808"

    pg_host = "factory.goldhonor.com"
    pg_port = 15432
    pg_user = "postgres"
    pg_password = "tongji12"
    pg_database = "goldhonor"

    filespath = "files/"

    mongodbpath = "mongodb://admin:tongji12@a10.4s188.com:35117"

    redishost = "a10.4s188.com"
    redisport = 35179
    redisuser = None
    redispassword = None

    rabbitmqhost = "a10.4s188.com"
    rabbitmqport = 35132
    rabbitmquser = "guest"
    rabbitmqpassword = "guest"

    elkhost = "a10.4s188.com"
    elkport = 9200
    elkuser = "guest"
    elkpassword = "guest"
    elkdatabase = ""

    myserverguid = None

    myservertype = None

    mydatapath = "data/"

    servercounter = 0

    mysqlconnectpool = None
    mysqlengine = None

    tornadoinstance = None
    asyncioloop = None
    BaseMySql = declarative_base()  # 生成orm基类,几乎没用

    @classmethod
    async def saveconfig(cls):

        filename = cls.mydatapath + cls.myservertype + "_serverconfig.json"

        out = dict()

        out["mysqlhost"] = cls.mysqlhost
        out["mysqlport"] = cls.mysqlport
        out["mysqluser"] = cls.mysqluser
        out["mysqlpassword"] = cls.mysqlpassword
        out["mysqldb"] = cls.mysqldb

        out["pg_host"] = cls.pg_host
        out["pg_port"] = cls.pg_port
        out["pg_user"] = cls.pg_user
        out["pg_password"] = cls.pg_password
        out["pg_database"] = cls.pg_database

        out["filespath"] = cls.filespath

        out["mongodbpath"] = cls.mongodbpath

        out["redishost"] = cls.redishost
        out["redisport"] = cls.redisport
        out["redisuser"] = cls.redisuser
        out["redispassword"] = cls.redispassword

        out["rabbitmqhost"] = cls.rabbitmqhost
        out["rabbitmqport"] = cls.rabbitmqport
        out["rabbitmquser"] = cls.rabbitmquser
        out["rabbitmqpassword"] = cls.rabbitmqpassword

        out["elkhost"] = cls.elkhost
        out["elkport"] = cls.elkport
        out["elkuser"] = cls.elkuser
        out["elkpassword"] = cls.elkpassword
        out["elkdatabase"] = cls.elkdatabase

        out["myserverguid"] = cls.myserverguid

        # 保存配置 json 文件
        f = open(filename, "w")
        s = json.dumps(out)
        f.write(s)
        f.close()

    @classmethod
    async def loadconfig(cls):
        filename = cls.mydatapath + cls.myservertype + "_serverconfig.json"
        if os.path.exists(filename) == True:  # 有就加载
            f = open(filename, "r")
            s = f.read()
            f.close()
            v = json.loads(s)

            cls.mysqlhost = v.get("mysqlhost", cls.mysqlhost)
            cls.mysqlport = v.get("mysqlport", cls.mysqlport)
            cls.mysqluser = v.get("mysqluser", cls.mysqluser)
            cls.mysqlpassword = v.get("mysqlpassword", cls.mysqlpassword)
            cls.mysqldb = v.get("mysqldb", cls.mysqldb)

            cls.pg_host = v.get("pg_host", cls.pg_host)
            cls.pg_port = v.get("pg_port", cls.pg_port)
            cls.pg_user = v.get("pg_user", cls.pg_user)
            cls.pg_password = v.get("pg_password", cls.pg_password)
            cls.pg_database = v.get("pg_database", cls.pg_database)

            cls.filespath = v.get("filespath", cls.filespath)

            cls.mongodbpath = v.get("mongodbpath", cls.mongodbpath)

            cls.redishost = v.get("redishost", cls.redishost)
            cls.redisport = v.get("redisport", cls.redisport)
            cls.redisuser = v.get("redisuser", cls.redisuser)
            cls.redispassword = v.get("redispassword", cls.redispassword)

            cls.rabbitmqhost = v.get("rabbitmqhost", cls.rabbitmqhost)
            cls.rabbitmqport = v.get("rabbitmqport", cls.rabbitmqport)
            cls.rabbitmquser = v.get("rabbitmquser", cls.rabbitmquser)
            cls.rabbitmqpassword = v.get(
                "rabbitmqpassword", cls.rabbitmqpassword)

            cls.elkhost = v.get("elkhost", cls.elkhost)
            cls.elkport = v.get("elkport", cls.elkport)
            cls.elkuser = v.get("elkuser", cls.elkuser)
            cls.elkpassword = v.get("elkpassword", cls.elkpassword)
            cls.elkdatabase = v.get("elkdatabase", cls.elkdatabase)

            cls.myserverguid = v.get("myserverguid", None)

            logging.info("加载配置文件：" + json.dumps(v))

    @classmethod
    async def InitServer(cls, servertype="unkown-servertype", startmysql=True, startpg=True):

        # 创建日志目录
        if not os.path.exists('logs'):
            os.makedirs('logs')
        logging.basicConfig(level=logging.DEBUG)  # 默认屏幕输出
        filehandler = TimedRotatingFileHandler(  # 时间轮转输出
            filename="logs/my.log",
            when='D',
            interval=1,
            backupCount=0)
        filehandler.suffix = "%Y%m%d-%H%M%S.log"
        formatter = logging.Formatter(
            "%(asctime)s-%(name)s-%(levelname)s-[%(filename)s:%(lineno)d]-%(message)s")
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.INFO)

        logging.getLogger().addHandler(filehandler)  # 添加时间轮转输出

        # 服务器名字   数据文件路径
        cls.myservertype = servertype
        cls.mydatapath = datafilepath()
        # 生成一个新的 guid 可能不会使用，如果有的话
        newguid = cls.myservertype + "_" + str(uuid.uuid1())

        await cls.loadconfig()

        if (cls.elkdatabase == ""):
            cls.elkdatabase = cls.myservertype

        if (cls.myserverguid == None):
            cls.myserverguid = newguid
            # 没有配置文件就保存
            await cls.saveconfig()

        # ELK的日志输出
        es_handler = CMRESHandler(hosts=[{'host': cls.elkhost, 'port': cls.elkport}],
                                  auth_type=CMRESHandler.AuthType.NO_AUTH,
                                  es_index_name=cls.elkdatabase,
                                  es_additional_fields={'App': cls.myservertype, 'AppGuid': cls.myserverguid})
        es_handler.setLevel(logging.INFO)

        formatter2 = logging.Formatter(
            "%(asctime)s-%(name)s-%(levelname)s-[%(filename)s:%(lineno)d]-%(message)s")
        es_handler.setFormatter(formatter2)

        logging.getLogger().addHandler(es_handler)
        # 禁止如下两个模块乱打调试日志，因为ELK会把 debug 日志打在屏幕，有干扰
        logging.getLogger("elasticsearch").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        # 创建 mysql 的工厂
        if startmysql:
            cls.mysqlengine = await create_engine(user=cls.mysqluser,
                                                  password=cls.mysqlpassword,
                                                  host=cls.mysqlhost,
                                                  port=cls.mysqlport,
                                                  db=cls.mysqldb,
                                                  loop=cls.asyncioloop)
        if startpg:
            cls.pg_pool = await asyncpg.create_pool(user='postgres',
                                                password='tongji12',
                                                database='goldhonor', host='factory.goldhonor.com', port=15432,
                                                command_timeout=60)

        pass

    @classmethod
    async def DropServer(cls):
        cls.mysqlengine.close()
        await cls.mysqlengine.wait_closed()
        await cls.pg_pool.close()


# 检查本地数据目录是否存在
def datafilepath():
    currentpath = os.getcwd() + "/data/"  # 缺省
    if (os.path.exists("/myfile/") == True):
        currentpath = "/myfile/"
    return currentpath


if __name__ == "__main__":  # 用于测试
    ServerParameters.asyncioloop = asyncio.get_event_loop()
    ServerParameters.asyncioloop.run_until_complete(
        ServerParameters.InitServer(servertype="test"))

    print("数据文件目录 " + datafilepath())

    ServerParameters.asyncioloop.run_until_complete(
        ServerParameters.DropServer())
