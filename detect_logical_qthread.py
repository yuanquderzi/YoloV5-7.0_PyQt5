from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from ui.detect_ui2 import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import sys
from detect_zy import detect
import cv2
import time
from PyQt5.QtGui import QIcon, QPixmap
import numpy as np
import os


class UI_Logic_Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(UI_Logic_Window, self).__init__(parent)
        self.setupUi(self)
        self.signal_slot()
        self.cap = cv2.VideoCapture()
        self.output_folder = 'output/'
        self.iou_threshold = 0.45  # 初始iou阈值
        self.confidence_threshold = 0.25 # 初始置信度阈值
        self.weights = 'weights/yolov5n.pt'

        # 设置图标
        icon = QIcon()
        icon.addPixmap(QPixmap('ui_img/logo.jpg'))
        self.setWindowIcon(icon)


    # 绑定信号与嘈
    def signal_slot(self):
        self.comboBox_model.currentTextChanged.connect(self.choose_model)
        self.pushButton_img.clicked.connect(self.open_img)
        self.pushButton_video.clicked.connect(self.open_video)
        self.pushButton_camera.clicked.connect(self.open_camera)
        self.pushButton_pause.clicked.connect(self.pause_video)
        self.pushButton_finish.clicked.connect(self.finish_detect)
        self.doubleSpinBox_iou.valueChanged.connect(self.update_iou_threshold)
        self.horizontalSlider_iou.valueChanged.connect(self.update_iou_threshold_from_slider)
        self.doubleSpinBox_conf.valueChanged.connect(self.update_conf_threshold)
        self.horizontalSlider_conf.valueChanged.connect(self.update_conf_threshold_from_slider)

    def choose_model(self):
        """
        根据用户从组合框中选择的模型名称，更新模型路径。

        :param model_name: 用户选择的模型名称
        """
        # 假设模型存储在 'models/' 目录下，并且模型名称对应模型文件的名称
        model_name = self.comboBox_model.currentText()
        model_name = model_name.lower()
        model_path = f'weights/{model_name}'  # 构建模型文件的路径

        # 检查模型文件是否存在
        if not os.path.isfile(model_path):
            QMessageBox.warning(self, u"Warning", u"模型文件不存在", buttons=QMessageBox.Ok,
                                defaultButton=QMessageBox.Ok)
            return

        # 更新程序中的模型路径
        self.weights = model_path
        print(f'当前选择的模型路径: {self.weights}')

    # 更新iou阈值的槽函数
    def update_iou_threshold(self):
        self.iou_threshold = self.doubleSpinBox_iou.value()
        # 同时更新滑块的值，以保持一致性
        self.horizontalSlider_iou.setValue(self.iou_threshold*100)

    # 更新iou阈值的槽函数，由滑块触发
    def update_iou_threshold_from_slider(self):
        self.iou_threshold = self.horizontalSlider_iou.value() /100
        self.doubleSpinBox_iou.setValue(self.iou_threshold)  # 更新数值输入框的值

    # 更新置信度阈值的槽函数
    def update_conf_threshold(self):
        self.confidence_threshold = self.doubleSpinBox_conf.value()
        # 同时更新滑块的值，以保持一致性
        self.horizontalSlider_conf.setValue(self.confidence_threshold*100)

    # 更新置信度阈值的槽函数，由滑块触发
    def update_conf_threshold_from_slider(self):
        self.confidence_threshold = self.horizontalSlider_conf.value() /100
        self.doubleSpinBox_conf.setValue(self.confidence_threshold)  # 更新数值输入框的值

    def clean_table(self):
        while (self.tableWidget.rowCount() > 0):
            self.tableWidget.removeRow(0)

    def update_statistic_table(self, detections):
        self.clean_table()
        self.tableWidget.setRowCount(0)
        if detections == []:
            return
        for i, box in enumerate(detections):
            each_item = [str(i), str(box["class"]), "{}%".format(box["score"]), str(box["location"])]
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            for j in range(len(each_item)):
                item = QtWidgets.QTableWidgetItem(str(each_item[j]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.tableWidget.setItem(row, j, item)

    # 打开图片并检测
    def open_img(self):
        try:
            img_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开图片", "data/images",
                                                                "*.jpg;;*.png;;All Files(*)")
        except OSError as reason:
            print('文件打开出错啦！核对路径是否正确' + str(reason))
        else:
            # 判断图片是否为空
            if not img_name:
                QtWidgets.QMessageBox.warning(self, u"Warning", u"打开图片失败", buttons=QtWidgets.QMessageBox.Ok,
                                              defaultButton=QtWidgets.QMessageBox.Ok)

            else:
                img = cv2.imread(img_name)
                annotated_img, detections = detect(img, model_path=self.weights, iou_thres=self.iou_threshold, conf_thres=self.confidence_threshold)
                # 获取当前系统时间，作为img文件名
                now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
                file_name = img_name.split('/')[-1]
                new_filename = file_name.split('.')[0] + '_' + now + '.' + file_name.split('.')[-1]  # 获得文件后缀名
                file_path = self.output_folder + 'img_output/' + new_filename
                cv2.imwrite(file_path, annotated_img)

                # 检测信息显示在界面
                self.update_statistic_table(detections)

                # 检测结果显示在界面
                self.result = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2BGRA)
                self.result = cv2.resize(self.result, (640, 480), interpolation=cv2.INTER_AREA)
                self.QtImg = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                          QtGui.QImage.Format_RGB32)
                self.label_5.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
                self.label_5.setScaledContents(True)  # 设置图像自适应界面大小


    def set_video_name_and_path(self, video_name):
        # 获取当前系统时间，作为img和video的文件名
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))

        file_name = video_name.split('/')[-1]
        new_filename = file_name.split('.')[0] + '_' + now + '.mp4'
        # if vid_cap:  # video
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 视频检测结果存储位置
        save_path = self.output_folder + 'video_output/' + new_filename
        return fps, w, h, save_path

    def set_camera_name_and_path(self):
        # 获取当前系统时间，作为img和video的文件名
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        # if vid_cap:  # video
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 视频检测结果存储位置
        save_path = self.output_folder + 'video_output/' + now + '.mp4'
        return fps, w, h, save_path

    def on_video_thread_finished(self):
        # 清空界面元素
        self.label_5.clear()
        self.clean_table()

        # 重新启用所有按钮
        self.pushButton_video.setDisabled(False)
        self.pushButton_img.setDisabled(False)
        self.pushButton_camera.setDisabled(False)
        self.pushButton_pause.setDisabled(False)

        # 重置暂停按钮状态
        self.pushButton_pause.setText(u'暂停/继续')

    # 打开视频并检测
    def open_video(self):
        video_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开视频", "data/images", "*.mp4;;*.avi;;All Files(*)")
        flag = self.cap.open(video_name)
        if not flag:
            QtWidgets.QMessageBox.warning(self, u"Warning", u"打开视频失败", buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            # -------------------------写入视频----------------------------------#
            fps, w, h, save_path = self.set_video_name_and_path(video_name)
            self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
            self.video_thread = VideoProcessingThread(self.cap, self.weights, self.vid_writer, self.iou_threshold, self.confidence_threshold)
            self.video_thread.frame_signal.connect(self.show_video_frame)
            self.video_thread.finished_signal.connect(self.on_video_thread_finished)  # 连接完成信号
            self.video_thread.start()
            # 进行视频识别时，关闭其他按键点击功能
            self.pushButton_video.setDisabled(True)
            self.pushButton_img.setDisabled(True)
            self.pushButton_camera.setDisabled(True)


    # 打开摄像头检测
    def open_camera(self):
        print("Open camera to detect")
        # 设置使用的摄像头序号，系统自带为0
        camera_num = 0
        # 打开摄像头
        self.cap = cv2.VideoCapture(camera_num)
        # 判断摄像头是否处于打开状态
        bool_open = self.cap.isOpened()
        if not bool_open:
            QtWidgets.QMessageBox.warning(self, u"Warning", u"打开摄像头失败", buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            fps, w, h, save_path = self.set_camera_name_and_path()
            fps = 5  # 控制摄像头检测下的fps，Note：保存的视频，播放速度有点快，我只是粗暴的调整了FPS
            self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

            self.video_thread = VideoProcessingThread(self.cap, self.weights, self.vid_writer, self.iou_threshold, self.confidence_threshold)
            self.video_thread.frame_signal.connect(self.show_video_frame)
            self.video_thread.finished_signal.connect(self.on_video_thread_finished)  # 连接完成信号
            self.video_thread.start()

            self.pushButton_video.setDisabled(True)
            self.pushButton_img.setDisabled(True)
            self.pushButton_camera.setDisabled(True)

    # 定义视频帧显示操作
    def show_video_frame(self, annotated_img, detections):
        # 检测信息显示在界面
        self.update_statistic_table(detections)

        # 检测结果显示在界面
        self.result = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2BGRA)
        self.result = cv2.resize(self.result, (640, 480), interpolation=cv2.INTER_AREA)
        self.QtImg = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                  QtGui.QImage.Format_RGB32)
        self.label_5.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
        self.label_5.setScaledContents(True)  # 设置图像自适应界面大小

    # 暂停与继续检测
    def pause_video(self):
        if self.video_thread.isRunning and not self.video_thread.is_paused:
            self.video_thread.pause()
            self.pushButton_pause.setText(u'继续检测')
        elif self.video_thread.is_paused:
            self.video_thread.resume()
            self.pushButton_pause.setText(u'暂停检测')

    # 结束视频检测
    def finish_detect(self):
        self.video_thread.stop()  # 调用新的方法来停止线程


