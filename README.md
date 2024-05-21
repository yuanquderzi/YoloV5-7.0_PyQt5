## **一、项目简介**
给yolov5-7.0版本加个gui界面，使用pyqt5，包含注册和登录界面，分别采用定时器QTimer和线程QThread显示视频帧，并实现简单的界面跳转，具体情况如下：

**特点：**
 1. UI界面与逻辑代码分离
 2. 支持自选定模型
 3. 同时输出检测结果与相应相关信息
 4. 支持图片，视频，摄像头检测
 5. 支持视频暂停与继续检测

**目的：**
 1. 熟悉QtDesign的使用
 2. 了解PyQt5基础控件与布局方法
 3. 了解界面跳转
 4. 了解信号与槽
 5. 熟悉视频在PyQt中的处理方法

**项目图片：**

![登录界面](data/register.png)
![注册界面](data/login.png)
![图片检测](data/picture.png)
![视频检测](data/video.png)
![摄像头检测](data/camera.png)

## **二、快速开始**
**环境与相关文件配置：**
 - 按照 ult-yolov5 中requirement的要求配置环境，自行安装PyQt5，注意都需要在一个evn环境中进行安装与配置
 - 下载或训练一个模型，将“.pt”文件放到weights文件夹，（权重文件可以自己选，程序默认打开weights文件夹）
 - 设置init中的opt

**两种程序使用方式：**

 - 直接运行detect_logical.py，进入检测界面
 - 运行main_logical.py，先登录，在进入检测界面

## **三、 参考与致谢**
 - 《PyQt5快速开发与实践》
 -  www.python3.vip
 - B站白月黑羽的PyQt教程 https://www.bilibili.com/video/BV1cJ411R7bP?from=search&seid=7706040462590056686
 - https://xugaoxiang.blog.csdn.net/article/details/118384430 从这个博主的博客中学到了很多知识，感觉博主，博主的代码框架也很好，也是本文代码是在其基础上进行学习和修改的
 - Github项目：YOLOv3GUI_Pytorch_PyQt5

## **四、 版权声明**
仅供交流学习使用，项目粗拙，勿商用，实际应用中出现的问题，个人不管哦~
=======

