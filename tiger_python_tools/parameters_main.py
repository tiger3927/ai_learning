import tornado.ioloop
import tornado.web
import tornado.websocket
import os.path

import json
import asyncio

from tornado.platform.asyncio import AsyncIOMainLoop
import tornado.gen

from config import ServerParameters

import motordownload
import motorupload

import sqlalchemy
from aiomysql.sa import create_engine
import logging

import tigerfunctools

import parameters_dictionary





class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write("Hello, world,I am Parameters 模块")
        self.write("<br/>")
        for k,v in parameters_dictionary.dts.items():
            self.write(k)
            self.write("<br/>")
            s=json.dumps(v,cls=tigerfunctools.CJsonEncoder,ensure_ascii=False)
            self.write(s)
            self.write("<br/>")
            self.write("<br/>")


settings = {
    'template_path': os.path.join(os.path.dirname(__file__), "views"),  # html文件
    'static_path': os.path.join(os.path.dirname(__file__), "static"),  # 静态文件（css,js,img）
    'cookie_secret': '61oETzKXQAGaYdkL5gEmGeJJFuYdasdfah7EQnp2',  # cookie自定义字符串加盐
    'autoreload': True,  # 自动重读网页，当刷新的时候
}

application = tornado.web.Application([
    (r"/aa", MainHandler),
    (r"/api/dictionarytype",parameters_dictionary.DictionaryTypeHandler),
    (r"/api/dictionary", parameters_dictionary.DictionaryTypeHandler),
    (r"/api/alldictionary", parameters_dictionary.AllDictionaryHandler),

    (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/assets/"}),
    (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/css/"}),
    (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/images/"}),
    (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/js/"}),
    (r"/lib/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/lib/"}),

], **settings)

if __name__ == "__main__":
    application.listen(8888)

    ServerParameters.asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    ServerParameters.tornadoinstance = tornado.ioloop.IOLoop.instance()
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.InitServer())

    ServerParameters.asyncioloop.create_task(parameters_dictionary.loadfromdatabase())

    tornado.ioloop.PeriodicCallback(parameters_dictionary.myloop,1000).start()#自定义循环协程

    ServerParameters.asyncioloop.run_forever()
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.DropServer())
