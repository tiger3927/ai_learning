import struct
import logging
import math
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base,DeclarativeMeta
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import json
import datetime
import decimal
from  PIL import Image
import io
import struct

import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
from email.header import Header
from email import encoders
import os,time,re
import mimetypes



def init_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s -%(module)s:%(filename)s-L%(lineno)d-%(levelname)s: %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logging.info("Current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))


def writenumberstringtobcd(s, count=6):
    if (type(s) is int):
        d1 = s
    else:
        d1 = int(s)
    bs = b""
    for i in range(count):
        d2 = d1 % 10
        d1 = d1 / 10
        b = int(d2)
        d2 = d1 % 10
        d1 = d1 / 10
        b = b + int(d2) * 16
        bs1 = struct.pack("B",b)
        bs = bs1 + bs
    return bs

def isPointInPolygon(point, rangelist):  #[[0,0],[1,1],[0,1],[0,0]] [1,0.8]
    # 判断是否在外包矩形内，如果不在，直接返回false
    lnglist = []
    latlist = []
    for i in range(len(rangelist)-1):
        lnglist.append(rangelist[i][0])
        latlist.append(rangelist[i][1])
    #print(lnglist, latlist)
    maxlng = max(lnglist)
    minlng = min(lnglist)
    maxlat = max(latlist)
    minlat = min(latlist)
    #print(maxlng, minlng, maxlat, minlat)
    if (point[0] > maxlng or point[0] < minlng or
        point[1] > maxlat or point[1] < minlat):
        return False
    count = 0
    point1 = rangelist[0]
    for i in range(1, len(rangelist)):
        point2 = rangelist[i]
        # 点与多边形顶点重合
        if (point[0] == point1[0] and point[1] == point1[1]) or (point[0] == point2[0] and point[1] == point2[1]):
            #print("在顶点上")
            return False
        # 判断线段两端点是否在射线两侧 不在肯定不相交 射线（-∞，lat）（lng,lat）
        if (point1[1] < point[1] and point2[1] >= point[1]) or (point1[1] >= point[1] and point2[1] < point[1]):
            # 求线段与射线交点 再和lat比较
            point12lng = point2[0] - (point2[1] - point[1]) * (point2[0] - point1[0])/(point2[1] - point1[1])
            #print(point12lng)
            # 点在多边形边上
            if (point12lng == point[0]):
                #print("点在多边形边上")
                return False
            if (point12lng < point[0]):
                count +=1
        point1 = point2
    #print(count)
    if count%2 == 0:
        return False
    else:
        return True

def distance(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

def calcangle(x1,y1,x2,y2):
    angle=0
    y_se= y2-y1
    x_se= x2-x1
    if x_se==0 and y_se>0:
        angle = 360
    if x_se==0 and y_se<0:
        angle = 180
    if y_se==0 and x_se>0:
        angle = 90
    if y_se==0 and x_se<0:
        angle = 270
    if x_se>0 and y_se>0:
       angle = math.atan(x_se/y_se)*180/math.pi
    elif x_se<0 and y_se>0:
       angle = 360 + math.atan(x_se/y_se)*180/math.pi
    elif x_se<0 and y_se<0:
       angle = 180 + math.atan(x_se/y_se)*180/math.pi
    elif x_se>0 and y_se<0:
       angle = 180 + math.atan(x_se/y_se)*180/math.pi
    return angle

def stringlenfrombytes(bs):
    count=0
    for x in bs:
        if (x!=0x00):
            count+=1
        else:
            break

    return count


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

#使用：   rts = json.dumps(objects, cls=AlchemyEncoder,ensure_ascii=False)# 加上ensure_ascii=False 是解决中文乱码问题

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:  # 添加了对datetime的处理
                    # print(type(data),data)
                    if isinstance(data, datetime.datetime):
                        fields[field] = data.strftime("%Y-%m-%d %H:%M:%S.%f")[
                                        :-3]  # SQLserver数据库中毫秒是3位，日期格式;2015-05-12 11:13:58.543
                    elif isinstance(data, datetime.date):
                        fields[field] = data.strftime("%Y-%m-%d")
                    elif isinstance(data, decimal.Decimal):
                        fields[field] = float(data)
                    else:
                        fields[field] = AlchemyEncoder.default(self, data)  # 如果是自定义类，递归调用解析JSON，这个是对象映射关系表 也加入到JSON
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


def GetCustomSmallPic(inputstream,cwidth,cheight,bscale = True):
    if (inputstream == None):
        return None
    size = [150,0]
    inputstream.seek(0)
    bbb=inputstream.read()
    img = Image.open(io.BytesIO(bbb))

    if (img == None):
        return None

    if (img.width <= cwidth and img.height <= cheight):
        return inputstream
    if (cwidth == 0 and cheight == 0):
        cwidth = img.width
        cheight = img.height
    else:
        if (cwidth == 0):
            cwidth = (cheight * img.width) / img.height
        if (cheight == 0):
            cheight = (cwidth * img.height) / img.width

    srcRect = [0, 0, img.width, img.height]

    if (bscale==True):
        if (img.width * 75 >= img.height * 100):# 宽度大, 变y
            x = cwidth
            y = (img.height * cwidth) / img.width
        else:
            x = (img.width * cheight) / img.height
            y = cheight
    else:
        x = cwidth
        y = cheight

    img=img.resize((int(x),int(y)))
    if (img.mode!="RGB"):
        img=img.convert("RGB")

    outstream=io.BytesIO()
    img.save(outstream,"JPEG")
    outstream.flush()
    return outstream

def WebApiResultJson(code,message,data=None):
    d=dict()
    d["code"]=code
    d["message"]=message
    d["data"]=data
    return json.dumps(d,cls=CJsonEncoder,ensure_ascii=False)

def BytestoBCD10(bsinput):
    if type(bsinput) is not bytes:
        return None
    p10=[]
    lll=len(bsinput)
    for i in range(10):
        if (2*i+1)>=lll:
            b1=0
        else:
            b1=bsinput[2*i+1]-0x30
            if b1>9:
                b1=9
        if (2*i+0)>=lll:
            b2=0
        else:
            b2=bsinput[2*i+0]-0x30
            if b2 > 9:
                b2 = 9
        p10.append(b2*0x10+b1)
    return struct.pack("BBBBBBBBBB",
                       p10[0],p10[1],p10[2],p10[3],p10[4],
                       p10[5],p10[6],p10[7],p10[8],p10[9])

def str_to_list(t_str):
    a_list = []
    for c in str(t_str):
        a_list.append(c)
    return a_list


def list_to_str(a_list):
    return "".join(list(map(str, a_list)))


def gcj02towgs(lon,lat):
    a = 6378245.0 # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323 #克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324 # 圆周率
    # 以下为转换公式
    x = lon - 105.0
    y = lat - 35.0
    # 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x));
    dLon += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0;
    dLon += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0;
    dLon += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0;
    #纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x));
    dLat += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0;
    dLat += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0;
    dLat += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0;
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI);
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI);
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return wgsLon,wgsLat


