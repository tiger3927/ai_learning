import os
os.environ['KERAS_BACKEND'] = 'tensorflow'

#搭建普通神经网络，识别手写数字

'''
import tensorflow as tf
from keras import backend as K
K.set_image_dim_ordering("tf")
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.6  #限制GPU内存占用率
config.gpu_options.allow_growth = True  # True 不全部占满显存, 按需分配
sess = tf.Session(config=config)
K.set_session(sess)  # 设置session
'''

import numpy as np
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers.core import Dense,Activation,Dropout
from keras.optimizers import SGD,RMSprop,Adam
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
#from keras_multi_gpu import make_parallel2

#from quiver_engine import server

np.random.seed(1671) #重复性 设置

#网络和训练
NB_EPOCH=20
BATCH_SIZE=128
VERBOSE=1
NB_CLASSES=10
#输出个数等于数字个数
OPTIMIZER=Adam()
#SGD优化器，本章稍后介绍
N_HIDDEN=128
VALIDATION_SPLIT=0.2
DROPOUT=0.3
MODEL_DIR = "model"


#训练集中用作验证集的数据比例
#数据：混合并划分训练集和测试集数据
#
(X_train,y_train),(X_test,y_test)=mnist.load_data()
#X_train是60000行28×28的数据，变形为60000×784
RESHAPED=784
#

X_train=X_train.reshape(60000,RESHAPED)
X_test=X_test.reshape(10000,RESHAPED)
X_train=X_train.astype('float32')
X_test=X_test.astype('float32')
#归一化
X_train/=255
X_test/=255

print(X_train.shape[0],'trainsamples')
print(X_test.shape[0],'testsamples')
#将类向量转换为二值类别矩阵
Y_train=np_utils.to_categorical(y_train,NB_CLASSES)
Y_test=np_utils.to_categorical(y_test,NB_CLASSES)
#将数字0到9，变成一个长度为10的数组

print(y_train.shape)
print(y_test.shape)
print(Y_train.shape)
print(Y_test.shape)

print(*Y_train[1])

#10个输出
#最后是softmax激活函数
model=Sequential()

model.add(Dense(N_HIDDEN,input_shape=(RESHAPED,)))
model.add(Activation('relu'))

model.add(Dropout(DROPOUT))

model.add(Dense(N_HIDDEN))
model.add(Activation('relu'))

model.add(Dropout(DROPOUT))

#最后一层是使用激活函数softmax的单个神经元，它是sigmoid函数的扩展。softmax将任意k维实向量压缩到区间(0,1)上的k维实向量。
model.add(Dense(NB_CLASSES))
model.add(Activation('softmax'))  #对应sigmod激活函数

#model.summary()  #打印出网络架构

#loss 目标函数  mse  categorical_crossentropy binary_crossentropy 等等
#optimizer 优化器
#metrics 评估指标
#   Accuracy： 准确率，针对预测目标的预测正确的比例
#   Precision： 查准率  衡量多分类问题中多少选择项是关联正确的
#   Recall： 查全率 衡量多分类问题中多少关联正确的数据被选出

#model = make_parallel2(model, 2)#使用多GPU的方式
model.compile(loss='categorical_crossentropy',optimizer=OPTIMIZER,metrics=['accuracy'])

#设置检查点 保存最好模型
checkpoint=ModelCheckpoint(filepath=os.path.join(MODEL_DIR,"model-{epoch:02d}.h5"))

history=model.fit(X_train,Y_train,batch_size=BATCH_SIZE,epochs=NB_EPOCH,verbose=VERBOSE,validation_split=VALIDATION_SPLIT)
#,callbacks=[checkpoint]
#加入回调保存H5
score=model.evaluate(X_test,Y_test,verbose=VERBOSE)
model.save(os.path.join(MODEL_DIR,"test_keras_1.h5"))

#model.evaluate()：用于计算损失值
#model.predict_classes()：用于计算输出类别
#model.predict_proba()：用于计算类别概率

print("Testscore:",score[0])
print('Testaccuracy:',score[1])

