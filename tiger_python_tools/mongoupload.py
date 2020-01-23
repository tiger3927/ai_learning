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
from pymongo import MongoClient


class mongoupload_Handler(tornado.web.RequestHandler):

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

    def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        #文件的暂存路径
        filedb = "upload"
        if ("filedb" in inputdict.keys()):
            filedb=inputdict["filedb"].decode("utf-8")

        client = MongoClient(config.ServerParameters.mongodbpath)
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
                bucket = GridFSBucket(db, filedb,chunk_size_bytes=32768)
                fileid=None
                with bucket.open_upload_stream(filename) as up:
                    fileid=up._id
                    up.write(meta["body"])
                    up.close()
                if (fileid==None):
                    uploaderror=uploaderror+1

        if (uploaderror==0):
            rrr=dict()
            rrr["id"]=str(fileid)
            rrr["filename"]=filename
            self.write(tigerfunctools.WebApiResultJson(0, "上传成功", rrr))
        else:
            self.write(tigerfunctools.WebApiResultJson(1,"有"+str(uploaderror)+"个文件上传出错",null))
        #upload_path=os.path.join(os.path.dirname(__file__),'files')
        #filepath = os.path.join(upload_path, filename)
        #with open(filepath, 'wb') as up:
        #    up.write(meta['body'])



if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/test', mongoupload_Handler),
    ])
    app.listen(3000)
    tornado.ioloop.IOLoop.instance().start()




