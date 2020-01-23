import asyncio
import aioredis

loop = asyncio.get_event_loop()
redis = None

counter=0

async def start():
    global redis

    redis = await aioredis.create_redis_pool(
        ('a10.4s188.com', 35179),
        minsize=50, maxsize=500,
        loop=loop)
    await redis.set('my-key', 'value')
    val = await redis.get('my-key')
    print(val)


async def end():
    global redis

    redis.close()
    await redis.wait_closed()

async def read():
    global counter
    global resis

    counter=counter+1
    print(counter)
    await redis.set('my-key', 'value '+str(counter))
    val = await redis.get('my-key')
    print(val)

loop.run_until_complete(start())

tasks=[]
for i in range(20000):
    t=loop.create_task(read())
    tasks.append(t)

loop.run_until_complete(asyncio.gather(*tasks))


loop.run_until_complete(end())
