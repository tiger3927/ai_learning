import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.escape import utf8, _unicode
from pymongo import MongoClient
from gridfs import *
from bson.objectid import ObjectId
import config
import tigerfunctools
from dateutil import parser
import datetime
from urllib import parse as urlparse

class mongodownload_Handler(tornado.web.RequestHandler):
    def get(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())

        filename = None
        filedb = "upload"
        smaxwidth = None
        smaxheight = None
        id = None
        if ("id" in inputdict.keys()):
            id=inputdict["id"].decode("utf-8")
        if ("filename" in inputdict.keys()):
            filename=inputdict["filename"].decode("utf-8")
        if ("filedb" in inputdict.keys()):
            filedb=inputdict["filedb"].decode("utf-8")
        if ("maxwidth" in inputdict.keys()):
            smaxwidth=inputdict["maxwidth"].decode("utf-8")
        if ("maxheight" in inputdict.keys()):
            smaxheight=inputdict["maxheight"].decode("utf-8")

        maxwidth = 0
        maxheight = 0
        if (smaxwidth != None):
            maxwidth = int(smaxwidth)
        if (smaxheight != None):
            maxheight = int(smaxheight)

        maxstr = ""
        if (maxwidth != 0 or maxheight != 0):
            maxstr = str(maxwidth) + "_" + str(maxheight)

        if (filename == None):
            filename = "goldhonor.jpg"

        client = MongoClient(config.ServerParameters.mongodbpath)
        db = client.jt808

        bucket=GridFSBucket(db,filedb)
        if (id!=None):
            fs=bucket.find({"_id":ObjectId(id)})
        else:
            fs=bucket.find({"filename":filename})
        if (fs==None):
            return
        if (fs.count()<=0):
            return
        fi=fs[0]

        filename=fi.filename
        m_time=fi.upload_date

        r_time=utf8(self.request.headers.get("If-Modified-Since", ""))
        if (len(r_time)>8):
            r_time=parser.parse(r_time)
            if (r_time==m_time):
                self.set_status(304)
                return

        ds=bucket.open_download_stream(fi._id)  #,dict( CheckMD5 = False, Seekable = True )
        if (ds==None):
            return

        isimage = False
        filelength = fi.length
        isresize = False
        newds=None
        if (filename.find(".jpg")>=0 or filename.find(".bmp")>=0 or filename.find(".gif")>=0 or filename.find(".png")>=0):
            isimage=True
            if (maxheight == 0 and maxwidth == 0):
                newds=None
            else:
                newds = tigerfunctools.GetCustomSmallPic(ds, maxwidth, maxheight)
                if (newds != None):
                    newds.seek(0,2)
                    filelength=newds.tell()
                    isresize = True
                    newds.seek(0,0)

        '''
        etag = str(fi.upload_date) + str(filelength)
        self.set_header("Etag", etag)

        if (self.check_etag_header()==True):
            ds.close()
            newds.close()
            self.set_status(304)
            return
        '''

        p=0
        range = self.request.headers.get("Range", "")
        if (len(range)>0):
            self.set_status(205)#断点续传
            p = int(range.replace("bytes=", "").replace("-", ""))
            if (p>=filelength):
                return
        self.set_header("Content-Range","bytes " + str(p) + "-" +str(filelength - 1) + "/" + str(filelength))
        self.set_header("Content-Length",str(filelength-p))
        if (isimage==True):
            self.set_header("Content-Type", "image/" + "jpg")
        else:
            self.set_header("Content-Type", "application/octet-stream")
        if (isresize):
            self.set_header("Content-Disposition","attachment;"+urlparse.urlencode({"filename":maxstr+filename}))
        else:
            self.set_header("Content-Disposition", "attachment;"+urlparse.urlencode({"filename":filename}))
        self.add_header("Date",datetime.datetime.now()) #.strftime("%a, %d %h %Y %H:%M:%S GMT")
        self.add_header("Last-Modified",m_time)
        self.add_header("Expires",datetime.datetime.now() + datetime.timedelta(days = 365))
        self.set_header("Cache-Control: public",True)

        if (isresize):
            newds.seek(p,0)
            bbb=newds.read()
            self.write(bbb[p:])
        else:
            ds.seek(p)
            bbb=ds.read()
            self.write(bbb)

        if (newds!=None):
            newds.close()
        if (ds!=None):
            ds.close()
        return