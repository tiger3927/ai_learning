import mxnet as mx

print(mx.context.num_gpus())
print(mx.context.gpu_memory_info())
a = mx.nd.ones((2, 3), mx.gpu())
for x in range(100000):
    a = a * 2 + 1
print(a)