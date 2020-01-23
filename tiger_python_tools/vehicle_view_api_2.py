import asyncpg
from config import ServerParameters
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import datetime
import asyncio
import tigerfunctools
from dateutil import parser
from tornado.escape import utf8, _unicode
import asyncio


class vehicle_view_Handler(tornado.web.RequestHandler):
	async def get(self):
		self.write("vehicle view api start %s	 "%ServerParameters.servercounter)
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

		async with ServerParameters.pg_pool.acquire() as conn:
			selectstr="select * from vehicle "
			countstr="select count(*) from vehicle "
			orderstr= ""
			if (orderfieldname!=None):
				orderstr= " order by {0} {1}".format(orderfieldname,orderflag)
			wherestr=" where (1=1) "

			fcount=1
			flist=[]

			searchval_vehiclenumber=inputdict["searchval_vehiclenumber"].decode("utf-8")
			if (len(searchval_vehiclenumber) > 0):

				wherestr=wherestr+ " and (vehiclenumber like ${0})".format(fcount)
				flist.append("%"+searchval_vehiclenumber+"%")
				fcount+=1

			searchval_vehicledrivingpermit_inittime=inputdict["searchval_vehicledrivingpermit_inittime"].decode("utf-8")
			if (len(searchval_vehicledrivingpermit_inittime) > 0):

				sss = searchval_vehicledrivingpermit_inittime.split(' - ')
				searchval_vehicledrivingpermit_inittime_start = parser.parse(sss[0])#datetime.datetime.strptime(sss[0], '%Y-%m-%d %H:%M:%S.%f')
				searchval_vehicledrivingpermit_inittime_end = parser.parse(sss[1])#datetime.datetime.strptime(sss[1], '%Y-%m-%d %H:%M:%S.%f')
				wherestr = wherestr + " and (vehicledrivingpermit_inittime between ${0}::timestamp and ${1}::timestamp )".format(fcount,fcount+1)
				flist.append(searchval_vehicledrivingpermit_inittime_start)
				flist.append(searchval_vehicledrivingpermit_inittime_end)
				fcount+=2

			searchval_vehicleowner_name=inputdict["searchval_vehicleowner_name"].decode("utf-8")
			if (len(searchval_vehicleowner_name) > 0):

				wherestr=wherestr+ " and (vehicleowner_name like ${0})".format(fcount)
				flist.append("%"+searchval_vehicleowner_name+"%")
				fcount+=1

			
			rowcount=await conn.fetchval(countstr+wherestr,*flist)
			offsetstr= " LIMIT {0} OFFSET {1}".format(int(length),int(start))
			rows = await conn.fetch(selectstr+wherestr+orderstr+offsetstr+";",*flist)
			data = [dict(r) for r in rows]

			result = {}
			result["draw"] = int(draw)
			result["recordsTotal"] = rowcount
			result["recordsFiltered"] = rowcount
			result["data"] = data

			sss = json.dumps(result, cls=tigerfunctools.CJsonEncoder, ensure_ascii=False)
			self.write(sss)

	async def PostDoInsert(self, inputdict):
		async with ServerParameters.pg_pool.acquire() as conn:
			insertstr="insert into vehicle({0}) values({1});"
			fieldstr=""
			valuestr=""
			fcount=1
			flist=[]

			if ("updaterowdata[vehiclenumber]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclenumber,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclenumber]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclevincode]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclevincode,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclevincode]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleenable]" in inputdict.keys()):#inputdict里面存在这个字段

				fthisv=True
				if (inputdict["updaterowdata[vehicleenable]"].decode("utf-8").lower()=="true"):
					fthisv=True
				else:
					fthisv=False
				fieldstr=fieldstr+"vehicleenable,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(fthisv)
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_inittime]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_inittime,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicledrivingpermit_inittime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_status]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_status,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_status]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_number]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_number,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_number]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_scan]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_scan,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_scan]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_goverment]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_goverment,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_goverment]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_starttime]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_starttime,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicledrivingpermit_starttime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_endtime]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_endtime,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicledrivingpermit_endtime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_class]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledrivingpermit_class,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_class]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_number]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleoperationpermit_number,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_number]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_scan]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleoperationpermit_scan,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_scan]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_goverment]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleoperationpermit_goverment,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_goverment]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_starttime]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleoperationpermit_starttime,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicleoperationpermit_starttime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_endtime]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleoperationpermit_endtime,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicleoperationpermit_endtime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_class]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleoperationpermit_class,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_class]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleservice_type]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleservice_type,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleservice_type]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleservicetype]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleservicetype,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleservicetype]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleseries]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleseries,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleseries]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemodel]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclemodel,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemodel]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemanufacturer]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclemanufacturer,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemanufacturer]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclecolor]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclecolor,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclecolor]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclefueltype]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclefueltype,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclefueltype]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleenginesize]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleenginesize,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehicleenginesize]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclebatterysize]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclebatterysize,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehiclebatterysize]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclewheelbase]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclewheelbase,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehiclewheelbase]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclefullweight]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclefullweight,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehiclefullweight]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclefullpoerson]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclefullpoerson,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(int(inputdict["updaterowdata[vehiclefullpoerson]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleloadweight]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleloadweight,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehicleloadweight]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclephotofront]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclephotofront,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclephotofront]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclephotoside]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclephotoside,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclephotoside]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclephotoback]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclephotoback,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclephotoback]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclegps_installtime]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclegps_installtime,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehiclegps_installtime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclegps_manufacturer]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclegps_manufacturer,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclegps_manufacturer]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclegps_model]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclegps_model,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclegps_model]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclegps_deviceid]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclegps_deviceid,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclegps_deviceid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_manufacturer]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleprint_manufacturer,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleprint_manufacturer]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_model]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleprint_model,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleprint_model]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_deviceid]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleprint_deviceid,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleprint_deviceid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledescription]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicledescription,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledescription]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclesignin_address]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclesignin_address,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclesignin_address]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_time]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleprint_time,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicleprint_time]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleowner_name]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleowner_name,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_name]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_cardid]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleowner_cardid,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_cardid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_phone]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleowner_phone,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_phone]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_company_name]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleowner_company_name,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_company_name]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_company_cardid]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleowner_company_cardid,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_company_cardid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_company_phone]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehicleowner_company_phone,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_company_phone]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclebelongplat]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclebelongplat,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclebelongplat]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclebelongplat_child]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclebelongplat_child,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclebelongplat_child]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemaster_name]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclemaster_name,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemaster_name]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemaster_cardid]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclemaster_cardid,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemaster_cardid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemaster_phone]" in inputdict.keys()):#inputdict里面存在这个字段

				fieldstr=fieldstr+"vehiclemaster_phone,"
				valuestr=valuestr+"${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemaster_phone]"].decode("utf-8"))
				fcount+=1

			fieldstr=fieldstr[0:-1]
			valuestr=valuestr[0:-1]
			querystr=insertstr.format(fieldstr,valuestr)
			result = await conn.execute(querystr,*flist)
			print(result)


	async def PostDoDelete(self, inputdict):
		vehicleid = int(inputdict["updaterowdata[vehicleid]"])
		async with ServerParameters.pg_pool.acquire() as conn:
			result = await conn.execute("delete from vehicle where vehicleid=$1;",vehicleid)
			print(result)

	async def PostDoUpdate(self, inputdict):
		vehicleid = int(inputdict["updaterowdata[vehicleid]"])
		async with ServerParameters.pg_pool.acquire() as conn:
			updatestr="update vehicle set {0} where vehicleid={1};"
			flist=[]
			valuestr=""
			fcount=1

			if ("updaterowdata[vehiclenumber]" in inputdict.keys()):

				valuestr=valuestr+"vehiclenumber=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclenumber]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclevincode]" in inputdict.keys()):

				valuestr=valuestr+"vehiclevincode=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclevincode]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleenable]" in inputdict.keys()):

				if (inputdict["updaterowdata[vehicleenable]"].decode("utf-8").lower()=="true"):
					fbool=True
				else:
					fbool=False
				valuestr=valuestr+"vehicleenable=${0},".format(fcount)
				flist.append(fbool)
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_inittime]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_inittime=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicledrivingpermit_inittime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_status]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_status=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_status]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_number]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_number=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_number]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_scan]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_scan=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_scan]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_goverment]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_goverment=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_goverment]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_starttime]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_starttime=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicledrivingpermit_starttime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_endtime]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_endtime=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicledrivingpermit_endtime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicledrivingpermit_class]" in inputdict.keys()):

				valuestr=valuestr+"vehicledrivingpermit_class=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledrivingpermit_class]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_number]" in inputdict.keys()):

				valuestr=valuestr+"vehicleoperationpermit_number=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_number]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_scan]" in inputdict.keys()):

				valuestr=valuestr+"vehicleoperationpermit_scan=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_scan]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_goverment]" in inputdict.keys()):

				valuestr=valuestr+"vehicleoperationpermit_goverment=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_goverment]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_starttime]" in inputdict.keys()):

				valuestr=valuestr+"vehicleoperationpermit_starttime=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicleoperationpermit_starttime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_endtime]" in inputdict.keys()):

				valuestr=valuestr+"vehicleoperationpermit_endtime=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicleoperationpermit_endtime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleoperationpermit_class]" in inputdict.keys()):

				valuestr=valuestr+"vehicleoperationpermit_class=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleoperationpermit_class]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleservice_type]" in inputdict.keys()):

				valuestr=valuestr+"vehicleservice_type=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleservice_type]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleservicetype]" in inputdict.keys()):

				valuestr=valuestr+"vehicleservicetype=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleservicetype]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleseries]" in inputdict.keys()):

				valuestr=valuestr+"vehicleseries=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleseries]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemodel]" in inputdict.keys()):

				valuestr=valuestr+"vehiclemodel=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemodel]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemanufacturer]" in inputdict.keys()):

				valuestr=valuestr+"vehiclemanufacturer=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemanufacturer]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclecolor]" in inputdict.keys()):

				valuestr=valuestr+"vehiclecolor=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclecolor]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclefueltype]" in inputdict.keys()):

				valuestr=valuestr+"vehiclefueltype=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclefueltype]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleenginesize]" in inputdict.keys()):

				valuestr=valuestr+"vehicleenginesize=${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehicleenginesize]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclebatterysize]" in inputdict.keys()):

				valuestr=valuestr+"vehiclebatterysize=${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehiclebatterysize]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclewheelbase]" in inputdict.keys()):

				valuestr=valuestr+"vehiclewheelbase=${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehiclewheelbase]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclefullweight]" in inputdict.keys()):

				valuestr=valuestr+"vehiclefullweight=${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehiclefullweight]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclefullpoerson]" in inputdict.keys()):

				valuestr=valuestr+"vehiclefullpoerson=${0},".format(fcount)
				flist.append(int(inputdict["updaterowdata[vehiclefullpoerson]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleloadweight]" in inputdict.keys()):

				valuestr=valuestr+"vehicleloadweight=${0},".format(fcount)
				flist.append(float(inputdict["updaterowdata[vehicleloadweight]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclephotofront]" in inputdict.keys()):

				valuestr=valuestr+"vehiclephotofront=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclephotofront]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclephotoside]" in inputdict.keys()):

				valuestr=valuestr+"vehiclephotoside=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclephotoside]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclephotoback]" in inputdict.keys()):

				valuestr=valuestr+"vehiclephotoback=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclephotoback]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclegps_installtime]" in inputdict.keys()):

				valuestr=valuestr+"vehiclegps_installtime=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehiclegps_installtime]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehiclegps_manufacturer]" in inputdict.keys()):

				valuestr=valuestr+"vehiclegps_manufacturer=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclegps_manufacturer]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclegps_model]" in inputdict.keys()):

				valuestr=valuestr+"vehiclegps_model=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclegps_model]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclegps_deviceid]" in inputdict.keys()):

				valuestr=valuestr+"vehiclegps_deviceid=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclegps_deviceid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_manufacturer]" in inputdict.keys()):

				valuestr=valuestr+"vehicleprint_manufacturer=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleprint_manufacturer]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_model]" in inputdict.keys()):

				valuestr=valuestr+"vehicleprint_model=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleprint_model]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_deviceid]" in inputdict.keys()):

				valuestr=valuestr+"vehicleprint_deviceid=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleprint_deviceid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicledescription]" in inputdict.keys()):

				valuestr=valuestr+"vehicledescription=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicledescription]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclesignin_address]" in inputdict.keys()):

				valuestr=valuestr+"vehiclesignin_address=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclesignin_address]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleprint_time]" in inputdict.keys()):

				valuestr=valuestr+"vehicleprint_time=${0},".format(fcount)
				flist.append(parser.parse(inputdict["updaterowdata[vehicleprint_time]"].decode("utf-8")))
				fcount+=1

			if ("updaterowdata[vehicleowner_name]" in inputdict.keys()):

				valuestr=valuestr+"vehicleowner_name=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_name]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_cardid]" in inputdict.keys()):

				valuestr=valuestr+"vehicleowner_cardid=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_cardid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_phone]" in inputdict.keys()):

				valuestr=valuestr+"vehicleowner_phone=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_phone]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_company_name]" in inputdict.keys()):

				valuestr=valuestr+"vehicleowner_company_name=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_company_name]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_company_cardid]" in inputdict.keys()):

				valuestr=valuestr+"vehicleowner_company_cardid=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_company_cardid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehicleowner_company_phone]" in inputdict.keys()):

				valuestr=valuestr+"vehicleowner_company_phone=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehicleowner_company_phone]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclebelongplat]" in inputdict.keys()):

				valuestr=valuestr+"vehiclebelongplat=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclebelongplat]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclebelongplat_child]" in inputdict.keys()):

				valuestr=valuestr+"vehiclebelongplat_child=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclebelongplat_child]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemaster_name]" in inputdict.keys()):

				valuestr=valuestr+"vehiclemaster_name=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemaster_name]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemaster_cardid]" in inputdict.keys()):

				valuestr=valuestr+"vehiclemaster_cardid=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemaster_cardid]"].decode("utf-8"))
				fcount+=1

			if ("updaterowdata[vehiclemaster_phone]" in inputdict.keys()):

				valuestr=valuestr+"vehiclemaster_phone=${0},".format(fcount)
				flist.append(inputdict["updaterowdata[vehiclemaster_phone]"].decode("utf-8"))
				fcount+=1

			valuestr=valuestr[0:-1]
			querystr=updatestr.format(valuestr,vehicleid)
			result = await conn.execute(querystr,*flist)
			print(result)