class VideoProcessingThread(QThread):
    frame_signal = pyqtSignal(np.ndarray, list)
    finished_signal = pyqtSignal()

    def __init__(self, cap, weights, vid_writer, iou_thres, conf_thres, parent=None):
        super(VideoProcessingThread, self).__init__(parent)
        self.cap = cap
        self.weights = weights
        self.vid_writer = vid_writer
        self.iou_thres = iou_thres
        self.conf_thres = conf_thres
        self.running = True  # 控制线程是否在处理视频
        self.is_paused = False  # 控制线程是否暂停
        self.should_stop = False  # 控制线程是否应该停止

    def run(self):
        while not self.should_stop:  # 使用 should_stop 标志来控制循环
            while self.is_paused:  # 如果线程被暂停，则在这里等待
                time.sleep(0.1)  # 稍作休息，避免 CPU 占用过高
            flag, img = self.cap.read()
            if not flag:
                break  # 如果没有帧可读，则退出循环
            if img is not None:
                annotated_img, detections = detect(img, model_path=self.weights, iou_thres=self.iou_thres, conf_thres=self.conf_thres)
                self.vid_writer.write(annotated_img)  # 检测结果写入视频
                self.frame_signal.emit(annotated_img, detections)
            else:
                break  # 如果读取帧失败，则退出循环

        self.vid_writer.release()  # 释放 VideoWriter 资源
        self.cap.release()  # 释放 VideoCapture 资源
        self.finished_signal.emit()  # 发送完成信号

    def pause(self):
        self.is_paused = True  # 暂停线程

    def resume(self):
        self.is_paused = False  # 恢复线程

    def stop(self):
        self.should_stop = True  # 设置标志以停止线程
        self.is_paused = False  # 确保线程能够退出循环

    @property
    def isRunning(self):
        return self.running and not self.is_paused  # 线程正在运行且未暂停


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = UI_Logic_Window()
    mainWindow.show()
    sys.exit(app.exec_())