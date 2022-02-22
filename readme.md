# 基于YOLOv5和PaddleOCR的表单提取工具
注：没有接触过机器学习，只是一个了解学习的demo

基本思路：输入表单图片（比如原型图或是设计稿），提取图片上所有表单相关的信息（包括label及其位置信息，表单域的类型及其位置信息），组合成html输出

## YOLOv5
表单域的类型和位置检测使用的是`yolov5`
需要先针对表单类型做数据训练
```
docker exec -it yolov5 python detect.py --source $pwd --weight $pwd
```
待检测的图片和权重文件需要放在容器挂载的目录里
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
+ 170        cls_bk = cls
+ 171        cls = names[int(cls.item())]
172        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
173        with open(txt_path + '.txt', 'a') as f:
174          f.write(('%s ' * len(line)).rstrip() % line + '\n')
+ 175        cls = cls_bk
```

## PaddleOCR
label的识别使用的是飞浆的OCR工具库
采用的是服务器部署的方案

## Flask
使用Flask作为接口服务器的web框架