"""
创建数据库 vehicle
CREATE TABLE vehicle (
  vehicleid SERIAL,
vehiclenumber varchar(12)    DEFAULT null  ,
vehiclevincode varchar(32)    DEFAULT null  ,
vehicleenable  boolean    DEFAULT true  ,
vehicledrivingpermit_inittime timestamp     DEFAULT null  ,
vehicledrivingpermit_status varchar(12)    DEFAULT null  ,
vehicledrivingpermit_number varchar(20)    DEFAULT null  ,
vehicledrivingpermit_scan varchar(64)    DEFAULT null  ,
vehicledrivingpermit_goverment varchar(64)    DEFAULT null  ,
vehicledrivingpermit_starttime timestamp     DEFAULT null  ,
vehicledrivingpermit_endtime timestamp     DEFAULT null  ,
vehicledrivingpermit_class varchar(12)    DEFAULT null  ,
vehicleoperationpermit_number varchar(32)    DEFAULT null  ,
vehicleoperationpermit_scan varchar(64)    DEFAULT null  ,
vehicleoperationpermit_goverment varchar(32)    DEFAULT null  ,
vehicleoperationpermit_starttime timestamp     DEFAULT null  ,
vehicleoperationpermit_endtime timestamp     DEFAULT null  ,
vehicleoperationpermit_class varchar(12)    DEFAULT null  ,
vehicleservice_type varchar(20)    DEFAULT null  ,
vehicleservicetype varchar(20)    DEFAULT null  ,
vehicleseries varchar(32)    DEFAULT null  ,
vehiclemodel varchar(32)    DEFAULT null  ,
vehiclemanufacturer varchar(48)    DEFAULT null  ,
vehiclecolor varchar(32)    DEFAULT null  ,
vehiclefueltype varchar(32)    DEFAULT null  ,
vehicleenginesize  real    DEFAULT 0  ,
vehiclebatterysize  real    DEFAULT 0  ,
vehiclewheelbase  real    DEFAULT 0  ,
vehiclefullweight  real    DEFAULT 0  ,
vehiclefullpoerson  integer    DEFAULT 0  ,
vehicleloadweight  real    DEFAULT 0  ,
vehiclephotofront varchar(64)    DEFAULT null  ,
vehiclephotoside varchar(64)    DEFAULT null  ,
vehiclephotoback varchar(64)    DEFAULT null  ,
vehiclegps_installtime timestamp     DEFAULT null  ,
vehiclegps_manufacturer varchar(48)    DEFAULT null  ,
vehiclegps_model varchar(48)    DEFAULT null  ,
vehiclegps_deviceid varchar(48)    DEFAULT null  ,
vehicleprint_manufacturer varchar(48)    DEFAULT null  ,
vehicleprint_model varchar(48)    DEFAULT null  ,
vehicleprint_deviceid varchar(48)    DEFAULT null  ,
vehicledescription varchar(255)    DEFAULT null  ,
vehiclesignin_address varchar(64)    DEFAULT null  ,
vehicleprint_time timestamp     DEFAULT null  ,
vehicleowner_name varchar(32)    DEFAULT null  ,
vehicleowner_cardid varchar(32)    DEFAULT null  ,
vehicleowner_phone varchar(24)    DEFAULT null  ,
vehicleowner_company_name varchar(64)    DEFAULT null  ,
vehicleowner_company_cardid varchar(48)    DEFAULT null  ,
vehicleowner_company_phone varchar(24)    DEFAULT null  ,
vehiclebelongplat varchar(64)    DEFAULT null  ,
vehiclebelongplat_child varchar(64)    DEFAULT null  ,
vehiclemaster_name varchar(48)    DEFAULT null  ,
vehiclemaster_cardid varchar(48)    DEFAULT null  ,
vehiclemaster_phone varchar(24)    DEFAULT null  ,
PRIMARY KEY(vehicleid)
) ;

comment on column vehicle.vehicleid is 'ID';

comment on column vehicle.vehiclenumber is '车牌号（可以为空，未上牌状态）';
comment on column vehicle.vehiclevincode is '车辆VIN码';
comment on column vehicle.vehicleenable is '车辆有效';
comment on column vehicle.vehicledrivingpermit_inittime is '车辆上牌时间';
comment on column vehicle.vehicledrivingpermit_status is '车辆年审状态';
comment on column vehicle.vehicledrivingpermit_number is '车辆行驶证编号';
comment on column vehicle.vehicledrivingpermit_scan is '车辆行驶证扫描件文件名';
comment on column vehicle.vehicledrivingpermit_goverment is '车辆行驶证颁发机构';
comment on column vehicle.vehicledrivingpermit_starttime is '车辆行驶证有效期起';
comment on column vehicle.vehicledrivingpermit_endtime is '车辆行驶证有效截止';
comment on column vehicle.vehicledrivingpermit_class is '车辆行驶证车辆分类';
comment on column vehicle.vehicleoperationpermit_number is '车辆运营证编号';
comment on column vehicle.vehicleoperationpermit_scan is '车辆运营证扫描件文件名';
comment on column vehicle.vehicleoperationpermit_goverment is '车辆运营证颁发机构';
comment on column vehicle.vehicleoperationpermit_starttime is '车辆运营证有效期起';
comment on column vehicle.vehicleoperationpermit_endtime is '车辆运营证有效截止';
comment on column vehicle.vehicleoperationpermit_class is '车辆属性自营挂靠其他';
comment on column vehicle.vehicleservice_type is '车辆服务类型（网约车，出租车，线路车，私人小汽车，货运车，施工机械）';
comment on column vehicle.vehicleservicetype is '车辆服务性质（自营，托管，其他）';
comment on column vehicle.vehicleseries is '车型系列';
comment on column vehicle.vehiclemodel is '车型型号';
comment on column vehicle.vehiclemanufacturer is '车辆生产厂家';
comment on column vehicle.vehiclecolor is '车辆颜色';
comment on column vehicle.vehiclefueltype is '车辆燃料类型（汽油，柴油，天然气，液化气，电动，混动，其他）';
comment on column vehicle.vehicleenginesize is '车辆发动机排量';
comment on column vehicle.vehiclebatterysize is '车辆新能源电池容量';
comment on column vehicle.vehiclewheelbase is '车辆轴距';
comment on column vehicle.vehiclefullweight is '车辆整备质量';
comment on column vehicle.vehiclefullpoerson is '车辆额定人数';
comment on column vehicle.vehicleloadweight is '车辆载重量';
comment on column vehicle.vehiclephotofront is '车辆照片正面文件名';
comment on column vehicle.vehiclephotoside is '车辆照片侧面文件名';
comment on column vehicle.vehiclephotoback is '车辆照片尾部文件名';
comment on column vehicle.vehiclegps_installtime is '车辆监控设备安装日期';
comment on column vehicle.vehiclegps_manufacturer is '车辆监控设备厂家';
comment on column vehicle.vehiclegps_model is '车辆监控设备型号';
comment on column vehicle.vehiclegps_deviceid is '车辆监控设别序列号';
comment on column vehicle.vehicleprint_manufacturer is '车辆发票打印设备厂家';
comment on column vehicle.vehicleprint_model is '车辆发票打印设备型号';
comment on column vehicle.vehicleprint_deviceid is '车辆发票打印设备序列号';
comment on column vehicle.vehicledescription is '车辆描述';
comment on column vehicle.vehiclesignin_address is '车辆注册地';
comment on column vehicle.vehicleprint_time is '车辆注册日期';
comment on column vehicle.vehicleowner_name is '车辆所有人';
comment on column vehicle.vehicleowner_cardid is '车辆所有人身份证号码';
comment on column vehicle.vehicleowner_phone is '车辆所有人电话号码';
comment on column vehicle.vehicleowner_company_name is '车辆所有公司';
comment on column vehicle.vehicleowner_company_cardid is '车辆所有公司组织代码';
comment on column vehicle.vehicleowner_company_phone is '车辆所有公司电话号码';
comment on column vehicle.vehiclebelongplat is '车辆所属平台公司';
comment on column vehicle.vehiclebelongplat_child is '车辆所属平台分公司';
comment on column vehicle.vehiclemaster_name is '车辆指定责任人姓名（可以是车主本人）';
comment on column vehicle.vehiclemaster_cardid is '车辆指定责任人身份证';
comment on column vehicle.vehiclemaster_phone is '车辆指定责任人电话号码';


 
CREATE UNIQUE INDEX uidx_vehiclenumber ON vehicle (vehiclenumber); 
CREATE UNIQUE INDEX uidx_vehiclevincode ON vehicle (vehiclevincode);          
CREATE INDEX idx_vehicledrivingpermit_number ON vehicle (vehicledrivingpermit_number);                
CREATE INDEX idx_vehicleoperationpermit_number ON vehicle (vehicleoperationpermit_number);                                                                         
CREATE INDEX idx_vehiclegps_deviceid ON vehicle (vehiclegps_deviceid);                   
CREATE INDEX idx_vehicleowner_name ON vehicle (vehicleowner_name); 
CREATE INDEX idx_vehicleowner_cardid ON vehicle (vehicleowner_cardid); 
CREATE INDEX idx_vehicleowner_phone ON vehicle (vehicleowner_phone); 
CREATE INDEX idx_vehicleowner_company_name ON vehicle (vehicleowner_company_name); 
CREATE INDEX idx_vehicleowner_company_cardid ON vehicle (vehicleowner_company_cardid); 
CREATE INDEX idx_vehicleowner_company_phone ON vehicle (vehicleowner_company_phone); 
CREATE INDEX idx_vehiclebelongplat ON vehicle (vehiclebelongplat); 
CREATE INDEX idx_vehiclebelongplat_child ON vehicle (vehiclebelongplat_child); 
CREATE INDEX idx_vehiclemaster_name ON vehicle (vehiclemaster_name); 
CREATE INDEX idx_vehiclemaster_cardid ON vehicle (vehiclemaster_cardid); 
CREATE INDEX idx_vehiclemaster_phone ON vehicle (vehiclemaster_phone);

"""