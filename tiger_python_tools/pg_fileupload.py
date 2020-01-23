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
import asyncio
import uuid
import os

class upload_Handler(tornado.web.RequestHandler):
    async def get(self):
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
        self.flush()

    async def post(self):
        inputdict = dict((k, v[-1]) for k, v in self.request.arguments.items())
        #文件的暂存路径
        filedb = ""
        subfilepath=""
        if ("filedb" in inputdict.keys()):
            filedb=inputdict["filedb"].decode("utf-8")
            subfilepath=filedb+"/"
            if (not (os.path.exists(ServerParameters.filespath+subfilepath))):
                os.makedirs(ServerParameters.filespath+subfilepath)

        async with ServerParameters.pg_pool.acquire() as conn:
            if (len(self.request.files)<=0):
                self.write(tigerfunctools.WebApiResultJson(1,"没有上传文件",None))
                return
            for fk in self.request.files:
                files=self.request.files[fk]
                for meta in files:
                    filename=meta['filename']
                    ext = os.path.splitext(filename)[-1]
                    savefilename=str(uuid.uuid4())+ext
                    f=open(ServerParameters.filespath+subfilepath+savefilename,"wb")
                    f.write(meta["body"])
                    filesize=len(meta["body"])
                    f.close()

                    result=await conn.execute("""insert into files 
                                        (files_filename,
                                        files_savefilename,
                                        files_saveindexfilename,
                                        files_uploadtime,
                                        files_modifytime,
                                        files_filedb,
                                        files_filesize,
                                        files_owner,
                                        files_organization) 
                                        values($1,$2,$3,$4,$5,$6,$7,$8,$9);""",
                                        filename,
                                        savefilename,
                                        "",
                                        datetime.datetime.utcnow(),
                                        datetime.datetime.utcnow(),
                                        filedb,
                                        filesize,
                                        "",
                                        ""
                                        )
                    print(result)

            rrr=dict()
            rrr["id"]=savefilename
            rrr["filename"]=filename
            self.write(tigerfunctools.WebApiResultJson(0, "上传成功", rrr))





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


"""

CREATE TABLE files
(
    files_id serial NOT NULL,
    files_filename varchar(64)    NOT NULL  ,
    files_savefilename varchar(64)    NOT NULL  ,
    files_saveindexfilename varchar(64)    NOT NULL  ,
	files_uploadtime timestamp    NOT NULL ,
	files_modifytime timestamp   ,
	files_filedb  varchar(32) DEFAULT '',
	files_filesize integer DEFAULT 0,
	files_owner varchar(32) DEFAULT NULL,
	files_organization varchar(32) DEFAULT NULL,
	files_info jsonb,
    PRIMARY KEY (files_id)
);

comment on column files.files_id is 'ID';
comment on column files.files_filename is '文件名';
comment on column files.files_savefilename is '存储文件名';
comment on column files.files_saveindexfilename is '索引文件名';
comment on column files.files_uploadtime is '上传时间';
comment on column files.files_modifytime is '修改时间';
comment on column files.files_filedb is '路径库';
comment on column files.files_filesize is '文件大小';
comment on column files.files_owner is '所有者';
comment on column files.files_organization is '所有组织';
comment on column files.files_info is '其他信息';

CREATE UNIQUE INDEX uidx_files_savefilename ON files (files_savefilename); 
CREATE INDEX idx_files_filename ON files (files_filename);                
CREATE INDEX idx_files_info on files using gin(files_info);

"""