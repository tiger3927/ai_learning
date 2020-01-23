from config import ServerParameters,logging,datafilepath
import asyncio
from dateutil import parser
import datetime
#from motor.motor_tornado import MotorClient,MotorGridFSBucket,MotorGridOut,MotorGridOutCursor
from motor.motor_asyncio import AsyncIOMotorClient
from asyncio.coroutines import coroutine
from pymongo.errors import AutoReconnect


async def findallhdmp4(stime):
    print("begin")
    mp4list=[]
    client=AsyncIOMotorClient(ServerParameters.mongodbpath)
    db=client.jt808
    cursor = db["Web_EventUpload"].find({"EventTime":{'$gt':stime}})
    count=0
    try:
        list1=await cursor.to_list(100)
        '''
        while (await cursor.fetch_next):
            count += 1
            print(count)
            datafileid= cursor.next_object()["datafileid"]
            print(datafileid)
            '''
        print(list1)
    except BaseException as e:
        logging.error(e)
        pass

    print("over")


    return


async def loop():
    while True:
        n=datetime.datetime.utcnow()+datetime.timedelta(0,-6000,0)
        logging.info("起始时间-结束时间 %s %s",n,datetime.datetime.utcnow())
        await findallhdmp4(n)
        print("over2")
        await asyncio.sleep(5)
    return


if __name__ == "__main__":  # 用于测试
    ServerParameters.asyncioloop = asyncio.get_event_loop()
    ServerParameters.asyncioloop.run_until_complete(ServerParameters.InitServer(servertype="convertmp4_h264_task"))
    #ServerParameters.asyncioloop.call_later(1, loop)
    ServerParameters.asyncioloop.create_task(loop())
    ServerParameters.asyncioloop.run_forever()
    #ServerParameters.asyncioloop.run_until_complete(ServerParameters.DropServer())