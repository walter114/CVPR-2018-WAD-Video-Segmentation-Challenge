import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import math
import pdb

def increase_batch(start, bound, rate=1e-4):
    # increase batch size
    next_size = start
    while True:
        yield math.floor(next_size)
        tmp = next_size*(1+rate)
        if not tmp>bound:
            next_size*=(1+rate)
        
def mini_batch(x, t, batch_generator, shuffle=True): 
    # get mini-batch
    ptr = 0
    data_size = x.shape[0]
    
    if shuffle:
        order = np.arange(data_size)
        np.random.shuffle(order)
        x_shuffle = x[order]
        t_shuffle = t[order]
    
    batch_size = batch_generator.__next__()    
    while True:
        if not ptr+batch_size >= data_size:
            yield x_shuffle[ptr:ptr+batch_size], t_shuffle[ptr:ptr+batch_size]
            ptr = ptr + batch_size
            batch_size = batch_generator.__next__()
        else:
            break
    yield x_shuffle[ptr:], t_shuffle[ptr:]

def decrease_dropout():
    # decrease dropout rate
    pass

def entropy_loss(y, t):
    loss = tf.nn.softmax_cross_entropy_with_logits(labels=t, logits=y)
    return tf.reduce_mean(loss)

def mean_square_loss(x, t):
    batch_size, input_dim = x.get_shape().as_list()
    if batch_size is None:
        batch_size = 1
    return tf.reduce_sum( tf.square(x - t) ) / (batch_size*input_dim)

def soft_ncut(img_seg, img, sigma_d=1e2, sigma_i=1e-2):
    batch_size, height, width, ch = img.get_shape().as_list()
    N = height*width
    
    img = tf.reshape(img, (-1, N, 1, ch))
    img1 = tf.tile(img, (1, 1, N, 1))
    img2 = tf.transpose(img, (0, 2, 1, 3))
    
    img_seg = tf.reshape(img_seg, (-1, N, 1, ch))
    img_seg1 = tf.tile(img_seg, (1, 1, N, 1))
    img_seg2 = tf.transpose(img_seg1, (0, 2, 1, 3))
    
    x, y = tf.meshgrid(tf.range(width, dtype=tf.float32), 
                       tf.range(height, dtype=tf.float32))
    x = tf.reshape(x, (N, -1))
    y = tf.reshape(y, (N, -1))
    yx = tf.concat([y, x], axis=1)
    yx = tf.expand_dims(yx, axis=0)
    yx = tf.tile(yx, (N, 1, 1))
    xy = tf.transpose(yx, perm=[1, 0, 2])
    dis = tf.sqrt(tf.reduce_sum( (xy-yx)**2, axis=2 ))
    dis = tf.expand_dims(dis, axis=0)
    dis = tf.expand_dims(dis, axis=3)
    dis = tf.tile(dis, (1, 1, 1, ch))
    
    W = tf.multiply( tf.exp(-tf.sqrt((img1-img2)**2)/sigma_i), tf.exp(-dis/sigma_d) )
    
    asso1 = tf.multiply(tf.multiply(img_seg1, W), img_seg2)
    asso1 = tf.reduce_sum(asso1, axis=[1, 2, 3])
    asso1_margin = tf.multiply(img_seg1, W)
    asso1_margin = tf.reduce_sum(asso1_margin, axis=[1, 2, 3])+1e-6
    
    asso2 = tf.multiply(tf.multiply(1-img_seg1, W), 1-img_seg2)
    asso2 = tf.reduce_sum(asso2, axis=[1, 2, 3])
    asso2_margin = tf.multiply(1-img_seg1, W)
    asso2_margin = tf.reduce_sum(asso2_margin, axis=[1, 2, 3])+1e-6
    
    loss = 2 - tf.div(asso1, asso1_margin) - tf.div(asso2, asso2_margin)
    loss = tf.reduce_mean(loss)
    return loss

def sigmoid_loss(y, t):
    loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=t, logits=y)
    loss = tf.reduce_mean(loss)
    return loss
    
    
    
    
    
    
    
    
    
    
    
    
