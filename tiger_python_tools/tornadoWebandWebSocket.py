import tornado.ioloop
import tornado.web
import tornado.websocket
import os.path

import json
import asyncio

from tornado.platform.asyncio import AsyncIOMainLoop
import tornado.gen

from config import ServerParameters

import vehicle_view_api_2 as vehicle_view_api
from pg_fileupload import upload_Handler as upload_Handler
from pg_filedownload import download_Handler as download_Handler
import motordownload
import motorupload

import sqlalchemy
from aiomysql.sa import create_engine
import logging


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class testapiHandler(tornado.web.RequestHandler):
    def post(self):
        self.write("test")

class WebSocketTestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("websocket.html")

class SocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    clients = set()

    @staticmethod
    def send_to_all(message):
        for c in SocketHandler.clients:
            c.write_message(json.dumps(message))

    def open(self):
        self.write_message(json.dumps({
            'type': 'sys',
            'message': 'Welcome to WebSocket',
        }))
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': str(id(self)) + ' has joined',
        })
        SocketHandler.clients.add(self)

    def on_close(self):
        SocketHandler.clients.remove(self)
        SocketHandler.send_to_all({
            'type': 'sys',
            'message': str(id(self)) + ' has left',
        })

    def on_message(self, message):
        SocketHandler.send_to_all({
            'type': 'user',
            'id': id(self),
            'message': message,
        })

class VehicleHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("vehicle_view.html")

settings = {

    'template_path': os.path.join(os.path.dirname(__file__), "views"),  # html文件
    'static_path': os.path.join(os.path.dirname(__file__), "static"),  # 静态文件（css,js,img）
    'cookie_secret': '61oETzKXQAGaYdkL5gEmGeJJFuYdasdfah7EQnp2',  # cookie自定义字符串加盐
    'autoreload': True,  # 自动重读网页，当刷新的时候
    # 'static_url_prefix': '/statics/',# 静态文件前缀
    # 'xsrf_cookies': True,          # 防止跨站伪造
    # 'ui_methods': mt,              # 自定义UIMethod函数
    # 'ui_modules': md,              # 自定义UIModule类
}

application = tornado.web.Application([
    (r"/about", MainHandler),
    (r"/vehicle", VehicleHandler),
    (r"/", IndexHandler),
    (r"/websocket", WebSocketTestHandler),
    (r"/chat", SocketHandler),
    (r"/testapi", testapiHandler),
    (r"/api/vehicle_view_api", vehicle_view_api.vehicle_view_Handler),
    (r"/api/download", download_Handler),
    (r"/api/upload", upload_Handler),
    (r"/assets/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/assets/"}),
    (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/css/"}),
    (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/images/"}),
    (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/js/"}),
    (r"/lib/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"] + "/lib/"}),

], **settings)

def mytestloop():
    ServerParameters.servercounter+=1
    logging.info(ServerParameters.servercounter)
    pass

if __name__ == "__main__":
    application.listen(8888)


    ServerParameters.asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    ServerParameters.tornadoinstance = tornado.ioloop.IOLoop.instance()
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.InitServer())

    #tornado.ioloop.PeriodicCallback(mytestloop,1000).start()

    ServerParameters.asyncioloop.run_forever()
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.DropServer())
