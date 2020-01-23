from sqlalchemy import Column, Integer, String, SmallInteger, BigInteger, Float, Unicode, Boolean, Time, LargeBinary, \
    DATETIME
import asyncio
import sqlalchemy

from config import ServerParameters


def getsqlalchemytable():  # CORE操作层对象
    mysqlmetadata = sqlalchemy.MetaData()
    return sqlalchemy.Table('vehicle', mysqlmetadata,
                            # ID
                            Column('vehicleid', Integer, primary_key=True),
                            # 车牌号（可以为空，未上牌状态）
                            Column('vehiclenumber', Unicode(12), unique=True, nullable=True),
                            # 车辆VIN码
                            Column('vehiclevincode', Unicode(32), unique=True, nullable=True),
                            # 车辆有效
                            Column('vehicleenable', Boolean, nullable=True),
                            # 车辆上牌时间
                            Column('vehicledrivingpermit_inittime', DATETIME, nullable=True),
                            # 车辆年审状态
                            Column('vehicledrivingpermit_status', Unicode(12), nullable=True),
                            # 车辆行驶证编号
                            Column('vehicledrivingpermit_number', Unicode(20), index=True, nullable=True),
                            # 车辆行驶证扫描件文件名
                            Column('vehicledrivingpermit_scan', Unicode(64), nullable=True),
                            # 车辆行驶证颁发机构
                            Column('vehicledrivingpermit_goverment', Unicode(64), nullable=True),
                            # 车辆行驶证有效期起
                            Column('vehicledrivingpermit_starttime', DATETIME, nullable=True),
                            # 车辆行驶证有效截止
                            Column('vehicledrivingpermit_endtime', DATETIME, nullable=True),
                            # 车辆行驶证车辆分类
                            Column('vehicledrivingpermit_class', Unicode(12), nullable=True),
                            # 车辆运营证编号
                            Column('vehicleoperationpermit_number', Unicode(32), index=True, nullable=True),
                            # 车辆运营证扫描件文件名
                            Column('vehicleoperationpermit_scan', Unicode(64), nullable=True),
                            # 车辆运营证颁发机构
                            Column('vehicleoperationpermit_goverment', Unicode(32), nullable=True),
                            # 车辆运营证有效期起
                            Column('vehicleoperationpermit_starttime', DATETIME, nullable=True),
                            # 车辆运营证有效截止
                            Column('vehicleoperationpermit_endtime', DATETIME, nullable=True),
                            # 车辆属性自营挂靠其他
                            Column('vehicleoperationpermit_class', Unicode(12), nullable=True),
                            # 车辆服务类型（网约车，出租车，线路车，私人小汽车，货运车，施工机械）
                            Column('vehicleservice_type', Unicode(20), nullable=True),
                            # 车辆服务性质（自营，托管，其他）
                            Column('vehicleservicetype', Unicode(20), nullable=True),
                            # 车型系列
                            Column('vehicleseries', Unicode(32), nullable=True),
                            # 车型型号
                            Column('vehiclemodel', Unicode(32), nullable=True),
                            # 车辆生产厂家
                            Column('vehiclemanufacturer', Unicode(48), nullable=True),
                            # 车辆颜色
                            Column('vehiclecolor', Unicode(32), nullable=True),
                            # 车辆燃料类型（汽油，柴油，天然气，液化气，电动，混动，其他）
                            Column('vehiclefueltype', Unicode(32), nullable=True),
                            # 车辆发动机排量
                            Column('vehicleenginesize', Float, nullable=True),
                            # 车辆新能源电池容量
                            Column('vehiclebatterysize', Float, nullable=True),
                            # 车辆轴距
                            Column('vehiclewheelbase', Float, nullable=True),
                            # 车辆整备质量
                            Column('vehiclefullweight', Float, nullable=True),
                            # 车辆额定人数
                            Column('vehiclefullpoerson', Integer, nullable=True),
                            # 车辆载重量
                            Column('vehicleloadweight', Float, nullable=True),
                            # 车辆照片正面文件名
                            Column('vehiclephotofront', Unicode(64), nullable=True),
                            # 车辆照片侧面文件名
                            Column('vehiclephotoside', Unicode(64), nullable=True),
                            # 车辆照片尾部文件名
                            Column('vehiclephotoback', Unicode(64), nullable=True),
                            # 车辆监控设备安装日期
                            Column('vehiclegps_installtime', DATETIME, nullable=True),
                            # 车辆监控设备厂家
                            Column('vehiclegps_manufacturer', Unicode(48), nullable=True),
                            # 车辆监控设备型号
                            Column('vehiclegps_model', Unicode(48), nullable=True),
                            # 车辆监控设别序列号
                            Column('vehiclegps_deviceid', Unicode(48), index=True, nullable=True),
                            # 车辆发票打印设备厂家
                            Column('vehicleprint_manufacturer', Unicode(48), nullable=True),
                            # 车辆发票打印设备型号
                            Column('vehicleprint_model', Unicode(48), nullable=True),
                            # 车辆发票打印设备序列号
                            Column('vehicleprint_deviceid', Unicode(48), nullable=True),
                            # 车辆描述
                            Column('vehicledescription', Unicode(255), nullable=True),
                            # 车辆注册地
                            Column('vehiclesignin_address', Unicode(64), nullable=True),
                            # 车辆注册日期
                            Column('vehicleprint_time', DATETIME, nullable=True),
                            # 车辆所有人
                            Column('vehicleowner_name', Unicode(32), index=True, nullable=True),
                            # 车辆所有人身份证号码
                            Column('vehicleowner_cardid', Unicode(32), index=True, nullable=True),
                            # 车辆所有人电话号码
                            Column('vehicleowner_phone', Unicode(24), index=True, nullable=True),
                            # 车辆所有公司
                            Column('vehicleowner_company_name', Unicode(64), index=True, nullable=True),
                            # 车辆所有公司组织代码
                            Column('vehicleowner_company_cardid', Unicode(48), index=True, nullable=True),
                            # 车辆所有公司电话号码
                            Column('vehicleowner_company_phone', Unicode(24), index=True, nullable=True),
                            # 车辆所属平台公司
                            Column('vehiclebelongplat', Unicode(64), index=True, nullable=True),
                            # 车辆所属平台分公司
                            Column('vehiclebelongplat_child', Unicode(64), index=True, nullable=True),
                            # 车辆指定责任人姓名（可以是车主本人）
                            Column('vehiclemaster_name', Unicode(48), index=True, nullable=True),
                            # 车辆指定责任人身份证
                            Column('vehiclemaster_cardid', Unicode(48), index=True, nullable=True),
                            # 车辆指定责任人电话号码
                            Column('vehiclemaster_phone', Unicode(24), index=True, nullable=True)
                            )


