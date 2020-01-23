from celerytesttask import query_users
from celery.result import AsyncResult
from celery import Task
from celery import Celery
from celery import apps

import asyncio
import time

import random

class A:
    count=0
    ioloop=None

@asyncio.coroutine
def test2():
    r = query_users.delay(2)
    res = AsyncResult(r.task_id)

    while (True):
        if (res.ready()==True):
            print(res.result)
            A.ioloop.stop()
            break
        else:
            yield from asyncio.sleep(0.01)

@asyncio.coroutine
def test3(n):
    i=0
    while(True):
        i+=1
        yield from asyncio.sleep(1)
        print("%s --- %s" %(n,i))

A.ioloop=asyncio.get_event_loop()
A.ioloop.create_task(test2())
#A.ioloop.create_task(test3(2))
#A.ioloop.create_task(test3(3))
A.ioloop.run_forever()
