import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.autoreload
import os.path
import json
import vcar_car
import vcar_server
import asyncio
from tornado.platform.asyncio import AsyncIOMainLoop

from aiohttp import ClientSession

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("vcar_setting.html")

class TestMapHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("vcar_testmap.html")

class UserHandler(tornado.web.RequestHandler):
    def post(self):
        user_name = self.get_argument("username")
        user_email = self.get_argument("email")
        user_website = self.get_argument("website")
        user_language = self.get_argument("language")
        self.render("user.html",username=user_name,email=user_email,website=user_website,language=user_language)


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
    (r"/about", MainHandler),
    (r"/", IndexHandler),
    (r"/testmap", TestMapHandler),
    (r"/user", UserHandler),
    (r"/websocket", WebSocketTestHandler),
    (r"/chat", SocketHandler),
    (r"/testapi", testapiHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    instance = tornado.ioloop.IOLoop.instance()
    asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    vcar_car.vcar_main(instance,asyncioloop)
    asyncioloop.run_forever()