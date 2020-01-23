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
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado import gen
import asyncio
import uuid
import os
from PIL import Image
import io
from urllib import parse as urlparse

class download_Handler(tornado.web.RequestHandler):
    async def post(self):
        self.flush()
        pass

    async def get(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())

        filename = None
        filedb = ""
        smaxwidth = None
        smaxheight = None
        id = None

        if ("filedb" in inputdict.keys()):
            filedb = inputdict["filedb"].decode("utf-8")
        if ("id" in inputdict.keys()):
            id = inputdict["id"].decode("utf-8")
            if (id.isnumeric() == True):
                async with ServerParameters.pg_pool.acquire() as conn:  # 查询数据库得到文件名
                    row = await conn.fetchrow("select * from files where files_id=$1;", int(id))
                    if row != None:
                        filename = row["files_savefilename"]
                        filedb = row["files_fileid"]
            else:
                filename = id
        else:
            if ("filename" in inputdict.keys()):
                filename = inputdict["filename"].decode("utf-8")

        if filename == None:
            self.set_status(404)
            return
        if len(filedb) > 0:
            filedb = filedb + "/"  # 加上路径符号

        if ("maxwidth" in inputdict.keys()):
            smaxwidth = inputdict["maxwidth"].decode("utf-8")
        if ("maxheight" in inputdict.keys()):
            smaxheight = inputdict["maxheight"].decode("utf-8")

        maxwidth = 0
        maxheight = 0
        if (smaxwidth != None):
            maxwidth = int(smaxwidth)
        if (smaxheight != None):
            maxheight = int(smaxheight)

        maxstr = ""
        if (maxwidth != 0 or maxheight != 0):
            maxstr = str(maxwidth) + "_" + str(maxheight)

        f = open(ServerParameters.filespath + filedb + filename, "rb")
        m_time =  datetime.datetime.fromtimestamp(os.path.getmtime(ServerParameters.filespath + filedb + filename))

        r_time = utf8(self.request.headers.get("If-Modified-Since", ""))
        if (len(r_time) > 8):
            r_time = parser.parse(r_time)
            if (r_time == m_time):
                self.set_status(304)  # 文件相同
                return

        isimage = False
        f.seek(0, 2)
        filelength = f.tell()
        isresize = False
        newds = None

        if (filename.find(".jpg") >= 0 or filename.find(".bmp") >= 0 or filename.find(".gif") >= 0 or filename.find(
                ".png") >= 0):
            isimage = True
            if (maxheight == 0 and maxwidth == 0):
                newds = None
            else:
                newds = AsycnGetCustomSmallPic(f, maxwidth, maxheight)
                if (newds != None):
                    newds.seek(0, 2)
                    filelength = newds.tell()
                    isresize = True
                    newds.seek(0, 0)

        '''
        etag = str(fi.upload_date) + str(filelength)
        self.set_header("Etag", etag)

        if (self.check_etag_header()==True):
            ds.close()
            newds.close()
            self.set_status(304)
            return
        '''

        p = 0
        range = self.request.headers.get("Range", "")
        if (len(range) > 0):
            self.set_status(205)  # 断点续传
            p = int(range.replace("bytes=", "").replace("-", ""))
            if (p >= filelength):
                return
        self.set_header("Content-Range", "bytes " + str(p) + "-" + str(filelength - 1) + "/" + str(filelength))
        self.set_header("Content-Length", str(filelength - p))
        if (isimage == True):
            self.set_header("Content-Type", "image/" + "jpg")
        else:
            self.set_header("Content-Type", "application/octet-stream")
        if (isresize):
            self.set_header("Content-Disposition", "attachment;" + urlparse.urlencode({"filename": maxstr + filename}))
        else:
            self.set_header("Content-Disposition", "attachment;" + urlparse.urlencode({"filename": filename}))
        self.add_header("Date", datetime.datetime.now())  # .strftime("%a, %d %h %Y %H:%M:%S GMT")
        self.add_header("Last-Modified", m_time)
        self.add_header("Expires", datetime.datetime.now() + datetime.timedelta(days=365))
        self.set_header("Cache-Control: public", True)

        if (isresize):
            newds.seek(p)
            bbb = newds.read()
            self.write(bbb[p:])
        else:
            f.seek(p)
            bbb = f.read()
            self.write(bbb)

        if (newds != None):
            newds.close()
        if (f != None):
            f.close()
        self.flush()


def AsycnGetCustomSmallPic(inputstream, cwidth, cheight, bscale=True):
    if (inputstream == None):
        return None
    size = [150, 0]
    inputstream.seek(0)
    bbb = inputstream.read()
    img = Image.open(io.BytesIO(bbb))

    if (img == None):
        return None

    if (img.width <= cwidth and img.height <= cheight):
        return None
    if (cwidth == 0 and cheight == 0):
        cwidth = img.width
        cheight = img.height
    else:
        if (cwidth == 0):
            cwidth = (cheight * img.width) / img.height
        if (cheight == 0):
            cheight = (cwidth * img.height) / img.width

    srcRect = [0, 0, img.width, img.height]

    if (bscale == True):
        if (img.width * 75 >= img.height * 100):  # 宽度大, 变y
            x = cwidth
            y = (img.height * cwidth) / img.width
        else:
            x = (img.width * cheight) / img.height
            y = cheight
    else:
        x = cwidth
        y = cheight

    img = img.resize((int(x), int(y)))
    if (img.mode != "RGB"):
        img = img.convert("RGB")

    outstream = io.BytesIO()
    img.save(outstream, "JPEG")
    outstream.flush()
    return outstream


if __name__ == '__main__':
    asyncioloop = asyncio.get_event_loop()
    AsyncIOMainLoop().install()
    tornadoinstance = tornado.ioloop.IOLoop.instance()

    app = tornado.web.Application([
        (r'/test', download_Handler),
    ])
    app.listen(3000)

    asyncioloop.run_forever()
