from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from ui.detect_ui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from detect_zy import detect
import cv2
import time
from PyQt5.QtGui import QIcon, QPixmap


class UI_Logic_Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(UI_Logic_Window, self).__init__(parent)
        self.setupUi(self)
        self.timer_video = QtCore.QTimer()  # 创建定时器
        self.signal_slot()
        self.cap = cv2.VideoCapture()
        self.num_stop = 1  # 暂停与播放辅助信号，note：通过奇偶来控制暂停与播放
        self.output_folder = 'output/'

        # 设置图标
        icon = QIcon()
        icon.addPixmap(QPixmap('ui_img/logo.jpg'))
        self.setWindowIcon(icon)


    # 绑定信号与嘈
    def signal_slot(self):
        self.pushButton_weights.clicked.connect(self.open_model)
        self.pushButton_img.clicked.connect(self.open_img)
        self.pushButton_video.clicked.connect(self.open_video)
        self.pushButton_camera.clicked.connect(self.open_camera)
        self.pushButton_pause.clicked.connect(self.pause_video)
        self.pushButton_finish.clicked.connect(self.finish_detect)

        self.timer_video.timeout.connect(self.show_video_frame)  # 定时器超时，将槽绑定至show_video_frame


    # 打开权重文件
    def open_model(self):
        self.openfile_name_model, _ = QFileDialog.getOpenFileName(self.pushButton_weights, '选择weights文件',
                                                                  'weights/')
        if not self.openfile_name_model:
            QMessageBox.warning(self, u"Warning", u"打开权重失败", buttons=QMessageBox.Ok,
                                          defaultButton=QMessageBox.Ok)
        else:
            print('加载weights文件地址为：' + str(self.openfile_name_model))

        self.weights = self.openfile_name_model


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
                annotated_img, detections = detect(img, model_path=self.weights)
                # 获取当前系统时间，作为img文件名
                now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
                file_name = img_name.split('/')[-1]
                new_filename = file_name.split('.')[0] + '_' + now + '.' + file_name.split('.')[-1]  # 获得文件后缀名
                file_path = self.output_folder + 'img_output/' + new_filename
                cv2.imwrite(file_path, annotated_img)

                # 检测信息显示在界面
                self.textBrowser.setText(str(detections))

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

    # 打开视频并检测
    def open_video(self):
        video_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开视频", "data/images", "*.mp4;;*.avi;;All Files(*)")
        flag = self.cap.open(video_name)
        if not flag:
            QtWidgets.QMessageBox.warning(self, u"Warning", u"打开视频失败", buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            self.timer_video.start(30)  # 以30ms为间隔，启动或重启定时器
            # 进行视频识别时，关闭其他按键点击功能
            self.pushButton_video.setDisabled(True)
            self.pushButton_img.setDisabled(True)
            self.pushButton_camera.setDisabled(True)

            # -------------------------写入视频----------------------------------#
            fps, w, h, save_path = self.set_video_name_and_path(video_name)
            self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

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
            self.timer_video.start(30)
            self.pushButton_video.setDisabled(True)
            self.pushButton_img.setDisabled(True)
            self.pushButton_camera.setDisabled(True)

            fps, w, h, save_path = self.set_camera_name_and_path()
            fps = 5  # 控制摄像头检测下的fps，Note：保存的视频，播放速度有点快，我只是粗暴的调整了FPS
            self.vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    # 定义视频帧显示操作
    def show_video_frame(self):
        flag, img = self.cap.read()
        if img is not None:
            annotated_img, detections = detect(img, model_path=self.weights)
            self.vid_writer.write(annotated_img)  # 检测结果写入视频
            # 检测信息显示在界面
            self.textBrowser.setText(str(detections))

            # 检测结果显示在界面
            self.result = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2BGRA)
            self.result = cv2.resize(self.result, (640, 480), interpolation=cv2.INTER_AREA)
            self.QtImg = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                      QtGui.QImage.Format_RGB32)
            self.label_5.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
            self.label_5.setScaledContents(True)  # 设置图像自适应界面大小

        else:
            self.timer_video.stop()
            # 读写结束，释放资源
            self.cap.release()  # 释放video_capture资源
            # 视频帧显示期间，禁用其他检测按键功能
            self.pushButton_video.setDisabled(False)
            self.pushButton_img.setDisabled(False)
            self.pushButton_camera.setDisabled(False)

    # 暂停与继续检测
    def pause_video(self):
        self.timer_video.blockSignals(False)
        # 暂停检测
        # 若QTimer已经触发，且激活
        if self.timer_video.isActive() == True and self.num_stop % 2 == 1:
            self.pushButton_pause.setText(u'暂停检测')  # 当前状态为暂停状态
            self.num_stop = self.num_stop + 1  # 调整标记信号为偶数
            self.timer_video.blockSignals(True)
        # 继续检测
        else:
            self.num_stop = self.num_stop + 1
            self.pushButton_pause.setText(u'继续检测')

    # 结束视频检测
    def finish_detect(self):
        # self.timer_video.stop()
        self.cap.release()  # 释放video_capture资源
        self.label_5.clear()  # 清空label画布
        self.textBrowser.clear() # 清楚检测信息
        # 启动其他检测按键功能
        self.pushButton_video.setDisabled(False)
        self.pushButton_img.setDisabled(False)
        self.pushButton_camera.setDisabled(False)

        # 结束检测时，查看暂停功能是否复位，将暂停功能恢复至初始状态
        # Note:点击暂停之后，num_stop为偶数状态
        self.pushButton_pause.setText(u'暂停/继续')
        self.num_stop = self.num_stop + 1
        self.timer_video.blockSignals(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = UI_Logic_Window()
    mainWindow.show()
    sys.exit(app.exec_())