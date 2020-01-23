import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from config import ServerParameters
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import dictionary_data
import datetime
import tigerfunctools
from dateutil import parser
from tornado.escape import utf8, _unicode



class dictionary_view_Handler(tornado.web.RequestHandler):
	async def get(self):
		self.write("dictionary view api start %s	 "%ServerParameters.servercounter)
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
			tbl=dictionary_data.getsqlalchemytable()
			# 添加查询条件
			s1= tbl.select()
			s2= sqlalchemy.select([func.count(tbl.c.dictionary_id).label('totalcount')])

			
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
		dictionary_id = int(inputdict["updaterowdata[dictionary_id]"])
		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionary_data.getsqlalchemytable()
			s=tbl.update().where(tbl.c.dictionary_id==dictionary_id)

			if ("updaterowdata[dictionary_typeid]" in inputdict.keys()):

				s=s.values(dictionary_typeid=int(inputdict["updaterowdata[dictionary_typeid]"].decode("utf-8")))

			if ("updaterowdata[dictionary_name]" in inputdict.keys()):

				s=s.values(dictionary_name=inputdict["updaterowdata[dictionary_name]"].decode("utf-8"))

			if ("updaterowdata[dictionary_code]" in inputdict.keys()):

				s=s.values(dictionary_code=inputdict["updaterowdata[dictionary_code]"].decode("utf-8"))

			if ("updaterowdata[dictionary_description]" in inputdict.keys()):

				s=s.values(dictionary_description=inputdict["updaterowdata[dictionary_description]"].decode("utf-8"))

			if ("updaterowdata[dictionary_orderindex]" in inputdict.keys()):

				s=s.values(dictionary_orderindex=int(inputdict["updaterowdata[dictionary_orderindex]"].decode("utf-8")))

			if ("updaterowdata[dictionary_typeval]" in inputdict.keys()):

				s=s.values(dictionary_typeval=inputdict["updaterowdata[dictionary_typeval]"].decode("utf-8"))

			if ("updaterowdata[dictionary_updatetime]" in inputdict.keys()):

				s=s.values(dictionary_updatetime=parser.parse(inputdict["updaterowdata[dictionary_updatetime]"].decode("utf-8")))

			trans = await conn.begin()
			result = await conn.execute(s)
			await trans.commit()
			#print(result.rowcount)


	async def PostDoInsert(self, inputdict):
		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionary_data.getsqlalchemytable()
			s=tbl.insert()


			if ("updaterowdata[dictionary_typeid]" in inputdict.keys()):

				s=s.values(dictionary_typeid = int(inputdict["updaterowdata[dictionary_typeid]"].decode("utf-8"))) 

			if ("updaterowdata[dictionary_name]" in inputdict.keys()):

				s=s.values(dictionary_name = inputdict["updaterowdata[dictionary_name]"].decode("utf-8"))

			if ("updaterowdata[dictionary_code]" in inputdict.keys()):

				s=s.values(dictionary_code = inputdict["updaterowdata[dictionary_code]"].decode("utf-8"))

			if ("updaterowdata[dictionary_description]" in inputdict.keys()):

				s=s.values(dictionary_description = inputdict["updaterowdata[dictionary_description]"].decode("utf-8"))

			if ("updaterowdata[dictionary_orderindex]" in inputdict.keys()):

				s=s.values(dictionary_orderindex = int(inputdict["updaterowdata[dictionary_orderindex]"].decode("utf-8"))) 

			if ("updaterowdata[dictionary_typeval]" in inputdict.keys()):

				s=s.values(dictionary_typeval = inputdict["updaterowdata[dictionary_typeval]"].decode("utf-8"))

			if ("updaterowdata[dictionary_updatetime]" in inputdict.keys()):

				s=s.values(dictionary_updatetime = parser.parse(inputdict["updaterowdata[dictionary_updatetime]"].decode("utf-8"))) #datetime.datetime.strptime(dict["updaterowdata[dictionary_updatetime]"].decode("utf-8").replace(' ',''),'%m/%d/%Y')


			trans = await conn.begin()
			result = await conn.execute(s)
			await trans.commit()
			#print(result.rowcount)


	async def PostDoDelete(self, inputdict):
		dictionary_id = int(inputdict["updaterowdata[dictionary_id]"])
		async with ServerParameters.mysqlengine.acquire() as conn:
			await conn.connection.ping()
			tbl=dictionary_data.getsqlalchemytable()
			s=tbl.delete().where(tbl.c.dictionary_id==dictionary_id)
		
			trans = await conn.begin()
			result = await conn.execute(s)
			await trans.commit()
			#print(result.rowcount)


