# 基于YOLOv5和PaddleOCR的表单提取工具

## YOLOv5

### detect.py
对`yolov5`的预测脚本做了一点修改
```diff
# 
+ 163 if save_txt and exist_ok:
+ 164   with open(txt_path + '.txt', 'w'):
+ 165     pass
166
167 for *xyxy, conf, cls in reversed(det):
168    if save_txt:  # Write to file
169        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
+ 170        cls = names[int(cls.item())]
171        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
172        with open(txt_path + '.txt', 'a') as f:
173            f.write(('%s ' * len(line)).rstrip() % line + '\n')
```