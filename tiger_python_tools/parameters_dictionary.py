import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from config import ServerParameters
import tornado.ioloop
import tornado.web

from tornado import gen
import json

import datetime
import tigerfunctools
from dateutil import parser
from tornado.escape import utf8, _unicode

import logging
import dictionary_data
import dictionarytype_data


class AllDictionaryHandler(tornado.web.RequestHandler):
    async def post(self):
        self.write(tigerfunctools.WebApiResultJson(0,"成功",json.dumps(dts,cls=tigerfunctools.CJsonEncoder,ensure_ascii=False)))
        pass

class DictionaryTypeHandler(tornado.web.RequestHandler):
    async def post(self):
        inputdict = dict((k, v[-1].decode("utf-8")) for k, v in self.request.arguments.items())
        s=inputdict.get("typename",None)
        if s==None:
            self.write(tigerfunctools.WebApiResultJson(1,"查询参数不对",None))
            return
        d=dts.get(s,None)
        d=d.dictionary
        if d==None:
            self.write(tigerfunctools.WebApiResultJson(1,"无对应字典类型",None))
            return
        self.write(tigerfunctools.WebApiResultJson(0,"成功",json.dumps(d,cls=tigerfunctools.CJsonEncoder,ensure_ascii=False)))
        return

class DictionaryHandler(tornado.web.RequestHandler):
    async def post(self):
        inputdict=dict((k,v[-1].decode("utf-8")) for k,v in self.request.arguments.items())
        ts=inputdict.get("typename",None)
        s=inputdict.get("itemname",None)
        if s==None:
            self.write(tigerfunctools.WebApiResultJson(1,"查询参数不对",None))
            return



class DictionaryHandler(tornado.web.RequestHandler):
    async def post(self):
        pass


looptimecounter = 0

dts = dict()
dtis = dict()


async def loadfromdatabase():
    global dts
    global dtis
    async with ServerParameters.mysqlengine.acquire() as conn:
        await conn.connection.ping()
        table = dictionarytype_data.getsqlalchemytable()
        s = table.select().order_by(sqlalchemy.text(" dictionarytype_name "))

        resultproxy = await conn.execute(s)
        rows = await resultproxy.fetchall()
        dts.clear()
        dtis.clear()

        for r in rows:
            r=dict(r)
            r["dictionary"]=[]
            dts[r["dictionarytype_name"]] = r
            dtis[str(r["dictionarytype_typeid"])]=r

        table = dictionary_data.getsqlalchemytable()
        s = table.select().order_by(sqlalchemy.text(" dictionary_typeid ")).order_by(
            sqlalchemy.text(" dictionary_orderindex "))
        resultproxy = await conn.execute(s)
        rows = await resultproxy.fetchall()
        for r in rows:
            r=dict(r)
            v=dtis.get(str(r["dictionary_typeid"]),None)
            if v!=None:
                v2=[]
                v["dictionary"].append(r)
    pass


async def myloop():  # 循环协程
    global looptimecounter
    if (looptimecounter % 600 == 0):
        await loadfromdatabase()
    looptimecounter = looptimecounter + 1
