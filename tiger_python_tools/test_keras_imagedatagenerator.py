from keras.preprocessing.image import ImageDataGenerator
from keras.datasets import cifar10
import numpy as np

NUM_TO_AUGMENT=5
#加载数据集
(X_train,y_train),(X_test,y_test)=cifar10.load_data()

#图像变换生成器，用于增加样本数量
datagen=ImageDataGenerator(
	rotation_range=40,#0到180
	width_shift_range=0.2,
	height_shift_range=0.2,
	zoom_range=0.2,
	horizontal_flip=True,
	fill_mode='nearest'#填充空白的方法)
