import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from config import ServerParameters
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import dictionarytype_data
import datetime
import tigerfunctools
from dateutil import parser
from tornado.escape import utf8, _unicode



class dictionarytype_view_Handler(tornado.web.RequestHandler):
	async def get(self):
		self.write("dictionarytype view api start %s	 "%ServerParameters.servercounter)
		await asyncio.sleep(2)
		self.write("end %s"%ServerParameters.servercounter)
		self.flush()

	async def post(self):
		inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
		if (inputdict["posttype"] == b"query"):
			await self.PostDoQuery(inputdict)
		elif (inputdict["posttype"] == b"update"):
			await self.PostDoUpdate(inputdict)
		elif (inputdict["posttype"] == b"insert"):
			await self.PostDoInsert(inputdict)
		elif (inputdict["posttype"] == b"delete"):
			await self.PostDoDelete(inputdict)

	async def PostDoQuery(self, inputdict):
		draw = inputdict["draw"].decode("utf-8")
		start = inputdict["start"].decode("utf-8")
		length = inputdict["length"].decode("utf-8")
		#排序字段
		orderfieldname=None
		orderflag=""
		if "order[0][column]" in inputdict.keys():
			orderfieldid=int(inputdict["order[0][column]"].decode("utf-8"))
			if (orderfieldid>=0):
				orderfieldname=inputdict["columns["+str(orderfieldid)+"][data]"].decode("utf-8")

		if "order[0][dir]" in inputdict.keys():
			orderflag=inputdict["order[0][dir]"].decode("utf-8")
		if (orderflag!="desc"):
		orderflag=""

		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionarytype_data.getsqlalchemytable()
			# 添加查询条件
			s1= tbl.select()
			s2= sqlalchemy.select([func.count(tbl.c.dictionarytype_id).label('totalcount')])

			
			resultproxy = await conn.execute(s2)
			row = await resultproxy.first()
			rowcount = row.totalcount

			if (orderfieldname!=None):
				s1=s1.order_by(sqlalchemy.text(" "+orderfieldname+" "+orderflag+" "))
			
			resultproxy = await conn.execute(s1.limit(int(length)).offset(int(start)))
			rows = await resultproxy.fetchall()
			data = [dict(r) for r in rows]

			result = {}
			result["draw"] = int(draw)
			result["recordsTotal"] = rowcount
			result["recordsFiltered"] = rowcount
			result["data"] = data

			sss = json.dumps(result, cls=tigerfunctools.CJsonEncoder, ensure_ascii=False)
			self.write(sss)

	async def PostDoUpdate(self, inputdict):
		dictionarytype_id = int(inputdict["updaterowdata[dictionarytype_id]"])
		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionarytype_data.getsqlalchemytable()
			s=tbl.update().where(tbl.c.dictionarytype_id==dictionarytype_id)

			if ("updaterowdata[dictionarytype_name]" in inputdict.keys()):

				s=s.values(dictionarytype_name=inputdict["updaterowdata[dictionarytype_name]"].decode("utf-8"))

			if ("updaterowdata[dictionarytype_description]" in inputdict.keys()):

				s=s.values(dictionarytype_description=inputdict["updaterowdata[dictionarytype_description]"].decode("utf-8"))

			if ("updaterowdata[dictionarytype_typeid]" in inputdict.keys()):

				s=s.values(dictionarytype_typeid=int(inputdict["updaterowdata[dictionarytype_typeid]"].decode("utf-8")))

			if ("updaterowdata[dictionarytype_updatetime]" in inputdict.keys()):

				s=s.values(dictionarytype_updatetime=parser.parse(inputdict["updaterowdata[dictionarytype_updatetime]"].decode("utf-8")))

			trans = await conn.begin()
			result = await conn.execute(s)
			await trans.commit()
			#print(result.rowcount)


	async def PostDoInsert(self, inputdict):
		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionarytype_data.getsqlalchemytable()
			s=tbl.insert()


			if ("updaterowdata[dictionarytype_name]" in inputdict.keys()):

				s=s.values(dictionarytype_name = inputdict["updaterowdata[dictionarytype_name]"].decode("utf-8"))

			if ("updaterowdata[dictionarytype_description]" in inputdict.keys()):

				s=s.values(dictionarytype_description = inputdict["updaterowdata[dictionarytype_description]"].decode("utf-8"))

			if ("updaterowdata[dictionarytype_typeid]" in inputdict.keys()):

				s=s.values(dictionarytype_typeid = int(inputdict["updaterowdata[dictionarytype_typeid]"].decode("utf-8"))) 

			if ("updaterowdata[dictionarytype_updatetime]" in inputdict.keys()):

				s=s.values(dictionarytype_updatetime = parser.parse(inputdict["updaterowdata[dictionarytype_updatetime]"].decode("utf-8"))) #datetime.datetime.strptime(dict["updaterowdata[dictionarytype_updatetime]"].decode("utf-8").replace(' ',''),'%m/%d/%Y')


			trans = await conn.begin()
			result = await conn.execute(s)
			await trans.commit()
			#print(result.rowcount)


	async def PostDoDelete(self, inputdict):
		dictionarytype_id = int(inputdict["updaterowdata[dictionarytype_id]"])
		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionarytype_data.getsqlalchemytable()
			s=tbl.delete().where(tbl.c.dictionarytype_id==dictionarytype_id)
		
			trans = await conn.begin()
			result = await conn.execute(s)
			await trans.commit()
			#print(result.rowcount)


