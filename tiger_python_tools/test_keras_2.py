import os
os.environ['KERAS_BACKEND'] = 'tensorflow'
#os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
#搭建CNN网络，识别手写数字

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
import tensorflow as tf
from keras.models import Sequential
#from keras.layers import regularizers
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Flatten
from keras.layers.core import Dense,Dropout
from keras.datasets import mnist
from keras.utils import np_utils
from keras.optimizers import SGD, RMSprop, Adam
import numpy as np
import matplotlib.pyplot as plt
import pylab
from keras.utils import multi_gpu_model
import matplotlib


gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
cpus = tf.config.experimental.list_physical_devices(device_type='CPU')
print(gpus, cpus)
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True) #自动增加显存占用，不全部占用


# 网络和训练
NB_EPOCH = 20
BATCH_SIZE = 128
VERBOSE = 1
OPTIMIZER = Adam()
VALIDATION_SPLIT = 0.2
IMG_ROWS, IMG_COLS = 28, 28
NB_CLASSES = 10
INPUT_SHAPE = (IMG_ROWS, IMG_COLS,1)
DROPOUT=0.3

# 定义 ConvNet
class LeNet:
    @staticmethod
    def build(input_shape, classes):
        model = Sequential()
        # CONV => RELU => POOL
        model.add(Conv2D(20, kernel_size=5, padding="same", input_shape=input_shape))
        model.add(Activation("relu"))
        model.add(Dropout(DROPOUT))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        # CONV=>RELU=>POOL
        model.add(Conv2D(50, kernel_size=5, border_mode="same"))
        model.add(Activation("relu"))
        model.add(Dropout(DROPOUT))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        model.add(Flatten())
        model.add(Dense(500))  #,kernel_regularizer=regularizers.l2(0.01)
        model.add(Activation("relu"))
        model.add(Dropout(DROPOUT))
        # softmax 分类器
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        return model

# 混合并划分训练集和测试集数据

def load_data(path='mnist.npz'):
    """Loads the MNIST dataset.
    # Arguments
        path: path where to cache the dataset locally
            (relative to ~/.keras/datasets).
    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    path = get_file(path,
                    origin='https://s3.amazonaws.com/img-datasets/mnist.npz',
                    file_hash='8a61469f7ea1b51cbae51d4f78837e45')
    """
    f = np.load(path)
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']
    f.close()
    return (x_train, y_train), (x_test, y_test)

(x_train, y_train), (x_test, y_test) = load_data()
print(x_train.shape)
'''
if K.image_data_format() == 'channels_first':
    x_train =x_train.reshape(x_train.shape[0], 1, IMG_ROWS, IMG_COLS)
    x_test =x_test.reshape(x_test.shape[0], 1, IMG_ROWS, IMG_COLS)
    INPUT_SHAPE = (1,IMG_ROWS, IMG_COLS)
else:
    x_train =x_train.reshape(x_train.shape[0], IMG_ROWS, IMG_COLS, 1)
    x_test =x_test.reshape(x_test.shape[0], IMG_ROWS, IMG_COLS, 1)
    INPUT_SHAPE = (IMG_ROWS, IMG_COLS, 1)
'''
x_train = x_train.reshape(x_train.shape[0], IMG_ROWS, IMG_COLS, 1)
x_test = x_test.reshape(x_test.shape[0], IMG_ROWS, IMG_COLS, 1)
INPUT_SHAPE = (IMG_ROWS, IMG_COLS, 1)

# 把它们看成float类型并归一化
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

# 我们需要使用形状60K×[1×28×28]作为卷积网络的输入
#x_train = x_train[:, np.newaxis, :, :]
#x_test = x_test[:, np.newaxis, :, :]
print(x_train.shape[0], 'trainsamples')
print(x_test.shape[0], 'testsamples')

# 将类向量转换成二值类别矩阵
y_train = np_utils.to_categorical(y_train, NB_CLASSES)
y_test = np_utils.to_categorical(y_test, NB_CLASSES)

# 初始化优化器和模型
with tf.device('/cpu:0'):
    model = LeNet.build(input_shape=INPUT_SHAPE, classes=NB_CLASSES)
parallel_model = multi_gpu_model(model,gpus=2)
parallel_model.compile(loss="categorical_crossentropy", optimizer=OPTIMIZER, metrics=["accuracy"])
history = parallel_model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=NB_EPOCH, verbose=VERBOSE,
                    validation_split=VALIDATION_SPLIT)
model.save("model/test_keras_2.h5")
score = parallel_model.evaluate(x_test, y_test, verbose=VERBOSE)
print("Testscore:", score[0])
print('Testaccuracy:', score[1])
# 列出全部历史数据
print(history.history.keys())
# 汇总准确率历史数据

plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('modelaccuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# 汇总损失函数历史数据
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('modelloss')
plt.ylabel('loss')
plt.xlabel(' epoch')
plt.legend([' train', 'test'], loc='upper left')
plt.show()

