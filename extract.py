import argparse
import os
import re

from paddleocr import PaddleOCR
from string import Template

import utils
import setting
import generate


ROOT = os.path.dirname(os.path.relpath(__file__))

def main(opt):
  formExtract(**vars(opt))

def formExtract(img, weight = 'last.pt'):
  temp_extract = Template('docker exec -it yolov5 python detect.py \
    --source ${img}\
    --weight ${weight}\
    --project /yolov5\
    --save-txt\
    --name ${res_name}\
    --exist-ok\
  ')
  extract = temp_extract.substitute(
    img=setting.DOCKER_MOUNT + img,
    weight=setting.DOCKER_MOUNT + weight,
    project=ROOT,
    res_name=setting.RESULT
  )
  # command('docker')
  extract_res = utils.command(extract)
  if extract_res.returncode == 0:
    image_name, suffix = os.path.basename(img).split('.')
    width, height = utils.get_image_size(setting.HOST_MOUNT + img)
    with open(setting.HOST_MOUNT + setting.RESULT + '/labels/' + image_name + '.txt', 'rb') as f:
      lines = f.readlines()
      form_res = []
      for line in lines:
        l_str = line.decode(encoding='utf-8')
        res = utils.format_form_info(l_str, width, height)
        if not res[0] == 'label' and not res[0] == 'required':
          form_res.append(res)

    res = run(setting.HOST_MOUNT + img)
    layout_label = label_layout(res)
    print(layout_label)
    layout_item = item_layout(form_res)
    print(layout_item)

    res = merge_layout(layout_label, layout_item)
    return res, generate.to_html(res)

def merge_layout(label_layout: dict, item_layout: dict, dir = 'horizontal'):
  label_keys = list(label_layout.keys())
  item_keys = list(item_layout.keys())

  label_keys.sort()
  item_keys.sort()
  layout = []
  item_row = 0
  prop_index = 0
  label_list = []
  # row
  for label_row in range(len(label_keys)):
    label_key = label_keys[label_row]
    labels = label_layout.get(label_key)
    labels.sort(key=utils.takeSec)
    if dir == 'vertical':
      max_height = utils.cal_max_height(labels)
      label_key += max_height
    item_key = utils.find_maybe_val(label_key, item_keys)
    print(item_key)
    row = []
    # y轴的值不近似说明这一行没有识别出表单域，需要用unknown来占位
    if not item_key or not utils.maybe_val(label_key, item_key):
      print('enter')
      for col in range(len(labels)):
        label, l_x1, l_x2, *rest = labels[col]
        row.append((label, 'unknown'))
      layout.append(row)
      continue
    else:
      item_row += 1
    items: list = item_layout.get(item_key)
    # 表单域内容按x轴上的位置升序排列
    items.sort(key=utils.takeSec)
    print('items:', items)

    item_col = 0
    for label_col in range(len(labels)):
      label, l_x1, l_x2, l_y1, l_y2 = labels[label_col]
      # 数组越界，是该行最后一个表单域内存在占位或默认值导致的
      if item_col >= len(items):
        continue
      item, i_x1, i_x2, i_y1, i_y2 = items[item_col]
      if dir == 'vertical':
        offset = i_x1 - int(l_x1)
        offset += (i_y1 - int(l_y2))
      else:
        offset = i_x1 - int(l_x2)

      print('offset:', offset)
      # label的位置在表单域内容之内，说明其实是placeholder，或者是默认值
      if utils.is_in_form_item(l_x1, l_x2, l_y1, l_y2, items, dir):
        continue
      # label与表单域内容不够接近，说明这两个分属不同的表单域
      if offset > 20:
        row.append((label, 'unknown'))
        continue
      item_col += 1

      label_list.append(label['label'])
      row.append(({ **label, 'prop': prop_index }, item))
      prop_index += 1

    layout.append(row)

  prop_index = 0
  print(label_list)
  props = utils.translation('\n'.join(label_list))
  for row in layout:
    for config, type in row:
      prop_index = config.get('prop', None)
      if prop_index == None:
        continue
      config['prop'] = re.sub(r'\W', '', props[prop_index])
      # config['prop'] = props[prop_index].replace('(', '_').replace(')', '_').replace('.', '')
  return layout

def item_layout(items, dir = 'horizontal'):
  layout = {}
  itemArr = []
  for item in items:
    itemArr.append(utils.changeOrigin(item))

  for type, x, y, w, h in itemArr:
    if dir == 'horizontal':
      index = y
      pos1 = x
      pos2 = x + w
      pos3 = y
      pos4 = y + h
    else:
      index = x
      pos1 = y
      pos2 = y + h
      pos3 = x
      pos4 = x + w
    key = utils.find_key(layout, index)
    if not layout.get(key, None):
      layout.setdefault(key, [(type, pos1, pos2, pos3, pos4)])
    else:
      layout[key].append((type, pos1, pos2, pos3, pos4))
  return layout

def label_layout(labels, dir = 'horizontal'):
  Y = 1
  X = 0
  W = 2
  H = 3
  TEXT = 0
  layout = {}
  for pos, cont in labels:
    if dir == 'horizontal':
      index = pos[Y]
      pos1 = pos[X]
      pos2 = pos[X] + pos[W]
      pos3 = pos[Y]
      pos4 = pos[Y] + pos[H]
    else:
      index = pos[X]
      pos1 = pos[Y]
      pos2 = pos[Y] + pos[H]
      pos3 = pos[X]
      pos4 = pos[X] + pos[W]
    text = utils.formatText(cont[TEXT])
    key = utils.find_key(layout, index)
    if not layout.get(key, None):
      layout.setdefault(key, [(text, pos1, pos2, pos3, pos4)])
    else:
      layout[key].append((text, pos1, pos2, pos3, pos4))
  return layout

def run(img):
  ocr = PaddleOCR(use_angle_cls=True, lang='ch')
  result = ocr.ocr(img, cls=True)
  return utils.format_label_info(result)

def parse_opt():
  parser = argparse.ArgumentParser()
  parser.add_argument('--img', type=str)
  parser.add_argument('--weight', type=str, default='last.pt')
  opt = parser.parse_args()
  return opt

if __name__ == '__main__':
  opt = parse_opt()
  main(opt)