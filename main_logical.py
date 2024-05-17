from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLineEdit, QDialog
import sys
from datetime import datetime

# 导入QT-Design生成的注册界面和登录界面
from ui.login_ui import Login_Ui
from ui.register_ui import Register_Ui

# 导入设计好的检测界面
from detect_logical_qthread import UI_Logic_Window

from lib.share import shareInfo # 公共变量名

from utils.id_utils import get_id_info, sava_id_info # 账号信息工具函数
from PyQt5.QtGui import QIcon, QPixmap

# 界面登录
class win_Login(QMainWindow, Login_Ui):
    def __init__(self, parent=None):
        super(win_Login, self).__init__(parent)
        self.setupUi(self)
        self.init_slots()
        self.hidden_pwd()

        icon = QIcon()
        icon.addPixmap(QPixmap('ui_img/icon.jpg'))
        self.setWindowIcon(icon)

    def init_slots(self):
        self.pushButton_login.clicked.connect(self.onSignIn)  # 点击按钮登录
        self.lineEdit_password.returnPressed.connect(self.onSignIn)  # 输入密码按下回车登录
        self.pushButton_register.clicked.connect(self.create_id)  # 点击注册跳转到注册界面

    # 密码输入框隐藏
    def hidden_pwd(self):
        self.lineEdit_password.setEchoMode(QLineEdit.Password)

    # 跳转到注册界面
    def create_id(self):
        shareInfo.createWin = win_Register()
        shareInfo.createWin.show()

    from datetime import datetime

    # 保存登录日志
    def save_login_log(self, username):
        with open('login_log.txt', 'a', encoding='utf-8') as f:
            f.write(username + '\t logged in at ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')

    # 登录
    def onSignIn(self):
        print("You pressed sign in")
        # 从登陆界面获得输入账户名与密码
        username = self.lineEdit_username.text().strip()
        password = self.lineEdit_password.text().strip()

        # 获得账号信息
        USER_PWD = get_id_info()

        if username not in USER_PWD.keys():
            QMessageBox.warning(self,"登陆失败!", "账号或密码输入错误", QMessageBox.Yes)
        else:
            if USER_PWD.get(username) != password:
                QMessageBox.warning(self, "登陆失败!", "账号或密码输入错误", QMessageBox.Yes)
            # 若登陆成功，则跳转主界面
            if USER_PWD.get(username) == password:
                self.save_login_log(username)
                print("Jump to main window")
                shareInfo.mainWin = UI_Logic_Window()
                shareInfo.mainWin.show()
                # 关闭当前窗口
                self.close()


class win_Register(QDialog, Register_Ui):
    def __init__(self, parent = None):
        super(win_Register, self).__init__(parent)
        self.setupUi(self)
        self.init_slots()

        icon = QIcon()
        icon.addPixmap(QPixmap('ui_img/icon.jpg'))
        self.setWindowIcon(icon)

    # 绑定槽信号
    def init_slots(self):
        self.pushButton_register.clicked.connect(self.new_account)
        self.pushButton_cancel.clicked.connect(self.cancel)

    # 创建新账户
    def new_account(self):
        print("Create new account")
        USER_PWD = get_id_info()
        # print(USER_PWD)
        new_username = self.lineEdit_username.text().strip()
        new_password = self.lineEdit_password.text().strip()
        # 判断用户名是否为空
        if new_username == "":
            QMessageBox.warning(self, "!", "账号不准为空", QMessageBox.Yes)
        else:
            # 判断账号是否存在
            if new_username in USER_PWD.keys():
                QMessageBox.warning(self, "!", "账号已存在", QMessageBox.Yes)
            else:
                # 判断密码是否为空
                if new_password == "":
                    QMessageBox.warning(self, "!", "密码不能为空", QMessageBox.Yes)
                else:
                    # 注册成功
                    print("Successful!")
                    sava_id_info(new_username, new_password)
                    QMessageBox.warning(self, "!", "注册成功！", QMessageBox.Yes)
                    # 关闭界面
                    self.close()

    # 取消注册
    def cancel(self):
        self.close()  # 关闭当前界面


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 利用共享变量名来实例化对象
    shareInfo.loginWin = win_Login() # 登录界面作为主界面
    shareInfo.loginWin.show()
    sys.exit(app.exec_())