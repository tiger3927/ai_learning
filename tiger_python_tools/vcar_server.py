from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
import tigerfunctools
import struct


class Connection(object):
    clients = set()
    EOF = b"\x7E"
    sendcounter=0

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self.imei=b""
        self._stream = stream
        self._address = address
        self._stream.set_close_callback(self.on_close)
        self._stream.read_until(Connection.EOF, self.on_receive)
        # print("A new user has entered the chat room.", address)

    def on_receive(self, data):
        #print("R: " + ':'.join("%02x" % x for x in data))
        self._stream.read_until(Connection.EOF, self.on_receive)
        self.processmsg(data)

    def broadcast_messages(self, data):
        #print("User said:", data[:-1], self._address)
        for conn in Connection.clients:
            conn.sendmsg(0x8005,data)

    def on_close(self):
        Connection.clients.remove(self)
        print("closed: now connection num is:", len(Connection.clients))

    def sendmsg(self, msgid=0x0001, sendbuffer=b""):  # 打包
        if (not (type(sendbuffer) is bytes)):
            return

        bcds = tigerfunctools.writenumberstringtobcd(0)
        b1 = struct.pack(">HH6sH" + str(len(sendbuffer)) + "s", msgid, len(sendbuffer), bcds, self.sendcounter,
                         sendbuffer)
        self.sendcounter = self.sendcounter + 1

        b2 = bytearray(0)
        # 校验码
        xb = b1[0]
        for x in b1[1:]:
            xb = xb ^ x
        # 转义封包
        b2.append(0x7e)
        for x in b1:
            if (x == 0x7e):
                b2.append(0x7d)
                b2.append(2)
            elif (x == 0x7d):
                b2.append(0x7d)
                b2.append(1)
            else:
                b2.append(x)
        if (xb == 0x7e):
            b2.append(0x7d)
            b2.append(2)
        elif (xb == 0x7d):
            b2.append(0x7d)
            b2.append(1)
        else:
            b2.append(xb)
        b2.append(0x7e)
        # print("S: " + ':'.join("%02x" % x for x in b2))

        self._stream.write(b2)
        return

    def processmsg(self, data=b""):
        if (len(data) < 12):
            return
        b2 = bytearray(0)
        status = 0
        for d in data[:-1]:
            if (d == 0x7d):
                status = 1
            else:
                if (status == 0):
                    b2.append(d)
                else:
                    status = 0
                    if (d == 0x01):
                        b2.append(0x7D)
                    elif (d == 0x02):
                        b2.append(0x7E)
                    else:
                        continue
                # 出错了
        xb = b2[0]
        for d in b2[1:-1]:
            xb = xb ^ d
        if (xb != b2[-1]):
            # 校验码错误
            return
        unpack_list = struct.unpack(">HH6sH", b2[0:12])
        msgid = unpack_list[0]
        msgbodylen = unpack_list[1]
        msgflowid = unpack_list[3]
        # b2[12]开始是body
        if (msgid==0x0002):
            self.processmsg0002(data)

        return
    def processmsg0002(self,data):
        self.sendmsg(0x0002)
        return


class ChatServer(TCPServer):
    def handle_stream(self, stream, address):
        #print("New connection :", address, stream)
        Connection(stream, address)
        print("connection num is:", len(Connection.clients))


if __name__ == '__main__':
    print("Server start ......")
    server = ChatServer()
    server.listen(9999)
    IOLoop.instance().start()
