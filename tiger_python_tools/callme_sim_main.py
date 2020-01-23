import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.autoreload
import os.path
import json
import callme_sim_car
import vcar_server
import asyncio
from aiohttp import ClientSession
import os
import config
from tornado.platform.asyncio import AsyncIOMainLoop
import tornado.gen


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world, Callme V Cars...... by Tiger")

class SettingHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("vcar_setting.html")

class TestMapHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("vcar_testmap.html")


class listpolygonnamesHandler(tornado.web.RequestHandler):
    def post(self):
        lst = os.listdir(config.datapath())
        files = [c for c in lst if os.path.isfile(config.datapath() + c) and c.endswith(".polygon")]
        outdict=dict()
        outdict["code"]=0
        outdict["message"]="成功"
        outdict["data"]=files
        self.write(json.dumps(outdict))

class getcurrentsystempolygonHandler(tornado.web.RequestHandler):
    def post(self):
        path=callme_sim_car.callme_car.mappoints
        if(path==None):
            outdict = dict()
            outdict["code"] = 1
            outdict["message"] = "并无加载的围栏"
            outdict["data"] = None
            self.write(json.dumps(outdict))
            return
        outdict = dict()
        outdict["code"] = 0
        outdict["message"] = "成功"
        outdict["data"] = path
        minx = min(x[0] for x in path)
        maxx = max(x[0] for x in path)
        miny = min(x[1] for x in path)
        maxy = max(x[1] for x in path)
        x=(minx+maxx)/2
        y=(miny+maxy)/2
        outdict["center"]=[x,y]
        self.write(json.dumps(outdict))


class loadpolygonfileHandler(tornado.web.RequestHandler):
    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        filename=inputdict["filename"].decode("utf-8")
        if (filename.endswith(".polygon") == False):
            filename = filename + ".polygon"
        f=open(config.datapath()+filename,"r")
        s=f.read()
        path=json.loads(s)
        f.close()
        minx = min(x[0] for x in path)
        maxx = max(x[0] for x in path)
        miny = min(x[1] for x in path)
        maxy = max(x[1] for x in path)
        x=(minx+maxx)/2
        y=(miny+maxy)/2
        outdict=dict()
        outdict["code"]=0
        outdict["message"]="成功"
        outdict["data"]=path
        outdict["center"] = [x, y]
        self.write(json.dumps(outdict))

class savepolygonfileHandler(tornado.web.RequestHandler):
    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        filename=inputdict["filename"].decode("utf-8")
        polygon=inputdict["polygon"].decode("utf-8")
        if (filename.endswith(".polygon")==False):
            filename=filename+".polygon"
        f=open(config.datapath()+filename,"w")
        f.write(polygon)
        f.close()
        callme_sim_car.callme_car.loadfrompolygonfile(filename)
        outdict=dict()
        outdict["code"]=0
        outdict["message"]="成功"
        outdict["data"]=None
        self.write(json.dumps(outdict))

class callme_sim_actionHandler(tornado.web.RequestHandler):
    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        action=inputdict["action"].decode("utf-8")
        if (action=="start"):
            vehiclecount = int(inputdict["vehiclecount"])
            if (vehiclecount > 1000):
                vehiclecount = 1000
            startphonenumber = int(inputdict["startphonenumber"])
            callme_sim_car.callme_car.count=vehiclecount
            callme_sim_car.callme_car.startphonenumber=startphonenumber
            callme_sim_car.callmecar_start()
        else:
            callme_sim_car.callmecar_stop()
        outdict=dict()
        outdict["code"]=0
        outdict["message"]="成功"
        outdict["data"]=None
        self.write(json.dumps(outdict))

class callme_sim_setconfigHandler(tornado.web.RequestHandler):
    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        if (callme_sim_car.callme_car.isstart==True):
            callme_sim_car.callmecar_stop()
        callme_sim_car.callme_car.count=int(inputdict["count"])
        callme_sim_car.callme_car.startphonenumber=int(inputdict["startphonenumber"])
        outdict=dict()
        outdict["code"]=0
        outdict["message"]="成功"
        outdict["data"]=None
        self.write(json.dumps(outdict))

class callme_sim_getconfigHandler(tornado.web.RequestHandler):
    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        outdict=dict()
        outdict["code"]=0
        outdict["message"]="成功"
        outdict["data"]=dict()
        outdict["data"]["vehiclecount"]=callme_sim_car.callme_car.count
        outdict["data"]["startphonenumber"]=callme_sim_car.callme_car.startphonenumber
        self.set_header("Access-Control-Allow-Origin", "*")#可以跨域访问Api
        self.write(json.dumps(outdict))




settings = {
    'template_path': 'views',        # html文件
    'static_path': 'static',        # 静态文件（css,js,img）
    'cookie_secret': '61oETzKXQAGaYdkL5gEmGeJJFuYdasdfah7EQnp2',      # cookie自定义字符串加盐
    'autoreload': True, #自动重读网页，当刷新的时候
    'debug':True,#调试模式，自动刷新刚改的网页
    #'static_url_prefix': '/statics/',# 静态文件前缀
    # 'xsrf_cookies': True,          # 防止跨站伪造
    # 'ui_methods': mt,              # 自定义UIMethod函数
    # 'ui_modules': md,              # 自定义UIModule类
}

application = tornado.web.Application([
    (r"/", SettingHandler),
    (r"/about", MainHandler),
    (r"/testmap", TestMapHandler),
    (r"/listpolygonnames", listpolygonnamesHandler),
    (r"/savepolygonfile", savepolygonfileHandler),
    (r"/callme_sim_action",callme_sim_actionHandler),
    (r"/getcurrentpolygon", getcurrentsystempolygonHandler),
    (r"/loadpolygonfile", loadpolygonfileHandler),
    (r"/callme_sim_setconfig",callme_sim_setconfigHandler),
    (r"/callme_sim_getconfig", callme_sim_getconfigHandler),
    (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/assets/"}),
    (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/css/"}),
    (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/images/"}),
    (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/js/"}),
    (r"/lib/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/lib/"}),
], **settings)

if __name__ == "__main__":
    '''
    application.listen(8888)
    instance = tornado.ioloop.IOLoop.instance()
    asyncioloop = asyncio.get_event_loop()
    callme_sim_car.callme_car_main(instance,asyncioloop)
    tornado.autoreload.start(instance)
    instance.start()
    '''
    '''
    application.listen(8888)

    #让tornado兼容asyncio
    tornado.ioloop.IOLoop.configure("tornado.platform.asyncio.AsyncIOLoop")
    instance = tornado.ioloop.IOLoop.instance()

    asyncioloop = asyncio.get_event_loop()
    callme_sim_car.callme_car_main(instance,asyncioloop)
    #tornado.autoreload.start()
    instance.start()
    '''

    application.listen(8888)

    #让tornado兼容asyncio
    #tornado.ioloop.IOLoop.configure("tornado.platform.asyncio.AsyncIOLoop")

    asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    instance = tornado.ioloop.IOLoop.instance()
    callme_sim_car.callme_car_main(instance,asyncioloop)
    #tornado.autoreload.start()
    #instance.start()
    asyncioloop.run_forever()