def SendMail(sender = '914843402@qq.com',
             receiver = '914843402@qq.com',
             subject = '',
             textcontent=None,
             htmlcontent=None,
             attachfilenamelist=[],
             smtpserver = 'smtp.qq.com',
             username = '914843402',
             password = 'izlvckkmrugjbcag'):

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    if (textcontent!=None):
        part1 = MIMEText(textcontent, 'plain')
        msgRoot.attach(part1)
    if (htmlcontent != None):
        part2 = MIMEText(htmlcontent, 'html')
        msgRoot.attach(part2)
    '''
    img1 = MIMEImage(open(pic_path, 'rb').read(), _subtype='octet-stream')
    img1.add_header('Content-ID', 'image1')
    msgRoot.attach(img1)
    '''
    for f in attachfilenamelist:
        ctype, encoding = mimetypes.guess_type(f)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype,subtype=ctype.split('/')
        filepath, filename = os.path.split(f)
        with open(f, 'rb') as fp:
            mb = MIMEBase(maintype,subtype)
            mb.set_payload(fp.read())
            mb.add_header('Content-Disposition', 'attachment', filename=filename)  # 修改邮件头
            encode_base64(mb)
            msgRoot.attach(mb)

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()



if __name__ == "__main__":  # 用于测试
    #print(WebApiResultJson(1,"你好",None))

    directory="C:\\Users\\tiger\\Desktop"
    filenames=[]
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        filenames.append(path)

    SendMail(subject="start mail",textcontent="content",attachfilenamelist=filenames)

    for x in BytestoBCD10(b"4422221111125dsfgsdfgsdfgsdfg"):
        print("%02x"%(x))
