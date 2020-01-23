# -*- coding: UTF-8 -*-
import threading
import time
import struct
from tornado import ioloop, gen
from tornado.gen import Task
import pdb, time, logging
import tornado.ioloop
import tornado.iostream
import socket
import tigerfunctools
import random
import asyncio
from aiohttp import ClientSession
import math
import const
import datetime
from tornado.platform.asyncio import AsyncIOMainLoop

gcounter=1

def vloop():
    global gcounter
    gcounter+=1
    print(gcounter)
    c_car.io_loop.call_later(c_car.interval/1000,vloop)
    for i in range(c_car.count):
        k = c_car.startphonenumber + i
        ks = "%015d" % k

        if ks in c_car.cars.keys():
            c_car.cars[ks].step()
        else:
            c = c_car(ks)
            c_car.cars[ks].step()
    return


class c_car:
    count = 1
    mappoints = [
        [106.259143, 29.698047],
        [106.371753, 29.360187],
        [106.602466, 29.424536],
        [106.731324, 29.487277],
        [106.848225, 29.543146],
        [106.836552, 29.715788],
        [106.642344, 29.780176],
        [106.445792, 29.707591],
        [106.259143, 29.698047]
    ]
    cars = {}
    cars_lock = threading.RLock()
    host = "a10.4s188.com"
    port = 35150
    EOF = b'\x7E'
    isstart = True
    io_loop = None
    asyncioloop = None
    stepdistance = 80  # 5秒80米  60公里

    jl_jd = 102834.74258026089786013677476285
    jl_wd = 111712.69150641055729984301412873
    jd_2km = 0.01944867998710680373454851233723
    wd_2km = 0.01790306878323875449480166909757

    jd_1m = 0.00000972433999355340186727425616862
    wd_1m = 0.00000895153439161937724740083454878

    interval = 5000  # 步长间隔

    startphonenumber = 910000000000000

    def __init__(self, imei, io_loop=None):

        self.io_loop = io_loop
        self.shutdown = False
        self.stream = None
        self.sock_fd = None
        self.imei = imei
        self.sendcounter = 0
        self.isconnected = 0
        self.stepcounter = 0
        self.stepinnercounter = 0
        self.status = "未连接"
        self.password808=b"12345"
        self.vehiclenumber="VIN"+self.imei
        self.polyline=None

        if c_car.cars_lock.acquire():
            c_car.cars[self.imei] = self
            c_car.cars_lock.release()
        return

    def get_stream(self):
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = tornado.iostream.IOStream(self.sock_fd)
        self.stream.set_close_callback(self.on_close)

    def set_shutdown(self):
        self.shutdown = True

    def on_close(self):
        '''
        if (self.imei in c_car.cars.keys()):
            del c_car.cars[self.imei]
        '''

        self.isconnected = 0
        self.stream = None
        if self.shutdown:
            self.io_loop.stop()
        self.status = "未连接"
        return

    def connect(self):
        if (self.stream == None):
            self.get_stream()
        self.stream.connect((self.host, self.port), self.connectcomplete)

    def connectcomplete(self):
        self.isconnected = 1
        self.status = "初始化OK"
        self.stream.read_until(c_car.EOF, self.on_receive)
        return

    def on_receive(self, data):
        # print("R: " + ':'.join("%02x" % x for x in data))
        self.stream.read_until(c_car.EOF, self.on_receive)
        self.processmsg(data)

    def step(self):
        if (c_car.isstart == True):
            print(self.imei, self.status)
        self.checkconnect()
        if (self.isconnected == 0):
            return
        self.stepcounter = self.stepcounter + 1
        if (self.stepcounter % 10 == 0):
            self.sendmsg(0x0002)  # 心跳

        if (self.status == "初始化OK"):
            self.login808()
            return

        if (self.status=="登录中"):
            self.stepinnercounter+=1
            if (self.stepinnercounter>20):
                self.status="初始化OK"
            return

        if (self.status=="登录失败"):
            self.signin808()
            return

        if (self.status=="注册中"):
            self.stepinnercounter+=1
            if (self.stepinnercounter>20):
                self.status="初始化OK"
            return

        if (self.status=="注册OK"):
            self.login808()
            return

        if (self.status=="注册失败"):
            self.login808()
            return

        if (self.status == "登录OK"):
            if (self.polyline != None):
                self.status = "模拟行驶中"
            else:
                self.makepoint()
                self.status = "生成随机点OK"
                self.stepinnercounter = 0
            return

        if (self.status == "生成随机点OK"):
            if (self.stepinnercounter % 6 == 0):  # 30秒间隔才调用一次计算，以免太多调用
                c_car.asyncioloop.create_task(
                    self.getgdpath(self.startpoint[0], self.startpoint[1], self.endpoint[0], self.endpoint[1]))
            self.stepinnercounter += 1
            return
        if (self.status == "获取导航路径OK"):
            self.polylineindex = 0
            self.polylineinnerindex = 0  # 两个点内部的过度
            self.status = "模拟行驶中"
            return
        if (self.status == "模拟行驶中"):
            if (self.polylineindex >= len(self.polyline) - 1):
                self.status = "到达终点OK"
                return
            if (self.polylineinnerindex == 0):
                # 每一步都可以随机调整速度
                # self.stepdistance = c_car.stepdistance / 3 + random.uniform(0, c_car.stepdistance)
                self.pdistance = tigerfunctools.distance(self.polyline[self.polylineindex],
                                                         self.polyline[self.polylineindex + 1]) / c_car.jd_1m
                if (self.pdistance > self.stepdistance):
                    # 分多步骤
                    self.polylineinnercount = int(self.pdistance / self.stepdistance) + 1
                    self.polylineinnerindex = 0
                else:
                    # 单步
                    self.polylineinnercount = 1
                    self.polylineinnerindex = 0
            self.send0200()
            return
        if (self.status == "到达终点OK"):
            self.polyline = None
            self.polylineindex = 0
            self.status = "初始化OK"
            return
        return

    def login808(self):
        b1=struct.pack(str(len(self.password808)+1)+"s",self.password808)
        self.status="登录中"
        self.sendmsg(0x0102,b1)
        self.stepinnercounter=0
        return

    def signin808(self):
        vbs=self.vehiclenumber.encode("gbk")
        imeibs=self.imei.encode("gbk")
        b1=struct.pack(">HH5s20s7sB"+str(len(vbs)+1)+"s",0,0,b"goldh",
                       b"autorec_a_"+imeibs[:8],imeibs[8:],0,
                       vbs)
        self.status="注册中"
        self.sendmsg(0x0100,b1)
        self.stepinnercounter=0
        return

    def send0200(self):
        # 发送0200模拟消息
        # 根据步长计算xyz和速度方向

        x = self.polyline[self.polylineindex][0] + ((self.polyline[self.polylineindex + 1][0] -
                                                     self.polyline[self.polylineindex][
                                                         0]) * self.polylineinnerindex) / self.polylineinnercount
        y = self.polyline[self.polylineindex][1] + ((self.polyline[self.polylineindex + 1][1] -
                                                     self.polyline[self.polylineindex][
                                                         1]) * self.polylineinnerindex) / self.polylineinnercount
        z = 100
        speed = (float(self.stepdistance) * (12 * 60)) / 100
        direction = tigerfunctools.calcangle(self.polyline[self.polylineindex][0], self.polyline[self.polylineindex][1],
                                             self.polyline[self.polylineindex + 1][0],
                                             self.polyline[self.polylineindex + 1][1])

        ts = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        bs = tigerfunctools.writenumberstringtobcd(ts, 6)

        x2,y2=tigerfunctools.gcj02towgs(x,y) #转变为真实gps坐标

        b1 = struct.pack(">IIIIHHH6s", 0, 0, int(y2 * 1000000), int(x2 * 1000000), int(z), int(speed * 10),
                         int(direction), bs)

        self.sendmsg(0x0200, b1)

        self.polylineinnerindex += 1
        if (self.polylineinnerindex >= self.polylineinnercount):
            self.polylineindex += 1
            self.polylineinnerindex = 0
        return

    def convertpolylinestrtolist(self, ps):
        plist = ps.split(";")
        ppp = []
        for u in plist:
            dd = u.split(",")
            ppp.append([float(dd[0]), float(dd[1])])
        return ppp

    def close(self):
        if (self.stream == None):
            return
        if (self.stream.closed() == True):
            return
        self.stream.close()
        return

    def checkconnect(self):
        if (self.stream != None):
            if (self.stream.closed() == False):
                return
        if (c_car.isstart == False):
            return
        # 开始连接
        # try:
        self.connect()
        # finally:
        #    return
        return

    def sendmsg(self, msgid=0x0001, sendbuffer=b""):  # 打包
        if (not (type(sendbuffer) is bytes)):
            return
        if (self.isconnected == 0):
            return

        bcds = tigerfunctools.writenumberstringtobcd(self.imei)
        b1 = struct.pack(">HH6sH" + str(len(sendbuffer)) + "s", msgid, len(sendbuffer), bcds, self.sendcounter,
                         sendbuffer)
        self.sendcounter = self.sendcounter + 1

        b2 = bytearray(0)
        # 校验码
        xb = b1[0]
        for x in b1[1:]:
            xb = xb ^ x
        # 转义封包
        b2.append(0x7e)
        for x in b1:
            if (x == 0x7e):
                b2.append(0x7d)
                b2.append(2)
            elif (x == 0x7d):
                b2.append(0x7d)
                b2.append(1)
            else:
                b2.append(x)
        if (xb == 0x7e):
            b2.append(0x7d)
            b2.append(2)
        elif (xb == 0x7d):
            b2.append(0x7d)
            b2.append(1)
        else:
            b2.append(xb)
        b2.append(0x7e)
        # print("S: " + ':'.join("%02x" % x for x in b2))

        self.stream.write(b2)
        #print("send ",self.sendcounter)
        return

    def processmsg(self, data=b""):
        if (len(data) < 12):
            return
        b2 = bytearray(0)
        status = 0
        for d in data[:-1]:
            if (d == 0x7d):
                status = 1
            else:
                if (status == 0):
                    b2.append(d)
                else:
                    status = 0
                    if (d == 0x01):
                        b2.append(0x7D)
                    elif (d == 0x02):
                        b2.append(0x7E)
                    else:
                        continue
                # 出错了
        xb = b2[0]
        for d in b2[1:-1]:
            xb = xb ^ d
        if (xb != b2[-1]):
            # 校验码错误
            return
        unpack_list = struct.unpack(">HH6sH", b2[0:12])
        msgid = unpack_list[0]
        msgbodylen = unpack_list[1]
        msgflowid = unpack_list[3]
        # b2[12]开始是body
        if (msgid==0x8001):
            self.processmsg8001(b2[12:])
        elif (msgid==0x8100):
            self.processmsg8100(b2[12:])
        elif (msgid==0x8500):
            self.processmsg8500(b2[12:],msgid,msgflowid)
        elif (msgid==0x8107):
            self.processmsg8107(b2[12:])

        return

    def processmsg8001(self,bs):
        unpack_list = struct.unpack(">HHB", bs[0:5])
        answerflowid=unpack_list[0]
        answermsgid=unpack_list[1]
        answerresult=unpack_list[2]

        if(answermsgid==0x0102):
            if (answerresult==0):
                if (self.status=="登录中"):
                    self.status="登录OK"
            elif (answerresult==1):
                if (self.status=="登录中"):
                    self.status = "登录失败"
            return

        return

    def processmsg8100(self,bs):
        unpack_list = struct.unpack(">HB", bs[0:3])
        answerflowid=unpack_list[0]
        answerresult=unpack_list[1]
        if (answerresult==0):
            if (self.status=="注册中"):
                self.status="注册OK"
                count=tigerfunctools.stringlenfrombytes(bs[3:])
                self.password808=struct.unpack(str(count)+"s",bs[3:3+count])[0]
            return
        else:
            if (self.status=="注册中"):
                self.status="注册失败"
            return
        return

    def processmsg8107(self,bs):
        imeibs = self.imei.encode("gbk")
        b=struct.pack(">H5s20s7s8s10sBBBB",
                      0xFFFF,
                      b"goldh",
                      b"autorec_a_"+imeibs[:8],imeibs[8:],
                      b"\x00\x00\x00\x00\x00\x00\x00\x00",
                      tigerfunctools.BytestoBCD10(imeibs),
                      0,0,0xFF,0xFF
                      )
        logging.info(self.imei+" 0107 "+str(b))
        self.sendmsg(0x0107,b)
        return

    def processmsg8500(self,bs,msgid,msgflowid):
        code = struct.unpack(">H", bs[0:2])[0]
        count = tigerfunctools.stringlenfrombytes(bs[2:])
        message = struct.unpack(str(count) + "s", bs[2:2 + count])[0]
        print(code,message)
        b=struct.pack(">HHB",msgflowid,msgid,0)
        self.sendmsg(0x0001,b)
        return

    def makepoint(self):
        # 生成导航起点终点
        minx = min(x[0] for x in c_car.mappoints)
        maxx = max(x[0] for x in c_car.mappoints)
        miny = min(x[1] for x in c_car.mappoints)
        maxy = max(x[1] for x in c_car.mappoints)


        #if (hasattr(self, "endpoint")):
        if False:
            self.startpoint = self.endpoint
        else:
            while True:
                x = random.uniform(minx, maxx)
                y = random.uniform(miny, maxy)
                if (tigerfunctools.isPointInPolygon([x, y], c_car.mappoints) == True):
                    self.startpoint = [x, y]
                    break
        while True:
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            if (tigerfunctools.isPointInPolygon([x, y], c_car.mappoints) == True):
                self.endpoint = [x, y]
                break
        return

    async def getgdpath(self, x1, y1, x2, y2):
        url = "https://restapi.amap.com/v3/direction/driving?origin=%f,%f&destination=%f,%f&strategy=4&output=json&key=3b715f1dbfba0802953f6952303b398d" % (
            x1, y1, x2, y2)
        async with ClientSession() as session:
            async with session.get(url) as response:
                j = await response.json()
                if (j["status"] == "0"):
                    return None
                if (j["count"] != "1"):
                    return None
                self.path = j["route"]["paths"][0]
                self.polyline = []
                for u in self.path["steps"]:
                    ms = self.convertpolylinestrtolist(u["polyline"])
                    for uu in ms:
                        self.polyline.append(uu)
                self.stepdistance = c_car.stepdistance / 2 + random.uniform(0, c_car.stepdistance)
                self.status = "获取导航路径OK"
                # print(self.polyline)
                # return j["route"]["paths"][0]
        return


def vcar_main(instance, asyncioloop):
    c_car.startphonenumber=970000000000000
    c_car.asyncioloop = asyncioloop
    c_car.io_loop = instance
    c_car.host = "a10.4s188.com"
    c_car.port = 35150
    #c_car.host = "127.0.0.1"
    #c_car.port = 5050
    c_car.count = 2
    c_car.isstart = True
    c_car.interval=1000
    c_car.stepdistance=16*(c_car.interval/1000)
    c_car.io_loop.call_later(c_car.interval/1000,vloop)
    #ioloop.PeriodicCallback(vloop, c_car.interval).start()
    
    return


def vcar_start():
    c_car.isstart = True
    return


def vcar_stop():
    c_car.isstart = False
    for x in c_car.cars:
        c_car.cars[x].close()
        c_car.cars[x].polyline = None
    return


if __name__ == "__main__":  # 用于测试
    tigerfunctools.init_logging()

    asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    instance = tornado.ioloop.IOLoop.instance()


    vcar_main(instance, asyncioloop)

    # asyncioloop.create_task(getgdpath(116.45925, 39.910031, 116.587922, 40.081577))

    logging.info("**********************start ioloop******************")
    asyncioloop.run_forever()

