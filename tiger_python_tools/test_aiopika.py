import asyncio
from aio_pika import connect_robust, Message,ExchangeType
import aio_pika

async def process_incoming_message(message: aio_pika.IncomingMessage):
    print(message.body)
    await message.ack()
    #await message.reject(requeue=True)



async def setupconsume(loop):
    connection = await connect_robust(
        "amqp://guest:guest@a10.4s188.com:35132/",
        loop=loop
    )
    queuename = "testqueue"
    exchangename="testexchange"
    routing_key = "test.#"
    # Creating channel
    channel = await connection.channel()
    # Declaring exchange
    exchange = await channel.declare_exchange(exchangename,ExchangeType.TOPIC)
    # Declaring queue
    queue = await channel.declare_queue(queuename)
    # Binding queue
    await queue.bind(exchange, routing_key)
    # Set the callback
    await queue.consume(process_incoming_message)
    return connection




async def sendtestloop(loop):
    connection = await connect_robust(
        "amqp://guest:guest@a10.4s188.com:35132/",
        loop=loop
    )

    queue_name = "testqueue"
    exchangename="testexchange"
    routing_key = "test.#"

    # Creating channel
    channel = await connection.channel()

    # Declaring exchange
    exchange = await channel.declare_exchange(exchangename,ExchangeType.TOPIC)

    # Declaring queue
    queue = await channel.declare_queue(queue_name)

    # Binding queue
    await queue.bind(exchange, routing_key)

    while True:
        try:
            await exchange.publish(
                Message(
                    bytes('Hello', 'utf-8'),
                ),
                "test"
            )
            await asyncio.sleep(3)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(setupconsume(loop))

    loop.create_task(sendtestloop(loop))
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
