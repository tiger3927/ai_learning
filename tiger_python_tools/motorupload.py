import tornado.websocket
from tornado.escape import utf8, _unicode
from gridfs import *
from bson.objectid import ObjectId
import config
import tigerfunctools
from dateutil import parser
import datetime
from urllib import parse as urlparse
import os
import json
import tornado.ioloop

from motor.motor_tornado import MotorClient,MotorGridFSBucket,MotorGridOut,MotorGridOutCursor
import asyncio
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado import gen
import io
from tornado import gen

class motorupload_Handler(tornado.web.RequestHandler):
    def get(self):
        self.write('''
        <html>
          <head><title>Upload File</title></head>
          <body>
            <form action='test' enctype="multipart/form-data" method='post'>
            <input type='file' name='test'/><br/>
            <input type='submit' value='submit'/>
            </form>
          </body>
        </html>
        ''')

    @gen.coroutine
    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        #文件的暂存路径
        filedb = "upload"
        if ("filedb" in inputdict.keys()):
            filedb=inputdict["filedb"].decode("utf-8")

        client = MotorClient(config.ServerParameters.mongodbpath)
        db = client.jt808
        filename = None
        fileid = None

        if (len(self.request.files)<=0):
            self.write(tigerfunctools.WebApiResultJson(1,"没有上传文件",None))
            return

        uploaderror=0

        for fk in self.request.files:
            files=self.request.files[fk]
            for meta in files:
                filename=meta['filename']
                bucket = MotorGridFSBucket(db, filedb)#,chunk_size_bytes=32768)

                up= bucket.open_upload_stream(filename)
                if (up==None):
                    self.write(tigerfunctools.WebApiResultJson(1, "写入数据库错误", None))
                    return

                fileid=up._id
                yield up.write(meta["body"])
                yield up.close()
                if (fileid==None):
                    uploaderror=uploaderror+1

        if (uploaderror==0):
            rrr=dict()
            rrr["id"]=str(fileid)
            rrr["filename"]=filename
            self.write(tigerfunctools.WebApiResultJson(0, "上传成功", rrr))
        else:
            self.write(tigerfunctools.WebApiResultJson(1,"有"+str(uploaderror)+"个文件上传出错",null))



def mytestloop():
    config.ServerParameters.servercounter+=1
    print(config.ServerParameters.servercounter)
    pass

if __name__ == '__main__':
    asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    tornadoinstance = tornado.ioloop.IOLoop.instance()

    #tornado.ioloop.PeriodicCallback(mytestloop,100).start()

    app = tornado.web.Application([
        (r'/test', motorupload_Handler),
    ])
    app.listen(3000)

    asyncioloop.run_forever()