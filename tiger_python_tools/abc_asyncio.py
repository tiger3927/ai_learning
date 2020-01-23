import asyncio
import time
from aiohttp import ClientSession

async def slow_operation(n):#协程中只能用异步操作的函数库
    await asyncio.sleep(1)
    print("Slow operation {} complete".format(n))


async def main():
    start = time.time()
    await slow_operation(4)
    await slow_operation(5)
    await slow_operation(6)
    await asyncio.wait([slow_operation(1),
        slow_operation(2),
        slow_operation(3),
    ])
    end = time.time()
    print('Complete in {} second(s)'.format(end-start))


url = "https://www.baidu.com/{}"
async def hello(url):
    async with ClientSession() as session:
        async with session.post(url) as response:
            response = await response.read()
            print(response)
            print('Hello World:%s' % time.time())


loop = asyncio.get_event_loop()
loop.create_task(slow_operation(4))         #不等待，只创建协程
loop.create_task(slow_operation(5))
loop.create_task(slow_operation(6))

loop.run_until_complete(hello("https://www.baidu.com/"))
#loop.run_until_complete(slow_operation(1))  #等待执行完毕
#loop.run_until_complete(slow_operation(2))
#loop.run_until_complete(slow_operation(3))
#loop.run_until_complete(main())