class cvehicle:
    def __init__(self):
        pass


class vehicle(ServerParameters.BaseMySql):  # 高级ORM对象
    __tablename__ = 'vehicle'  # 表名

    # ID :
    vehicleid = Column(Integer, primary_key=True)
    # 车牌号（可以为空，未上牌状态） :
    vehiclenumber = Column(Unicode(12), unique=True, nullable=True)
    # 车辆VIN码 :
    vehiclevincode = Column(Unicode(32), unique=True, nullable=True)
    # 车辆有效 :
    vehicleenable = Column(Boolean, nullable=True)
    # 车辆上牌时间 :
    vehicledrivingpermit_inittime = Column(DATETIME, nullable=True)
    # 车辆年审状态 :
    vehicledrivingpermit_status = Column(Unicode(12), nullable=True)
    # 车辆行驶证编号 :
    vehicledrivingpermit_number = Column(Unicode(20), index=True, nullable=True)
    # 车辆行驶证扫描件文件名 :
    vehicledrivingpermit_scan = Column(Unicode(64), nullable=True)
    # 车辆行驶证颁发机构 :
    vehicledrivingpermit_goverment = Column(Unicode(64), nullable=True)
    # 车辆行驶证有效期起 :
    vehicledrivingpermit_starttime = Column(DATETIME, nullable=True)
    # 车辆行驶证有效截止 :
    vehicledrivingpermit_endtime = Column(DATETIME, nullable=True)
    # 车辆行驶证车辆分类 :
    vehicledrivingpermit_class = Column(Unicode(12), nullable=True)
    # 车辆运营证编号 :
    vehicleoperationpermit_number = Column(Unicode(32), index=True, nullable=True)
    # 车辆运营证扫描件文件名 :
    vehicleoperationpermit_scan = Column(Unicode(64), nullable=True)
    # 车辆运营证颁发机构 :
    vehicleoperationpermit_goverment = Column(Unicode(32), nullable=True)
    # 车辆运营证有效期起 :
    vehicleoperationpermit_starttime = Column(DATETIME, nullable=True)
    # 车辆运营证有效截止 :
    vehicleoperationpermit_endtime = Column(DATETIME, nullable=True)
    # 车辆属性自营挂靠其他 :
    vehicleoperationpermit_class = Column(Unicode(12), nullable=True)
    # 车辆服务类型（网约车，出租车，线路车，私人小汽车，货运车，施工机械） :
    vehicleservice_type = Column(Unicode(20), nullable=True)
    # 车辆服务性质（自营，托管，其他） :
    vehicleservicetype = Column(Unicode(20), nullable=True)
    # 车型系列 :
    vehicleseries = Column(Unicode(32), nullable=True)
    # 车型型号 :
    vehiclemodel = Column(Unicode(32), nullable=True)
    # 车辆生产厂家 :
    vehiclemanufacturer = Column(Unicode(48), nullable=True)
    # 车辆颜色 :
    vehiclecolor = Column(Unicode(32), nullable=True)
    # 车辆燃料类型（汽油，柴油，天然气，液化气，电动，混动，其他） :
    vehiclefueltype = Column(Unicode(32), nullable=True)
    # 车辆发动机排量 :
    vehicleenginesize = Column(Float, nullable=True)
    # 车辆新能源电池容量 :
    vehiclebatterysize = Column(Float, nullable=True)
    # 车辆轴距 :
    vehiclewheelbase = Column(Float, nullable=True)
    # 车辆整备质量 :
    vehiclefullweight = Column(Float, nullable=True)
    # 车辆额定人数 :
    vehiclefullpoerson = Column(Integer, nullable=True)
    # 车辆载重量 :
    vehicleloadweight = Column(Float, nullable=True)
    # 车辆照片正面文件名 :
    vehiclephotofront = Column(Unicode(64), nullable=True)
    # 车辆照片侧面文件名 :
    vehiclephotoside = Column(Unicode(64), nullable=True)
    # 车辆照片尾部文件名 :
    vehiclephotoback = Column(Unicode(64), nullable=True)
    # 车辆监控设备安装日期 :
    vehiclegps_installtime = Column(DATETIME, nullable=True)
    # 车辆监控设备厂家 :
    vehiclegps_manufacturer = Column(Unicode(48), nullable=True)
    # 车辆监控设备型号 :
    vehiclegps_model = Column(Unicode(48), nullable=True)
    # 车辆监控设别序列号 :
    vehiclegps_deviceid = Column(Unicode(48), index=True, nullable=True)
    # 车辆发票打印设备厂家 :
    vehicleprint_manufacturer = Column(Unicode(48), nullable=True)
    # 车辆发票打印设备型号 :
    vehicleprint_model = Column(Unicode(48), nullable=True)
    # 车辆发票打印设备序列号 :
    vehicleprint_deviceid = Column(Unicode(48), nullable=True)
    # 车辆描述 :
    vehicledescription = Column(Unicode(255), nullable=True)
    # 车辆注册地 :
    vehiclesignin_address = Column(Unicode(64), nullable=True)
    # 车辆注册日期 :
    vehicleprint_time = Column(DATETIME, nullable=True)
    # 车辆所有人 :
    vehicleowner_name = Column(Unicode(32), index=True, nullable=True)
    # 车辆所有人身份证号码 :
    vehicleowner_cardid = Column(Unicode(32), index=True, nullable=True)
    # 车辆所有人电话号码 :
    vehicleowner_phone = Column(Unicode(24), index=True, nullable=True)
    # 车辆所有公司 :
    vehicleowner_company_name = Column(Unicode(64), index=True, nullable=True)
    # 车辆所有公司组织代码 :
    vehicleowner_company_cardid = Column(Unicode(48), index=True, nullable=True)
    # 车辆所有公司电话号码 :
    vehicleowner_company_phone = Column(Unicode(24), index=True, nullable=True)
    # 车辆所属平台公司 :
    vehiclebelongplat = Column(Unicode(64), index=True, nullable=True)
    # 车辆所属平台分公司 :
    vehiclebelongplat_child = Column(Unicode(64), index=True, nullable=True)
    # 车辆指定责任人姓名（可以是车主本人） :
    vehiclemaster_name = Column(Unicode(48), index=True, nullable=True)
    # 车辆指定责任人身份证 :
    vehiclemaster_cardid = Column(Unicode(48), index=True, nullable=True)
    # 车辆指定责任人电话号码 :
    vehiclemaster_phone = Column(Unicode(24), index=True, nullable=True)


