# -*- coding: utf-8 -*-
"""CBIRWorking.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fvS6XaihLVMXBH7SDr7kYiurRv79ot6K
"""

import numpy as np
from numpy import linalg as LA
from keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from collections import defaultdict
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os
import sys
import fnmatch
import shutil
import random
import math
from keras.preprocessing.image import ImageDataGenerator
import h5py
import argparse

class VGGNet:
    def __init__(self):
        # weights: 'imagenet'
        # pooling: 'max' or 'avg'
        # input_shape: (width, height, 3), width and height should >= 48
        self.input_shape = (224, 224, 3)
        self.weight = 'imagenet'
        self.pooling = 'max'
        self.model = VGG16(weights = self.weight, input_shape = (self.input_shape[0], self.input_shape[1], self.input_shape[2]), pooling = self.pooling, include_top = False)
        self.model.predict(np.zeros((1, 224, 224 , 3)))

    '''
    Use vgg16 model to extract features
    Output normalized feature vector
    '''
    def extract_feat(self, img_path):
        img = image.load_img(img_path, target_size=(self.input_shape[0], self.input_shape[1]))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        feat = self.model.predict(img)
        norm_feat = feat[0]/LA.norm(feat[0])
        return norm_feat


def cbir(vid, queries):
    result_paths = defaultdict(list)
    #print(training_img_list)
    model=VGGNet()

    path = r"videos/outputs/crops/{}/".format(vid)
    featsarr = []
    image_paths = []
    img = os.listdir(path)
    for j in img:
        image_paths.append(path+"/"+j)
        feats=model.extract_feat(path+"/"+j)
        featsarr.append(feats)
    print("done")
    feats = np.array(featsarr)

    n = len(queries)
    print(n, queries)
    if n >= 1:
        for i in range(n):
            result = []
            try:
                query = model.extract_feat(os.path.join('website/static/queryImage', queries[i]))            
            except:
                print("file does not exist")
                continue
            k = 5
            # Use k-nearest neighbors to retrieve similar images
            nn = NearestNeighbors(n_neighbors=k, metric='cosine')
            nn.fit(feats)
            distances, indices = nn.kneighbors(np.array([query]))
            # Plot the query image and similar images
            # fig, axs = plt.subplots(1, k+1, figsize=(15, 8))
            # axs[0].imshow(load_img(testpath))
            # axs[0].set_title('Query Image')
            for j in range(k):
                # axs[i+1].imshow(load_img(image_paths[indices[0][i]]))
                result.append(image_paths[indices[0][j]])
                #save the result images
                shutil.copy(image_paths[indices[0][j]], 'website/static/resultImage/')
                # axs[i+1].set_title(f'Distance: {distances[0][i]:.2f}')
            # plt.show()
            result_paths[queries[i]].extend(result)
    return result_paths