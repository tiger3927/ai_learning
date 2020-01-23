import asyncio
import aioredis
import config

loop = None


async def go():
    redis = await aioredis.create_redis(
        (config.ServerParameters.redishost, config.ServerParameters.redisport), loop=loop)
    #await redis.set('my-key', 'value')
    val = await redis.get('ggoldh_autorec_a_86333212_0028504')
    print(val)
    redis.close()
    await redis.wait_closed()

if __name__ == "__main__":  # 用于测试
    loop = asyncio.get_event_loop()
    loop.run_until_complete(config.ServerParameters.InitServer())
    loop.run_until_complete(go())
