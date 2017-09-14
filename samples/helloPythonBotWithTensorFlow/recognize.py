import tensorflow as tf
import numpy as np

savedFileName = 'checkpoint/saved_file_1'

x = tf.placeholder(tf.float32, [None, 784])
W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))
y = tf.matmul(x, W) + b

sess = tf.Session()
sess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
saver.restore(sess, savedFileName)

def predict(image):
  results = sess.run(y, feed_dict={x: [image]})
  predictedValue = np.argmax(results[0])
  return predictedValue
