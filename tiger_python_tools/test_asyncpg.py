import asyncio
import asyncpg


async def run():
    #conn = await asyncpg.connect(user='postgres', password='tongji12',
    #                             database='postgres', host='a10.4s188.com',port=35112)
    conn = await asyncpg.connect(user='postgres', password='tongji12',
                                 database='goldhonor', host='factory.goldhonor.com',port=15432)
    values = await conn.fetch('SELECT * FROM pg_type')
    print(values[0])
    print(type(values[0]))

    print(values[0]["typname"])
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())