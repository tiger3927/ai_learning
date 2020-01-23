import os
os.environ['KERAS_BACKEND']='mxnet'

import keras

print(keras.backend.backend())