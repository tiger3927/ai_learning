from keras.preprocessing.image import ImageDataGenerator
from keras.datasets import cifar10

import numpy as np

NUM_TO_AUGMENT = 5

# 加载 数据 集
(X_train, y_train), (X_test, y_test) = cifar10.load_data()
# 扩展
print(" Augmenting training set images...")
datagen = ImageDataGenerator(rotation_range=40,
                             width_shift_range=0.2,
                             height_shift_range=0.2,
                             zoom_range=0.2,
                             horizontal_flip=True,
                             fill_mode=' nearest')

xtas, ytas = [], []
for i in range(X_train.shape[0]):
    num_aug = 0
    x = X_train[i]  # (3, 32, 32)
    print(x.shape)
    x = x.reshape((1,) + x.shape)  # (1, 3, 32, 32)
    for x_aug in datagen.flow(x, batch_size=1, save_to_dir='preview', save_prefix='cifar', save_format='jpeg'):
        if num_aug >= NUM_TO_AUGMENT:
            break
        xtas.append(x_aug[0])
        num_aug += 1
