import tensorflow as tf
import datetime

# running
# Creates a graph.(cpu version)
print('cpu version')
with tf.device('/gpu:0'):
    a1 = tf.constant(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0,
         5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0,
         3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[6, 9], name='a1')
    b1 = tf.constant(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0,
         5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0,
         3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[9, 6], name='b1')
    c1 = tf.matmul(a1, b1)
    c1 = tf.matmul(c1, a1)
    c1 = tf.matmul(c1, b1)
# Creates a session with log_device_placement set to True.
sess1 = tf.Session(config=tf.ConfigProto(log_device_placement=True))
# Runs the op.
starttime1 = datetime.datetime.now()
for i in range(9999):
    sess1.run(c1)
print(sess1.run(c1))
sess1.close()
tf.reset_default_graph()
endtime1 = datetime.datetime.now()
time1 = (endtime1 - starttime1).seconds
# print('time1:',time1)
#############################################
print('gpuversion')
# Creates a graph.(gpu version)
# running
with tf.device('/cpu:0'):
    a2 = tf.constant(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0,
         5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0,
         3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[6, 9], name='a2')
    b2 = tf.constant(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0,
         5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0,
         3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[9, 6], name='b2')
    c2 = tf.matmul(a2, b2)
    c2 = tf.matmul(c2, a2)
    c2 = tf.matmul(c2, b2)
# Creates a session with log_device_placement set to True.
sess2 = tf.Session(config=tf.ConfigProto(log_device_placement=True))
# Runs the op.
starttime2 = datetime.datetime.now()
for i in range(9999):
    sess2.run(c2)
print(sess2.run(c2))
sess2.close()
endtime2 = datetime.datetime.now()
time2 = (endtime2 - starttime2).seconds
print('time1:', time1)
print('time2:', time2)
