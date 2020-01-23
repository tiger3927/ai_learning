import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from config import ServerParameters
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import vehicle_data
import datetime
import tigerfunctools
from dateutil import parser
from tornado.escape import utf8, _unicode
import asyncio
import vehicle_data
import config
import xlrd

#测试在mysql上做些操作,读取excel内容更新数据库

async def testsql():
    async with ServerParameters.mysqlengine.acquire() as conn:
        await conn.connection.ping()
        tbl = vehicle_data.getsqlalchemytable()
        # 添加查询条件
        s1 = tbl.select()
        s2 = sqlalchemy.select([func.count(tbl.c.vehicleid).label('totalcount')])

        resultproxy = await conn.execute(s2)
        row = await resultproxy.first()
        rowcount = row.totalcount
        print("Vehicle Count : ",rowcount)

        xls=xlrd.open_workbook("C:\\Users\\tiger\\Desktop\\呼我出行重庆公司AI设备安装表1111.xls")
        datasheet = xls.sheet_by_index(0)
        rowcount = datasheet.nrows
        for x in range(2,rowcount):
            vincode=datasheet.cell(x,2).value
            vnumber=datasheet.cell(x,3).value
            imei=datasheet.cell(x,7).value
            imei=imei[5:]

            print(vincode,vnumber,imei)

            a="goldh"
            b="autorec_a_"+imei[:8]
            c=imei[-7:]

            print(a,b,c)

            s1=tbl.select().where(tbl.c.vehiclegps_manufacturer == a).where(tbl.c.vehiclegps_model == b).where(tbl.c.vehiclegps_deviceid == c)
            resultproxy = await conn.execute(s1)
            rows = await resultproxy.fetchall()
            data = [dict(r) for r in rows]
            print(data)
            await conn.connection.ping()

            bbb=0
            for d in data:
                vindex=int(d["vehicleid"])
                if (bbb==0):
                    bbb=1
                    s = tbl.update().where(tbl.c.vehicleid == vindex)
                    s = s.values(vehiclenumber=vnumber).values(vehiclevincode=vincode)
                    trans=await conn.begin()
                    result = await conn.execute(s)
                    await trans.commit()
                else:
                    s = tbl.delete().where(tbl.c.vehicleid == vindex)
                    trans=await conn.begin()
                    result = await conn.execute(s)
                    await trans.commit()

            print(result.rowcount)


    pass

if __name__ == '__main__':

    ServerParameters.asyncioloop = asyncio.get_event_loop()
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.InitServer())
    print(config.datafilepath())
    ServerParameters.asyncioloop.run_until_complete(testsql())
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.DropServer())
    print("over")