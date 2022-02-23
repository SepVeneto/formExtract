import hashlib
import subprocess
import urllib.parse, urllib.request
import json
import math
import re

from string import Template
from PIL import Image

import utils
import setting

def takeSec(elem):
  return elem[1]

def format_prop(prop: str):
  prop = prop.replace(':', '').strip()
  prop_list = prop.split(' ')
  prop = ''
  for index in range(len(prop_list)):
    if index == 0:
      prop = prop_list[index].lower()
    else:
      first = prop_list[index][:1]
      rest = prop_list[index][1:]
      prop += first.upper() + rest
  return prop

def md5(query):
  cont:str = setting.APPID + query + setting.SALT + setting.SECRET
  return hashlib.md5(cont.encode(encoding='utf-8')).hexdigest()

def command(cmd):
  return subprocess.run(cmd, stderr=subprocess.PIPE, encoding='gbk')

def translation(query):
  url = Template('${api}?q=${query}&from=zh&to=en&appid=${appid}&salt=${salt}&sign=${sign}').substitute(
    api=setting.TRAN_URL,
    query=urllib.parse.quote(query),
    appid=setting.APPID,
    salt=setting.SALT,
    sign=md5(query)
  )
  res = urllib.request.urlopen('http://api.fanyi.baidu.com' + url)
  res = json.loads(res.read())
  props = []
  trans_result = res['trans_result']
  for item in trans_result:
    props.append(utils.format_prop(item['dst']))
  return props

def find_maybe_val(val, items):
  for item in items:
    if maybe_val(val, item):
      return item 
  return None

def is_in_form_item(l_x1, l_x2, items):
  for type, x1, x2 in items:
    if l_x2 <= x2 and l_x1 >= x1:
      return True
  return False

def format_label_info(infos):
  arr = []
  prev_i = 0
  curr_i = 0
  used_map = {}
  for prev_i in range(len(infos)):
    prev_pos, prev_cont = infos[prev_i]
    prev_x, prev_y, prev_w, prev_h = pos2xywh(prev_pos)
    for curr_i in range(prev_i, len(infos)):
      curr_pos, curr_cont = infos[curr_i]
      curr_x, curr_y, curr_w, curr_h = pos2xywh(curr_pos)
      if prev_y == curr_y and prev_x == curr_x:
        continue
      elif maybe_val(prev_y, curr_y, 24) and maybe_val(curr_x, prev_x, 50):
        w = max(curr_w, prev_w)
        h = max(curr_h, prev_h)
        x = min(prev_x, curr_x)
        y = min(prev_y, curr_y)
        used_map[prev_i] = True
        used_map[curr_i] = True
        # print()
        arr.append(((x, y, w, h), (prev_cont[0] + curr_cont[0], prev_cont[1] * curr_cont[1])))
        break 
    if used_map.get(prev_i, None):
      continue
    used_map[prev_i] = True
    arr.append(((prev_x, prev_y, prev_w, prev_h), prev_cont))
  return arr

def pos2xywh(pos):
  X = 0
  Y = 1
  topleft, topright, bottomright, bottomleft = pos
  x = topleft[X]
  y = topleft[Y]
  width = topright[X] - topleft[X]
  height = bottomleft[Y] - topleft[Y]
  return x, y, width, height

def find_key(dicts: dict, maybe_key: str):
  keys = dicts.keys()
  if len(keys) == 0:
    return maybe_key
  for key in keys:
    if maybe_val(maybe_key, key):
      return key
  return maybe_key

def changeOrigin(info):
  type, x, y, w, h = info 
  return (type, x - (w / 2), y - (h / 2), w, h)

def maybe_val(origin, target, threshold = 10):
  if not target:
    return False
  return origin <= (target + threshold) and origin >= (target - threshold)

def format_form_info(info, width, height):
  index, x, y, w, h = info.split(' ')
  return index, math.ceil(float(x) * width), math.ceil(float(y) * height), math.ceil(float(w) * width), math.ceil(float(h) * height)

def get_image_size(img):
  image = Image.open(img)
  width, height = image.size
  return width, height

def formatText(cont: str):
  required = False
  label = cont
  isRequired = not bool(re.match(r'^[a-zA-Z0-9\u4e00-\u9fa5]', cont))
  if isRequired:
    required = isRequired
    label = label[1:]
  return {
    'label': label,
    'required': required
  }