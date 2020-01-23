from sqlalchemy import Column, Integer, String,SmallInteger,BigInteger,Float,Unicode,Boolean,Time,LargeBinary,DATETIME
import asyncio
import sqlalchemy

from config import ServerParameters

def getsqlalchemytable():    #CORE操作层对象
	mysqlmetadata = sqlalchemy.MetaData()
	return sqlalchemy.Table('dictionary', mysqlmetadata,
					#ID
					Column('dictionary_id',  Integer  ,primary_key=True       ),
					#字典类型索引
					Column('dictionary_typeid',  Integer   ,index=True      ),
					#字典名称
					Column('dictionary_name',  Unicode(64)   ,index=True      ),
					#字典编码
					Column('dictionary_code',  Unicode(32)   ,index=True   ,nullable=True    ),
					#字典描述
					Column('dictionary_description',  Unicode(128)     ,nullable=True    ),
					#字典排序
					Column('dictionary_orderindex',  Integer        ),
					#字典类型名称
					Column('dictionary_typeval',  Unicode(64)     ,nullable=True    ),
					#字典更新日期
					Column('dictionary_updatetime',  DATETIME     ,nullable=True    )
					)


class cdictionary:
	def __init__(self):
		pass

				   
	
	
class dictionary(ServerParameters.BaseMySql):  #高级ORM对象
	__tablename__ = 'dictionary' #表名

	#ID :
	dictionary_id = Column(  Integer  ,primary_key=True       )
	#字典类型索引 :
	dictionary_typeid = Column(  Integer   ,index=True      )
	#字典名称 :
	dictionary_name = Column(  Unicode(64)   ,index=True      )
	#字典编码 :
	dictionary_code = Column(  Unicode(32)   ,index=True   ,nullable=True    )
	#字典描述 :
	dictionary_description = Column(  Unicode(128)     ,nullable=True    )
	#字典排序 :
	dictionary_orderindex = Column(  Integer        )
	#字典类型名称 :
	dictionary_typeval = Column(  Unicode(64)     ,nullable=True    )
	#字典更新日期 :
	dictionary_updatetime = Column(  DATETIME     ,nullable=True    )





"""
CREATE TABLE `dictionary` (
  dictionary_id int NOT NULL AUTO_INCREMENT COMMENT 'ID',
dictionary_typeid  INT  DEFAULT 0  COMMENT '字典类型索引',
dictionary_name VARCHAR(64)  DEFAULT null  COMMENT '字典名称',
dictionary_code VARCHAR(32)  DEFAULT null  COMMENT '字典编码',
dictionary_description VARCHAR(128)  DEFAULT null  COMMENT '字典描述',
dictionary_orderindex  INT  DEFAULT 0  COMMENT '字典排序',
dictionary_typeval VARCHAR(64)  DEFAULT null  COMMENT '字典类型名称',
dictionary_updatetime DATETIME  DEFAULT null  COMMENT '字典更新日期',

  PRIMARY KEY (`dictionary_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT ='字典' ;
 
create index idx_dictionary_typeid on dictionary (dictionary_typeid) ; 
create index idx_dictionary_name on dictionary (dictionary_name) ; 
create index idx_dictionary_code on dictionary (dictionary_code) ;            

"""