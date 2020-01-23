import pika
import random


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag = method.delivery_tag)



if __name__ == "__main__":
    credentials = pika.PlainCredentials('guest', 'guest')
    #这里可以连接远程IP，请记得打开远程端口  
    parameters = pika.ConnectionParameters('a10.4s188.com',35132,'/',credentials)  
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    #接收消息，只是根据queue，发送消息，会需要exchange
    channel.exchange_declare("testexchange","topic")
    channel.queue_declare(queue='testqueue')  

    #把队列queue绑定到一个分配器exchange上，
    #关键是路由规则key，任何队列可以到任何分配器，靠规则分配
    channel.queue_bind("testqueue","testexchange","test.#")

    number = random.randint(1,1000)
    body = 'hello world:%s' %number
    channel.basic_publish(exchange='testexchange', 
                            routing_key='test',  
                            body=body)  
    print("Sent %s" % body)

    channel.basic_consume(callback,
                      queue='testqueue',no_ack=False)
    channel.start_consuming()


    connection.close()  