"""
CREATE TABLE `vehicle` (
  vehicleid int NOT NULL AUTO_INCREMENT COMMENT 'ID',
vehiclenumber VARCHAR(12.0)  DEFAULT null  COMMENT '车牌号（可以为空，未上牌状态）',
vehiclevincode VARCHAR(32.0)  DEFAULT null  COMMENT '车辆VIN码',
vehicleenable  BOOLEAN  DEFAULT true  COMMENT '车辆有效',
vehicledrivingpermit_inittime DATETIME  DEFAULT null  COMMENT '车辆上牌时间',
vehicledrivingpermit_status VARCHAR(12.0)  DEFAULT null  COMMENT '车辆年审状态',
vehicledrivingpermit_number VARCHAR(20.0)  DEFAULT null  COMMENT '车辆行驶证编号',
vehicledrivingpermit_scan VARCHAR(64.0)  DEFAULT null  COMMENT '车辆行驶证扫描件文件名',
vehicledrivingpermit_goverment VARCHAR(64.0)  DEFAULT null  COMMENT '车辆行驶证颁发机构',
vehicledrivingpermit_starttime DATETIME  DEFAULT null  COMMENT '车辆行驶证有效期起',
vehicledrivingpermit_endtime DATETIME  DEFAULT null  COMMENT '车辆行驶证有效截止',
vehicledrivingpermit_class VARCHAR(12.0)  DEFAULT null  COMMENT '车辆行驶证车辆分类',
vehicleoperationpermit_number VARCHAR(32.0)  DEFAULT null  COMMENT '车辆运营证编号',
vehicleoperationpermit_scan VARCHAR(64.0)  DEFAULT null  COMMENT '车辆运营证扫描件文件名',
vehicleoperationpermit_goverment VARCHAR(32.0)  DEFAULT null  COMMENT '车辆运营证颁发机构',
vehicleoperationpermit_starttime DATETIME  DEFAULT null  COMMENT '车辆运营证有效期起',
vehicleoperationpermit_endtime DATETIME  DEFAULT null  COMMENT '车辆运营证有效截止',
vehicleoperationpermit_class VARCHAR(12.0)  DEFAULT null  COMMENT '车辆属性自营挂靠其他',
vehicleservice_type VARCHAR(20.0)  DEFAULT null  COMMENT '车辆服务类型（网约车，出租车，线路车，私人小汽车，货运车，施工机械）',
vehicleservicetype VARCHAR(20.0)  DEFAULT null  COMMENT '车辆服务性质（自营，托管，其他）',
vehicleseries VARCHAR(32.0)  DEFAULT null  COMMENT '车型系列',
vehiclemodel VARCHAR(32.0)  DEFAULT null  COMMENT '车型型号',
vehiclemanufacturer VARCHAR(48.0)  DEFAULT null  COMMENT '车辆生产厂家',
vehiclecolor VARCHAR(32.0)  DEFAULT null  COMMENT '车辆颜色',
vehiclefueltype VARCHAR(32.0)  DEFAULT null  COMMENT '车辆燃料类型（汽油，柴油，天然气，液化气，电动，混动，其他）',
vehicleenginesize  FLOAT  DEFAULT 0  COMMENT '车辆发动机排量',
vehiclebatterysize  FLOAT  DEFAULT 0  COMMENT '车辆新能源电池容量',
vehiclewheelbase  FLOAT  DEFAULT 0  COMMENT '车辆轴距',
vehiclefullweight  FLOAT  DEFAULT 0  COMMENT '车辆整备质量',
vehiclefullpoerson  INT  DEFAULT 0  COMMENT '车辆额定人数',
vehicleloadweight  FLOAT  DEFAULT 0  COMMENT '车辆载重量',
vehiclephotofront VARCHAR(64.0)  DEFAULT null  COMMENT '车辆照片正面文件名',
vehiclephotoside VARCHAR(64.0)  DEFAULT null  COMMENT '车辆照片侧面文件名',
vehiclephotoback VARCHAR(64.0)  DEFAULT null  COMMENT '车辆照片尾部文件名',
vehiclegps_installtime DATETIME  DEFAULT null  COMMENT '车辆监控设备安装日期',
vehiclegps_manufacturer VARCHAR(48.0)  DEFAULT null  COMMENT '车辆监控设备厂家',
vehiclegps_model VARCHAR(48.0)  DEFAULT null  COMMENT '车辆监控设备型号',
vehiclegps_deviceid VARCHAR(48.0)  DEFAULT null  COMMENT '车辆监控设别序列号',
vehicleprint_manufacturer VARCHAR(48.0)  DEFAULT null  COMMENT '车辆发票打印设备厂家',
vehicleprint_model VARCHAR(48.0)  DEFAULT null  COMMENT '车辆发票打印设备型号',
vehicleprint_deviceid VARCHAR(48.0)  DEFAULT null  COMMENT '车辆发票打印设备序列号',
vehicledescription VARCHAR(255.0)  DEFAULT null  COMMENT '车辆描述',
vehiclesignin_address VARCHAR(64.0)  DEFAULT null  COMMENT '车辆注册地',
vehicleprint_time DATETIME  DEFAULT null  COMMENT '车辆注册日期',
vehicleowner_name VARCHAR(32.0)  DEFAULT null  COMMENT '车辆所有人',
vehicleowner_cardid VARCHAR(32.0)  DEFAULT null  COMMENT '车辆所有人身份证号码',
vehicleowner_phone VARCHAR(24.0)  DEFAULT null  COMMENT '车辆所有人电话号码',
vehicleowner_company_name VARCHAR(64.0)  DEFAULT null  COMMENT '车辆所有公司',
vehicleowner_company_cardid VARCHAR(48.0)  DEFAULT null  COMMENT '车辆所有公司组织代码',
vehicleowner_company_phone VARCHAR(24.0)  DEFAULT null  COMMENT '车辆所有公司电话号码',
vehiclebelongplat VARCHAR(64.0)  DEFAULT null  COMMENT '车辆所属平台公司',
vehiclebelongplat_child VARCHAR(64.0)  DEFAULT null  COMMENT '车辆所属平台分公司',
vehiclemaster_name VARCHAR(48.0)  DEFAULT null  COMMENT '车辆指定责任人姓名（可以是车主本人）',
vehiclemaster_cardid VARCHAR(48.0)  DEFAULT null  COMMENT '车辆指定责任人身份证',
vehiclemaster_phone VARCHAR(24.0)  DEFAULT null  COMMENT '车辆指定责任人电话号码',

  PRIMARY KEY (`vehicleid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT ='车辆' ;
 
create unique index idx_vehiclenumber on vehicle (vehiclenumber) ;  
create unique index idx_vehiclevincode on vehicle (vehiclevincode) ;           
create index idx_vehicledrivingpermit_number on vehicle (vehicledrivingpermit_number) ;                
create index idx_vehicleoperationpermit_number on vehicle (vehicleoperationpermit_number) ;                                                                         
create index idx_vehiclegps_deviceid on vehicle (vehiclegps_deviceid) ;                   
create index idx_vehicleowner_name on vehicle (vehicleowner_name) ; 
create index idx_vehicleowner_cardid on vehicle (vehicleowner_cardid) ; 
create index idx_vehicleowner_phone on vehicle (vehicleowner_phone) ; 
create index idx_vehicleowner_company_name on vehicle (vehicleowner_company_name) ; 
create index idx_vehicleowner_company_cardid on vehicle (vehicleowner_company_cardid) ; 
create index idx_vehicleowner_company_phone on vehicle (vehicleowner_company_phone) ; 
create index idx_vehiclebelongplat on vehicle (vehiclebelongplat) ; 
create index idx_vehiclebelongplat_child on vehicle (vehiclebelongplat_child) ; 
create index idx_vehiclemaster_name on vehicle (vehiclemaster_name) ; 
create index idx_vehiclemaster_cardid on vehicle (vehiclemaster_cardid) ; 
create index idx_vehiclemaster_phone on vehicle (vehiclemaster_phone) ;

"""
