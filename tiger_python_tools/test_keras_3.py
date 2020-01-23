from keras.datasets import cifar10
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense,Dropout,Activation,Flatten
from keras.layers.convolutional import Conv2D,MaxPooling2D
from keras.optimizers import SGD,Adam,RMSprop
import matplotlib.pyplot as plt
from keras.utils.vis_utils import plot_model
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from keras.utils import multi_gpu_model

#CIFAR- 10
#CIFAR-10是一个包含了60000张32×32像素的三通道图像数据集

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

#常量
IMG_CHANNELS=3
IMG_ROWS=32
IMG_COLS=32
BATCH_SIZE=128
NB_EPOCH=20
NB_CLASSES=10
VERBOSE=1
VALIDATION_SPLIT=0.2
OPTIM=RMSprop()

#加载数据集
(X_train,y_train),(X_test,y_test)=cifar10.load_data()
print('X_trainshape:',X_train.shape)
print(X_train.shape[0],'trainsamples')
print(X_test.shape[0],'testsamples')

#分类转换one-hot
Y_train=np_utils.to_categorical(y_train,NB_CLASSES)
Y_test=np_utils.to_categorical(y_test,NB_CLASSES)

#看成float类型并归一化
X_train=X_train.astype('float32')
X_test=X_test.astype('float32')
X_train/=255
X_test/=255
'''
if K.image_data_format() == 'channels_first':
    X_train =X_train.reshape(X_train.shape[0], IMG_CHANNELS, IMG_ROWS, IMG_COLS)
    X_test =X_test.reshape(X_test.shape[0], IMG_CHANNELS, IMG_ROWS, IMG_COLS)
    INPUT_SHAPE = (IMG_CHANNELS,IMG_ROWS, IMG_COLS)
else:
    X_train =X_train.reshape(X_train.shape[0], IMG_ROWS, IMG_COLS, IMG_CHANNELS)
    X_test =X_test.reshape(X_test.shape[0], IMG_ROWS, IMG_COLS, IMG_CHANNELS)
    INPUT_SHAPE = (IMG_ROWS, IMG_COLS, IMG_CHANNELS)
'''
X_train = X_train.reshape(X_train.shape[0], IMG_ROWS, IMG_COLS, IMG_CHANNELS)
X_test = X_test.reshape(X_test.shape[0], IMG_ROWS, IMG_COLS, IMG_CHANNELS)
INPUT_SHAPE = (IMG_ROWS, IMG_COLS, IMG_CHANNELS)

print(X_train.shape)
print(X_test.shape)

#网络
model=Sequential()
model.add(Conv2D(32,(3,3),padding='same',input_shape=(IMG_ROWS,IMG_COLS,IMG_CHANNELS)))
model.add(Activation('relu'))
model.add(Conv2D(32,(3,3),padding='same'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))
model.add(Conv2D(64,(3,3),padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64,3,3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(NB_CLASSES))
model.add(Activation('softmax'))
model.summary()

#训练
parallel_model = multi_gpu_model(model)
parallel_model.compile(loss='categorical_crossentropy',optimizer=OPTIM,metrics=['accuracy'])
parallel_model.fit(X_train,Y_train,batch_size=BATCH_SIZE,epochs=NB_EPOCH,validation_split=VALIDATION_SPLIT,verbose=VERBOSE)
score=parallel_model.evaluate(X_test,Y_test,batch_size=BATCH_SIZE,verbose=VERBOSE)
print("Testscore:",score[0])
print('Testaccuracy:',score[1])

#保存模型 And the weights learned by our deep network on the trainingset
model_json=model.to_json()
open('cifar10_architecture.json','w').write(model_json)
model.save_weights('cifar10_weights.h5',overwrite=True)
plot_model(model, to_file='CIFAR-10-net.png', show_shapes=True)