from PIL import Image
import cv2
import shutil
import os
import numpy as np

IMG_ROOT = './form/images/'
LABEL_ROOT = './form/labels/'
images= os.listdir(IMG_ROOT)
labels = os.listdir(LABEL_ROOT)

def brightness(files, c, b):
  start = len(os.listdir(IMG_ROOT)) + 1
  for index in range(len(files)):
    file = files[index]
    img = cv2.imread(IMG_ROOT + file)
    rows, cols, chunnel = img.shape
    blank = np.zeros([rows, cols, chunnel], img.dtype)
    res = cv2.addWeighted(img, c, blank, 1 - c, b)
    cv2.imwrite(IMG_ROOT + str(start + index) + '.png', res)


def binary(files):
  start = len(os.listdir(IMG_ROOT)) + 1
  for index in range(len(files)):
    file = files[index]
    img = cv2.imread(IMG_ROOT + file)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_img, 250, 255, cv2.THRESH_BINARY)
    cv2.imwrite(IMG_ROOT + str(start + index) + '.png', thresh)

def expandDataset(files, type):
  if type == 'images':
    files = os.listdir(IMG_ROOT)
    for index in range(len(files)):
      shutil.copy(IMG_ROOT + files[index], IMG_ROOT + str(len(files) + index + 1) + '.png')

  if type == 'labels':
    start = len(os.listdir(LABEL_ROOT))
    for index in range(len(files)):
      if files[index] == 'classes.txt':
        continue
      shutil.copy(LABEL_ROOT + files[index], LABEL_ROOT + str(start + index) + '.txt')

if __name__ == '__main__':
  # 提高对比度
  brightness(images, 0.8, 1)
  expandDataset(labels, 'labels')
  # 降低对比度
  brightness(images, 1.1, 1)
  expandDataset(labels, 'labels')
  # 提高亮度
  brightness(images, 1, 3)
  expandDataset(labels, 'labels')
  # 二值化
  binary(images)
  expandDataset(labels, 'labels')