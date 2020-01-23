from sqlalchemy import Column, Integer, String,SmallInteger,BigInteger,Float,Unicode,Boolean,Time,LargeBinary,DATETIME
import asyncio
import sqlalchemy

from config import ServerParameters

def getsqlalchemytable():    #CORE操作层对象
	mysqlmetadata = sqlalchemy.MetaData()
	return sqlalchemy.Table('dictionarytype', mysqlmetadata,
					#ID
					Column('dictionarytype_id',  Integer  ,primary_key=True       ),
					#字典类型名称
					Column('dictionarytype_name',  Unicode(64)   ,index=True      ),
					#字典类型描述
					Column('dictionarytype_description',  Unicode(128)     ,nullable=True    ),
					#字典类型索引
					Column('dictionarytype_typeid',  Integer   ,index=True      ),
					#字典类型更新时间
					Column('dictionarytype_updatetime',  DATETIME     ,nullable=True    )
					)


class cdictionarytype:
	def __init__(self):
		pass

				   
	
	
class dictionarytype(ServerParameters.BaseMySql):  #高级ORM对象
	__tablename__ = 'dictionarytype' #表名

	#ID :
	dictionarytype_id = Column(  Integer  ,primary_key=True       )
	#字典类型名称 :
	dictionarytype_name = Column(  Unicode(64)   ,index=True      )
	#字典类型描述 :
	dictionarytype_description = Column(  Unicode(128)     ,nullable=True    )
	#字典类型索引 :
	dictionarytype_typeid = Column(  Integer   ,index=True      )
	#字典类型更新时间 :
	dictionarytype_updatetime = Column(  DATETIME     ,nullable=True    )





"""
CREATE TABLE `dictionarytype` (
  dictionarytype_id int NOT NULL AUTO_INCREMENT COMMENT 'ID',
dictionarytype_name VARCHAR(64)  DEFAULT null  COMMENT '字典类型名称',
dictionarytype_description VARCHAR(128)  DEFAULT null  COMMENT '字典类型描述',
dictionarytype_typeid  INT  DEFAULT 0  COMMENT '字典类型索引',
dictionarytype_updatetime DATETIME  DEFAULT null  COMMENT '字典类型更新时间',

  PRIMARY KEY (`dictionarytype_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT ='字典' ;
 
create index idx_dictionarytype_name on dictionarytype (dictionarytype_name) ;    
create index idx_dictionarytype_typeid on dictionarytype (dictionarytype_typeid) ;   

"""