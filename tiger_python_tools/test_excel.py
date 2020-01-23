import xlrd
from dateutil import parser
import datetime
import time

# 测试在mysql上做些操作,读取excel内容更新数据库

xls = xlrd.open_workbook("C:\\Users\\tiger\\Desktop\\金宏联泰现金、银行存款日报表-2018.12.7.xlsx")
datasheet = xls.sheet_by_name("现金日记账")
rowcount = datasheet.nrows
mylist = []
myv=0.0
for y in range(1, rowcount):
    try:
        d = xlrd.xldate.xldate_as_datetime(datasheet.cell(y, 0).value, 0)
        c = str(datasheet.cell(y, 1).value)
        v = float(datasheet.cell(y, 3).value)
        if (d<parser.parse("2018/1/1") or d>parser.parse("2018/12/30")):
            continue
        if (not(c.find("孙德")>=0 or c.find("王继")>=0)):
            continue
        if (c.find("海尔")>=0):
            continue
        if (c.find("往来")>=0):
            continue
        # rdate=parser.parse(d)
        print(d, c,v)
        myv=myv+v
    except:
        print("error")
print(myv)