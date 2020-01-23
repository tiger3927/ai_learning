from config import ServerParameters, logging, datafilepath
import asyncio
from dateutil import parser
import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from asyncio.coroutines import coroutine
from pymongo.errors import AutoReconnect
from ffmpy import FFmpeg
import os


def cut_change(video_path, out_path, out_path2, out_path3, base_path, fps_r):
    """
    操作ffmpeg执行
    :param video_path: 处理输入流视频
    :param out_path: 合成缩略图 10×10
    :param out_path2: 封面图路径
    :param out_path3: 合成Ts流和 *.m3u8文件
    :param fps_r: 对视频帧截取速度
    """
    ff = FFmpeg(inputs={video_path: None},
                outputs={out_path: '-f image2 -vf fps=fps={},scale=180*75,tile=10x10'.format(fps_r),
                         out_path2: '-y -f mjpeg -ss 0 -t 0.001',
                         None: '-c copy -map 0 -y -f segment -segment_list {0} -segment_time 1  -bsf:v h264_mp4toannexb  {1}/cat_output%03d.ts'.format(
                             out_path3, base_path),
                         })
    print(ff.cmd)
    ff.run()


def converttstoh264(inputfilename, outputfilename):
    ff = FFmpeg(
        inputs={inputfilename: None},
        outputs={outputfilename: '-strict -2 -b:v 1000K -vcodec h264'}
    )
    print(ff.cmd)
    # ffmpeg -i inputfilename -strict -2 -vcodec h264 outputfilename
    ff.run()


async def findallhdmp4(stime):
    print("begin")
    mp4list = []
    client = AsyncIOMotorClient(ServerParameters.mongodbpath)
    db = client.jt808
    cursor = db["Web_EventUpload"].find({"EventTime": {'$gt': stime}})
    count = 0
    fileidlist = []
    try:

        list1 = await cursor.to_list(100)
        '''
        while (await cursor.fetch_next):
            count += 1
            print(count)
            datafileid= cursor.next_object()["datafileid"]
            print(datafileid)
            '''
        for x in list1:
            x[""]
        print(list1)
    except BaseException as e:
        logging.error(e)
        pass

    print("over")

    return


async def findlargemp4fileffmpeg(starttime, endtime):
    #print("begin findlargemp4fileffmpeg")
    mp4list = []
    client = AsyncIOMotorClient(ServerParameters.mongodbpath)
    db = client.jt808

    bucket = AsyncIOMotorGridFSBucket(db, "eventuploadvideos")
    cursor = bucket.find({"uploadDate": {'$gt': starttime,
                                         '$lte': endtime}, "filename": {"$regex": ".mp4$"}})
    filelist = await cursor.to_list(100000)

    ccount=0
    for fi in filelist:
        if fi["length"] > 1000000:
            print(fi)
            if os.path.exists(fi["filename"]):
                os.remove(fi["filename"])
            ds = await bucket.open_download_stream(fi["_id"])
            f = open("input"+fi["filename"], 'wb')
            bbb = await ds.read()
            f.write(bbb)
            f.close()
            ds.close()
            converttstoh264("input"+fi["filename"], fi["filename"])
            if os.path.exists("input"+fi["filename"]):
                os.remove("input"+fi["filename"])
            # 保存到bucket
            try:
                if os.path.exists(fi["filename"]):
                    uf=open(fi["filename"],"rb")
                    ubbb=uf.read()
                    uf.close()
                    os.remove(fi["filename"])
                    bucket.delete(fi["_id"])
                    uds = bucket.open_upload_stream_with_id(fi["_id"], fi["filename"])
                    await uds.write(ubbb)
                    uds.close()
                    ccount=ccount+1
                    logging.info("convert %s %s",fi["_id"],fi["filename"])
            except BaseException as e:
                logging.error(e)
    logging.info("end findlargemp4fileffmpeg total %s convert %s",len(filelist),ccount)
    return


async def loop():
    while True:
        endtime = datetime.datetime.utcnow()
        starttime = endtime+datetime.timedelta(0, -60*60*48, 0)
        #logging.info("起始时间-结束时间 %s %s", starttime, endtime)
        await findlargemp4fileffmpeg(starttime, endtime)
        await asyncio.sleep(10)
    return


if __name__ == "__main__":  # 用于测试
    ServerParameters.asyncioloop = asyncio.get_event_loop()
    ServerParameters.asyncioloop.run_until_complete(
        ServerParameters.InitServer(servertype="convertmp4_h264_task"))
    #ServerParameters.asyncioloop.call_later(1, loop)
    ServerParameters.asyncioloop.create_task(loop())
    ServerParameters.asyncioloop.run_forever()
    # ServerParameters.asyncioloop.run_until_complete(ServerParameters.DropServer())
