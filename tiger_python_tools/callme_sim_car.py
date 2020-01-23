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
import random
import asyncio
from aiohttp import ClientSession
import math
import datetime
import json
import os
import tigerfunctools
import config


class callme_car:
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
    EOF = b'\x3E'
    isstart = True
    io_loop = None
    asyncioloop = None
    stepdistance = 80  # 5秒80米  60公里
    startphonenumber = 16200000000

    jl_jd = 102834.74258026089786013677476285
    jl_wd = 111712.69150641055729984301412873
    jd_2km = 0.01944867998710680373454851233723
    wd_2km = 0.01790306878323875449480166909757
    jd_1m = 0.00000972433999355340186727425616862
    wd_1m = 0.00000895153439161937724740083454878

    interval = 5000  # 步长间隔

    appname = b"callme_sim_python"

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
        self.password808 = b"12345"
        self.vehiclenumber = "VIN" + self.imei
        self.polyline = None

        if callme_car.cars_lock.acquire():
            callme_car.cars[self.imei] = self
            callme_car.cars_lock.release()
        return

    def get_stream(self):
        self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = tornado.iostream.IOStream(self.sock_fd)
        self.stream.set_close_callback(self.on_close)

    def set_shutdown(self):
        self.shutdown = True

    def on_close(self):
        '''
        if (self.imei in callme_car.cars.keys()):
            del callme_car.cars[self.imei]
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
        self.stream.read_until(callme_car.EOF, self.on_receive)
        return

    def on_receive(self, data):
        # print("R: " + ':'.join("%02x" % x for x in data))
        self.stream.read_until(callme_car.EOF, self.on_receive)
        self.processmsg(data)

    def changestatus(self, status):
        self.status = status
        self.stepinnercounter = 0

    def step(self):
        if (callme_car.isstart == True):
            print(self.imei, self.status)
        self.checkconnect()
        if (self.isconnected == 0):
            return
        self.stepcounter = self.stepcounter + 1
        if (self.stepcounter % 10 == 0):
            b1 = struct.pack("B", 60)
            self.sendmsg(0x0105, b1)  # 心跳

        if (self.status == "初始化OK"):
            self.login0103()
            return

        if (self.status == "登录中"):
            self.stepinnercounter += 1
            if (self.stepinnercounter > 20):
                self.changestatus("初始化OK")
            return

        if (self.status == "登录失败"):
            self.stepinnercounter += 1
            if (self.stepinnercounter > 20):
                self.login0103()
            return

        if (self.status == "注册中"):
            self.stepinnercounter += 1
            if (self.stepinnercounter > 20):
                self.changestatus("初始化OK")
            return

        if (self.status == "注册OK"):
            self.login808()
            return

        if (self.status == "注册失败"):
            self.login808()
            return

        if (self.status == "登录OK"):
            if (self.polyline != None):
                self.changestatus("模拟行驶中")
            else:
                self.makepoint()
                self.changestatus("生成随机点OK")
                self.stepinnercounter = 0
            return

        if (self.status == "生成随机点OK"):
            if (self.stepinnercounter % 6 == 0):  # 30秒间隔才调用一次计算，以免太多调用
                callme_car.asyncioloop.create_task(
                    self.getgdpath(self.startpoint[0], self.startpoint[1], self.endpoint[0], self.endpoint[1]))
            self.stepinnercounter += 1
            return
        if (self.status == "获取导航路径OK"):
            self.polylineindex = 0
            self.polylineinnerindex = 0  # 两个点内部的过度
            self.changestatus("模拟行驶中")
        if (self.status == "模拟行驶中"):
            if (self.polylineindex >= len(self.polyline) - 1):
                self.changestatus("到达终点OK")
                return
            if (self.polylineinnerindex == 0):
                # 每一步都可以随机调整速度
                # self.stepdistance = callme_car.stepdistance / 3 + random.uniform(0, callme_car.stepdistance)
                self.pdistance = tigerfunctools.distance(self.polyline[self.polylineindex],
                                                         self.polyline[self.polylineindex + 1]) / callme_car.jd_1m
                if (self.pdistance > self.stepdistance):
                    # 分多步骤
                    self.polylineinnercount = int(self.pdistance / self.stepdistance) + 1
                    self.polylineinnerindex = 0
                else:
                    # 单步
                    self.polylineinnercount = 1
                    self.polylineinnerindex = 0
            self.send0205()

            return
        if (self.status == "到达终点OK"):
            self.polyline = None
            self.polylineindex = 0
            self.changestatus("登录OK")

        return

    def login0103(self):
        bimei = self.imei.encode("gbk")
        b1 = struct.pack(str(len(bimei) + 1) + "s" + str(len(callme_car.appname) + 1) + "sBBBBBBB", bimei,
                         callme_car.appname, 0, 0, 0, 0, 0, 0, 0)
        self.changestatus("登录中")
        self.sendmsg(0x0103, b1)
        self.stepinnercounter = 0
        return

    def signin808(self):
        vbs = self.vehiclenumber.encode("gbk")
        imeibs = self.imei.encode("gbk")
        b1 = struct.pack(">HH5s20s7sB" + str(len(vbs) + 1) + "s", 0, 0, b"goldh",
                         b"autorec_a_" + imeibs[:8], imeibs[8:], 0,
                         vbs)
        self.changestatus("注册中")
        self.sendmsg(0x0100, b1)
        self.stepinnercounter = 0
        return

    def send0205(self):
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

        # timefrom1970=(datetime.datetime.now()-datetime.datetime(1970,1,1)).seconds
        timefrom1970 = int(time.mktime(datetime.datetime.now().timetuple()))
        sss = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(x, y, z, int(direction), speed, 100, 8, 1,
                                                                             100, 0, 0, 0, 1, 4, 100, 300, 10,
                                                                             timefrom1970)

        bsss = sss.encode("gbk")

        # b1 = struct.pack(">IIIIHHH6s", 0, 0, int(y * 1000000), int(x * 1000000), int(z), int(speed * 10),
        #                 int(direction), bs)
        b1 = struct.pack(str(len(bsss) + 1) + "s", bsss)

        self.sendmsg(0x0205, b1)

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
        if (callme_car.isstart == False):
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

        dnow = datetime.datetime.now()
        dnowstr = dnow.strftime("%y%m%d%H%M%S")
        bcds = tigerfunctools.writenumberstringtobcd(dnowstr)
        if (self.sendcounter >= 65535):
            self.sendcounter = 0
        b1 = struct.pack(">HH6sH" + str(len(sendbuffer)) + "s", msgid, len(sendbuffer), bcds, self.sendcounter,
                         sendbuffer)
        self.sendcounter = self.sendcounter + 1

        b2 = bytearray(0)
        # 校验码
        xb = b1[0]
        for x in b1[1:]:
            xb = xb ^ x
        # 转义封包
        b2.append(0x3e)
        for x in b1:
            if (x == 0x3e):
                b2.append(0x3d)
                b2.append(2)
            elif (x == 0x3d):
                b2.append(0x3d)
                b2.append(1)
            else:
                b2.append(x)
        if (xb == 0x3e):
            b2.append(0x3d)
            b2.append(2)
        elif (xb == 0x3d):
            b2.append(0x3d)
            b2.append(1)
        else:
            b2.append(xb)
        b2.append(0x3e)
        # print("S: " + ':'.join("%02x" % x for x in b2))

        self.stream.write(b2)
        return

    def processmsg(self, data=b""):
        if (len(data) < 12):
            return
        b2 = bytearray(0)
        status = 0
        for d in data[:-1]:
            if (d == 0x3d):
                status = 1
            else:
                if (status == 0):
                    b2.append(d)
                else:
                    status = 0
                    if (d == 0x01):
                        b2.append(0x3D)
                    elif (d == 0x02):
                        b2.append(0x3E)
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
        if (msgid == 0x8001):
            self.processmsg8001(b2[12:])
        elif (msgid == 0x8100):
            self.processmsg8100(b2[12:])
        elif (msgid == 0x8500):
            self.processmsg8500(b2[12:], msgid, msgflowid)
        elif (msgid == 0xA500):
            self.processmsg8500(b2[12:], msgid, msgflowid)
        return

    def processmsg8001(self, bs):
        unpack_list = struct.unpack(">HHB", bs[0:5])
        answerflowid = unpack_list[0]
        answermsgid = unpack_list[1]
        answerresult = unpack_list[2]

        if (answermsgid == 0x0103):
            if (answerresult == 1):
                if (self.status == "登录中"):
                    self.changestatus("登录OK")
            else:
                if (self.status == "登录中"):
                    self.changestatus("登录失败")
                    self.stepinnercounter = 1
            return

        return

    def processmsg8100(self, bs):
        unpack_list = struct.unpack(">HB", bs[0:3])
        answerflowid = unpack_list[0]
        answerresult = unpack_list[1]
        if (answerresult == 0):
            if (self.status == "注册中"):
                self.changestatus("注册OK")
                count = tigerfunctools.stringlenfrombytes(bs[3:])
                self.password808 = struct.unpack(str(count) + "s", bs[3:3 + count])[0]
            return
        else:
            if (self.status == "注册中"):
                self.changestatus("注册失败")
            return
        return

    def processmsg8500(self, bs, msgid, msgflowid):
        code = struct.unpack(">H", bs[0:2])[0]
        count = tigerfunctools.stringlenfrombytes(bs[2:])
        message = struct.unpack(str(count) + "s", bs[2:2 + count])[0]
        print(code, message)
        b = struct.pack(">HHB", msgflowid, msgid, 0)
        self.sendmsg(0x0001, b)
        return

    def processmsgA500(self, bs, msgid, msgflowid):
        code = struct.unpack(">H", bs[0:2])[0]
        count = tigerfunctools.stringlenfrombytes(bs[2:])
        message = struct.unpack(str(count) + "s", bs[2:2 + count])[0]
        print(code, message)
        b = struct.pack(">HHB", msgflowid, msgid, 0)
        self.sendmsg(0x0001, b)
        return

    def makepoint(self):
        # 生成导航起点终点
        minx = min(x[0] for x in callme_car.mappoints)
        maxx = max(x[0] for x in callme_car.mappoints)
        miny = min(x[1] for x in callme_car.mappoints)
        maxy = max(x[1] for x in callme_car.mappoints)

        if (hasattr(self, "endpoint")):
            self.startpoint = self.endpoint
        else:
            while True:
                x = random.uniform(minx, maxx)
                y = random.uniform(miny, maxy)
                if (tigerfunctools.isPointInPolygon([x, y], callme_car.mappoints) == True):
                    self.startpoint = [x, y]
                    break
        while True:
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            if (tigerfunctools.isPointInPolygon([x, y], callme_car.mappoints) == True):
                self.endpoint = [x, y]
                break
        return

    def loadfrompolygonfile(filename):
        f = open(config.datapath() + filename, "r")
        s = f.read()
        f.close()
        callme_car.mappoints = json.loads(s)
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
                self.stepdistance = callme_car.stepdistance / 2 + random.uniform(0, callme_car.stepdistance)
                self.changestatus("获取导航路径OK")
                # print(self.polyline)
                # return j["route"]["paths"][0]
        return


class LoopThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.counter = 0

    def run(self):
        while (True):
            time.sleep(5)
        return


def vloop():
    callme_car.io_loop.call_later(callme_car.interval / 1000, vloop)
    for i in range(callme_car.count):
        k = callme_car.startphonenumber + i
        ks = "%011d" % k
        if ks in callme_car.cars.keys():
            callme_car.cars[ks].step()
        else:
            c = callme_car(ks)
            callme_car.cars[ks].step()
    return


def callme_car_saveconfig():
    out = dict()
    out["mappoints"] = callme_car.mappoints
    out["count"] = callme_car.count
    out["startphonenumber"] = callme_car.startphonenumber
    f = open(config.datapath() + "callme_sim_config.json", "w")
    s = json.dumps(out)
    f.write(s)
    f.close()


def callme_car_main(io_loop, asyncioloop):
    callme_car.startphonenumber = 16300000000
    callme_car.asyncioloop = asyncioloop
    callme_car.io_loop = io_loop
    callme_car.host = "127.0.0.1"
    callme_car.port = 5050
    callme_car.count = 1
    callme_car.isstart = False
    #ioloop.PeriodicCallback(vloop, callme_car.interval).start() #有问题，会一次多条
    callme_car.io_loop.call_later(callme_car.interval / 1000, vloop)

    if (os.path.isfile(config.datafilepath() + "callme_sim_config.json")):
        f = open(config.datafilepath() + "callme_sim_config.json", "r")
        s = f.read()
        f.close()
        o = json.loads(s)
        callme_car.startphonenumber = o["startphonenumber"]
        callme_car.count = o["count"]
        callme_car.mappoints = o["mappoints"]

    return


def callmecar_start():
    callme_car_saveconfig()
    callme_car.isstart = True
    return


def callmecar_stop():
    callme_car.isstart = False
    for x in callme_car.cars:
        callme_car.cars[x].close()
        callme_car.cars[x].polyline = None
    return


if __name__ == "__main__111":
    asyncioloop = asyncio.get_event_loop()

    # asyncioloop.run_until_complete(getgdpath(116.45925, 39.910031, 116.587922, 40.081577))

if __name__ == "__main__222":

    minx = min(x[0] for x in callme_car.mappoints)
    maxx = max(x[0] for x in callme_car.mappoints)
    miny = min(x[1] for x in callme_car.mappoints)
    maxy = max(x[1] for x in callme_car.mappoints)

    while True:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        if (tigerfunctools.isPointInPolygon([x, y], callme_car.mappoints) == True):
            print(x, y)
            break

    print(minx, maxx, miny, maxy)

if __name__ == "__main__":  # 用于测试
    tigerfunctools.init_logging()

    io_loop = tornado.ioloop.IOLoop.instance()
    asyncioloop = asyncio.get_event_loop()

    callme_car_main(io_loop, asyncioloop)
    callme_car.isstart = True

    # asyncioloop.create_task(getgdpath(116.45925, 39.910031, 116.587922, 40.081577))

    logging.info("**********************start ioloop******************")
    io_loop.start()
