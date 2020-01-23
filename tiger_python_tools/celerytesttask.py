from celery import Celery
import time
import asyncio
import os

app = Celery("tasks", broker="amqp://guest:guest@a10.4s188.com:35132",backend="amqp://guest:guest@a10.4s188.com:35132",)
#app.conf.CELERY_RESULT_BACKEND = "amqp://guest:guest@a10.4s188.com:35132"
#app.conf.CELERYD_CONCURRENCY=5  #并发数量（进程）
#app.conf.CELERYD_PREFETCH_MULTIPLIER=5   #每次取出的任务数量
#app.conf.CELERYD_MAX_TASKS_PER_CHILD =200 #运行多少次，进程杀掉
#app.conf.CELERY_TASK_RESULT_EXPIRES = 1200 #超时时间
app.conf.update()


@app.task(name='task.query_users')
def query_users(i):
    # 耗时的数据库操作
    time.sleep(5) #模仿独占的工作
    print("task.query_users %s" % i)
    print(os.getpid())
    return i

if __name__ == "__main__":
    print(os.getpid())
    app.start()