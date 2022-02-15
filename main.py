import argparse
import math
import subprocess
import os
from PIL import Image
from paddleocr import PaddleOCR
from string import Template

ROOT = os.path.dirname(os.path.relpath(__file__))
DOCKER_MOUNT = '/yolov5/'
HOST_MOUNT = './model/'
RESULT= 'res'

def command(cmd):
  return subprocess.run(cmd, stderr=subprocess.PIPE, encoding='gbk')

def main(opt):
  formExtract(**vars(opt))

def formExtract(img, weight):
  temp_extract = Template('docker exec -it yolov5 python detect.py \
    --source ${img}\
    --weight ${weight}\
    --project /yolov5\
    --nosave\
    --save-txt\
    --name ${res_name}\
    --exist-ok\
  ')
  extract = temp_extract.substitute(
    img=DOCKER_MOUNT + img,
    weight=DOCKER_MOUNT + weight,
    project=ROOT,
    res_name=RESULT
  )
  # command('docker')
  extract_res = command(extract)
  if extract_res.returncode == 0:
    image_name, suffix = os.path.basename(img).split('.')
    width, height = get_image_size(HOST_MOUNT + img)
    with open(HOST_MOUNT + RESULT + '/labels/' + image_name + '.txt', 'rb') as f:
      lines = f.readlines()
      for line in lines:
        l_str = line.decode(encoding='utf-8')
        print(format_form_info(l_str, width, height))

    res = run(HOST_MOUNT + img)
    print(res)

def format_form_info(info, width, height):
  index, x, y, w, h = info.split(' ')
  return index, math.ceil(float(x) * width), math.ceil(float(y) * height), math.ceil(float(w) * width), math.ceil(float(h) * height)

def get_image_size(img):
  image = Image.open(img)
  width, height = image.size
  return width, height

def run(img):
  ocr = PaddleOCR(use_angle_cls=True, lang='ch')
  result = ocr.ocr(img, cls=True)
  return result

def parse_opt():
  parser = argparse.ArgumentParser()
  parser.add_argument('--img', type=str)
  parser.add_argument('--weight', type=str, default='last.pt')
  opt = parser.parse_args()
  return opt

if __name__ == '__main__':
  opt = parse_opt()
  main(opt)