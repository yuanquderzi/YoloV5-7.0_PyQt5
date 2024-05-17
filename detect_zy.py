import numpy as np
from torch import load,from_numpy,tensor
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer, xyxy2xywh)
from utils.augmentations import letterbox
from utils.plots import Annotator, colors
import cv2
import base64
import torch
from utils.torch_utils import select_device
from models.common import DetectMultiBackend
import time
imgsz = (640, 640)  # 输入图片的大小 默认640(pixels)
conf_thres = 0.25  # object置信度阈值 默认0.25  用在nms中
iou_thres = 0.45  # 做nms的iou阈值 默认0.45   用在nms中
max_det = 1000  # 每张图片最多的目标数量  用在nms中
device = 'cpu'  # 设置代码执行的设备 cuda device, i.e. 0 or 0,1,2,3 or cpu
classes = None  # 在nms中是否是只保留某些特定的类 默认是None 就是所有类只要满足条件都可以保留 --class 0, or --class 0 2 3
agnostic_nms = False  # 进行nms是否也除去不同类别之间的框 默认False
augment = False  # 预测是否也要采用数据增强 TTA 默认False
visualize = False  # 特征图可视化 默认FALSE
half = False  # 是否使用半精度 Float16 推理 可以缩短推理时间 但是默认是False
dnn = False  # 使用OpenCV DNN进行ONNX推理
line_thickness=3 # bounding box thickness (pixels)


def detect(img,model_path,iou_thres,conf_thres):
    # 导入模型
    device1 = select_device(device)
    model = DetectMultiBackend(model_path, device=device1, dnn=dnn, data=None, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    if half:
        model.half()  # to FP16
    bs = 1
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    im0 = img
    annotator = Annotator(im0, line_width=line_thickness, example=str(names))
    im = letterbox(im0, 640, stride=32, auto=True)[0]
    im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    im = np.ascontiguousarray(im)  # www 函数将一个内存不连续存储的数组转换为内存连续存储的数组，使得运行速度更快。
    im = torch.from_numpy(im).to(device)
    im = im.half() if model.fp16 else im.float()
    im /= 255  # 0 - 255 to 0.0 - 1.0
    if len(im.shape) == 3:
        im = im[None]  # expand for batch dim

    # 预测中
    pred = model(im, augment=False)
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

    # 返回结果
    detections = []
    for i, det in enumerate(pred):  # per image 每张图片
        if len(det):
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
            # result
            for *xyxy, conf, cls in reversed(det):

                c = int(cls)  # integer class
                label = f'{names[c]} {conf:.2f}'
                annotator.box_label(xyxy, label, color=colors(c, True))

                #xywh1 = [c.numpy().tolist() for c in xyxy]
                xyxy = [int(c) for c in xyxy]  # 确保坐标是整数

                dic = {
                    'class': f'{names[int(cls)]}',  # 检测目标对应的类别名
                    'location': xyxy,  # 坐标信息
                    'score': round(float(conf) * 100, 2)  # 目标检测分数
                }
                detections.append(dic)
    annotated_img = annotator.result()
    return annotated_img, detections

def base64_input(base64_txt):
    img_str = base64.b64decode(base64_txt)
    im_ndarray = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(im_ndarray, cv2.IMREAD_COLOR)  # BGR
    model_path = 'yolov5s.pt'
    result = detect(image, model_path=model_path)
    print(result)
    return result

def image_input(image):
    start_time = time.time()
    model_path = 'yolov5s.pt'
    result = detect(image, model_path=model_path, iou_thres = 0.45, conf_thres = 0.25)
    print(result)
    print("预测时间：",time.time()-start_time)
    return result


if __name__ == '__main__':
    # base64图片
    #base64_txt = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDA110JCgsKCA02gsODg0PEyAVExI2EyccHhcgLikxMC4pLSwzOko+MzZGNy1tQFdBRkxOU33Mj5aYVpQYEpRUk//22wBDA24ODhMREyYVFSZ/2Q=="
    #base64_input(base64_txt)

    # image 图片
    image = cv2.imread("data/images/bus.jpg")
    image_input(image)


