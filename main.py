from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtCore import *
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import *
from moviepy.editor import VideoFileClip
import threading
import cv2
import sys, os
import PySide2
import datetime
import firstSource
import matplotlib
import matplotlib.pyplot as plt
import secondSource
from PySide2.QtGui import QMovie
import sys
import numpy as np

import shutil
from decimal import Decimal

matplotlib.use('agg')
sys.path.append('deploy')

from MyControl import *
from PIL import Image

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ['PYTHON_EXE'] = sys.executable

class status():
    def __init__(self):
        # self.handleCalc()
        #正常情况下应该是先跳转到主页menu，现在主页还没完善好，因此先跳转到行人单目标检测
        self.id_num = 0
        self.handleCalc()
        # note: 添加变量
        self.file_path = []  # 用于保存结果文件
        self.video_path = []  # 用于保存选择的视频路径
        self.final_time = 0
        self.txt_output_path = ''
        self.video_output_path = ''
        self.txt_statistic_output_path = ''
        # self.is_enter = False

    def show_ui(self, location):
        loca="ui/"+location
        qfile_staus = QFile(loca)
        qfile_staus.open(QFile.ReadOnly)
        qfile_staus.close()
        self.ui = QUiLoader().load(qfile_staus)
        self.ui.setWindowTitle("百度飞桨PP-Tracking")
        appIcon = QIcon("source/first/logo.jpg")
        self.ui.setWindowIcon(appIcon)

    def help_set_shadow(self, x_offset
                        , y_offset
                        , radius
                        , color
                        , *control):
        for x in control:
            tempEffect = QGraphicsDropShadowEffect(self.ui)
            tempEffect.setOffset(x_offset, y_offset)
            tempEffect.setBlurRadius(radius)  # 阴影半径
            tempEffect.setColor(color)
            x.setGraphicsEffect(tempEffect)

    def help_set_style_sheet(self, s, *controllers):
        for x in controllers:
            x.setStyleSheet(s)

    def help_hide(self, *control):
        for x in control:
            x.setVisible(False)

    def help_set_up(self, *control):
        for x in control:
            x.raise_()

    def help_set_edit(self, edit, one):
        if one == 1 or one == -1:
            self.time = self.time + one
            if self.time>999: self.time=999
            if self.time<0: self.time=0
            edit.setText(str(self.time))
        else:
            # self.confi = float(float(self.confi) + float(one))
            self.confi = Decimal(str(self.confi)) + Decimal(str(one))
            self.confi = Decimal(self.confi).quantize(Decimal("0.00"))
            if self.confi > 1.0: self.confi = 1.0
            if self.confi < 0.0: self.confi = 0.0
            edit.setText(str(self.confi))

    def help_set_edit_by_hand_new(self, edit):
        text = edit.text()
        if not text.isdigit():
            QMessageBox.warning(self.ui, '错误提示', '只能输入整形数字！')
        else:
            self.std = int(edit.text())
            now = int(edit.text())
            if self.std>9999: self.std = 9999
            if self.std<0: self.std = 0
            if now != self.std: edit.setText(str(self.std))

    def help_set_edit_by_hand(self, edit, one):
        if one == 1:
            text = edit.text()
            if not text.isdigit():
                QMessageBox.warning(self.ui, '错误提示', '只能输入整形数字！')
            else:
                self.time = int(edit.text())
                now = int(edit.text())
                if self.time>999: self.time = 999
                if self.time<0: self.time = 0
                if now != self.time: edit.setText(str(self.time))
        else:
            self.confi = int(Decimal(str(edit.text())) * 100)
            self.confi = Decimal(str(self.confi / 100.0))
            now = Decimal(str(edit.text()))
            if self.confi > 1.0: self.confi = 1.0
            if self.confi < 0.0: self.confi = 0.0
            if now != self.confi:
                edit.setText(str(self.confi))

    def help_set_spinBox(self, edit, add, down, one):
        edit.textChanged.connect(lambda: self.help_set_edit_by_hand(edit, one))
        add.clicked.connect(lambda: self.help_set_edit(edit, one))
        down.clicked.connect(lambda: self.help_set_edit(edit, -1*one))

    def help_set_progress(self, len, progress, show_label):
        """
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        用来更新那个进度条的函数
        ！！！注意更新进度条的时候一定要先修改self.progressPos,
        self.progressPos是一个0到1的小数

        :param len:指的是总进度条的长度，是120
        :param progress: 指的是self.ui.label_progressBar,直接传这个参数就可以
        :param show_label:是self.ui.label_progressBar_num，直接传这个
        :return:
        """
        show_label.setText('  ')
        progress.resize(int(self.progressPos*len), progress.height())


    def handleCalc(self):
        self.show_ui("main_menu.ui")
        self.have_show_video = 0
        self.is_tracking = '--draw_center_traj'
        self.is_enter_surely = 0
        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget1
                             , self.ui.widget1_2
                             , self.ui.widget1_3)
        self.help_set_shadow(-10, 10, 30, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget
                             , self.ui.widget_3
                             , self.ui.widget_4
                             , self.ui.widget_5
                             , self.ui.widget_6
                             , self.ui.widget_7
                             , self.ui.widget_8)
        test_video=r"C:\Users\Administrator\Desktop\university\d4199e42f744cbe3be7f5ac262cd9056.mp4"
        label1 = MyMenuVideoLabel("source/second/menu_pedestrian.PNG"
                                , 360, 184, 320, 180
                                , test_video
                                , self.ui)

        label2 = MyMenuVideoLabel("source/second/menu_car.PNG"
                                , 800, 184, 320, 180
                                , test_video
                                , self.ui)

        label3 = MyMenuVideoLabel("source/second/menu_muti_object.PNG"
                                  , 1240, 184, 320, 180
                                  , test_video
                                  , self.ui)
        self.ui.show()
        self.ui.pushButton.clicked.connect(self.pedestrian_menu)
        self.ui.pushButton_2.clicked.connect(self.car_menu)
        self.ui.pushButton_3.clicked.connect(self.mult_menu)

    def load_son_menu(self, menu_ui, id):
        # 后面完善的话还要传入那些video和video的一开始的图片
        self.clear_video()
        self.show_ui(menu_ui)
        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget1
                             , self.ui.widget1_2
                             , self.ui.widget1_3)
        self.help_set_shadow(0, 4, 0, QColor(221, 221, 221, 0.3 * 255), self.ui.label_3)
        test_video = r"C:\Users\Administrator\Desktop\university\d4199e42f744cbe3be7f5ac262cd9056.mp4"
        if id == 1:
            label1 = MyMenuVideoLabel("source/second/people_one.PNG"
                                      , 360, 400, 320, 180
                                      , test_video
                                      , self.ui)
            label2 = MyMenuVideoLabel("source/second/people_small.PNG"
                                      , 800, 400, 320, 180
                                      , test_video
                                      , self.ui)
            label3 = MyMenuVideoLabel("source/second/people_two.PNG"
                                      , 1240, 400, 320, 180
                                      , test_video
                                      , self.ui)
        elif id == 2:
            label1 = MyMenuVideoLabel("source/second/car_one.PNG"
                                      , 360, 400, 320, 180
                                      , test_video
                                      , self.ui)
            label2 = MyMenuVideoLabel("source/second/car_small.PNG"
                                      , 800, 400, 320, 180
                                      , test_video
                                      , self.ui)
            label3 = MyMenuVideoLabel("source/second/car_two.PNG"
                                      , 1240, 400, 320, 180
                                      , test_video
                                      , self.ui)
        self.ui.show()

    def pedestrian_menu(self):
        self.is_mult = False
        self.is_enter_surely = 0
        self.load_son_menu("pedestrian_menu.ui", 1)
        self.ui.pushButton.clicked.connect(self.pedestrian_one_photo)
        self.ui.pushButton_2.clicked.connect(self.pedestrian_small_object)
        self.ui.pushButton_3.clicked.connect(self.pedestrian_double_photo)
        self.ui.pushButton_12.clicked.connect(self.handleCalc)

    def car_menu(self):
        self.is_mult = False
        self.is_enter_surely = 0
        self.load_son_menu("car_menu.ui", 2)
        self.ui.pushButton_12.clicked.connect(self.handleCalc)
        self.ui.pushButton.clicked.connect(self.car_one_photo)
        self.ui.pushButton_2.clicked.connect(self.car_small_object)
        self.ui.pushButton_3.clicked.connect(self.car_double_photo)

    def mult_menu(self):
        self.clear_video()
        self.is_mult=True
        self.show_ui("mult_menu.ui")
        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget1_2
                             , self.ui.widget1_3)
        self.help_set_shadow(0, 4, 0, QColor(221, 221, 221, 0.3 * 255), self.ui.label_3)
        test_video = r"C:\Users\Administrator\Desktop\university\d4199e42f744cbe3be7f5ac262cd9056.mp4"
        label1 = MyMenuVideoLabel("source/second/other_one.PNG"
                                  , 580, 400, 320, 180
                                  , test_video
                                  , self.ui)
        label2 = MyMenuVideoLabel("source/second/other_two.PNG"
                                  , 1020, 400, 320, 180
                                  , test_video
                                  , self.ui)
        self.ui.pushButton_12.clicked.connect(self.handleCalc)
        self.ui.show()
        self.show_list = []
        self.ui.pushButton_2.clicked.connect(self.mult_one_photo)
        self.ui.pushButton_3.clicked.connect(self.mult_small_object)

    def pedestrian_one_photo(self):
        self.universe_for_one_small("pedestrian_one_photo.ui",
                                    "pedestrian_one_photo_working.ui",
                                    "pedestrian_one_photo_working_enter.ui")
        self.page_id = 1
        self.is_draw_line = ''
        self.come_back=self.pedestrian_menu
        self.ui.pushButton_13.clicked.connect(self.come_back)

    def pedestrian_small_object(self):
        self.page_id = 3
        self.universe_for_one_small("pedestrian_small_object.ui",
                                    "pedestrian_small_object_working.ui",
                                    "pedestrian_small_object_working_enter.ui")
        self.is_draw_line = ''
        self.come_back = self.pedestrian_menu
        self.ui.pushButton_13.clicked.connect(self.come_back)

    def pedestrian_double_photo(self):
        self.page_id = 4
        self.universe_for_double("pedestrian_double_photo.ui",
                                 "pedestrian_double_photo_working.ui")
        self.come_back = self.pedestrian_menu
        self.is_draw_line = ''
        self.ui.pushButton_13.clicked.connect(self.come_back)

    def car_one_photo(self):
        self.page_id = 2
        self.universe_for_one_small("car_one_photo.ui",
                                    "car_one_photo_working.ui",
                                    "car_one_photo_working_enter.ui")
        self.is_draw_line = ''
        self.come_back=self.car_menu
        self.ui.pushButton_13.clicked.connect(self.come_back)

    def car_small_object(self):
        self.page_id = 5
        self.universe_for_one_small("car_small_object.ui",
                                    "car_small_object_working.ui",
                                    "car_small_object_working_enter.ui")
        self.is_draw_line = ''
        self.come_back = self.car_menu
        self.ui.pushButton_13.clicked.connect(self.come_back)

    def car_double_photo(self):
        self.page_id = 6
        self.universe_for_double("car_double_photo.ui",
                                 "car_double_photo_working.ui")
        self.come_back = self.car_menu
        self.is_draw_line = ''
        self.ui.pushButton_13.clicked.connect(self.come_back)

    def universe_for_double(self, first_ui, next_ui):
        self.show_ui(first_ui)
        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget_2)
        self.have_show_video = 2
        self.is_draw_line = ''
        self.ui.pushButton_5.clicked.connect(
            lambda: self.load_video1(self.ui.pushButton_5
                                     , self.ui.label_15)
        )
        self.ui.pushButton_10.clicked.connect(
            lambda: self.load_video1(self.ui.pushButton_10
                                     , self.ui.label_16)
        )
        self.not_enter_ui = next_ui
        self.confi = 0.5
        self.time = 0
        self.std = 10
        self.progressPos = 0.0
        self.ui.show()

    def universe_for_one_small(self,
                               first_ui,
                               not_enter_ui,
                               is_enter_ui):
        self.show_ui(first_ui)
        self.file_path = []
        self.video_path = []
        self.is_draw_line = ''
        # 先设置shadow
        self.have_show_video=1
        self.help_set_shadow(0, 4, 0, QColor(221, 221, 221, 0.3 * 255)
                             , self.ui.label_3)
        self.help_set_shadow(0, 0, 50, QColor(221, 221, 221, 0.3 * 255)
                             , self.ui.widget_2, self.ui.widget_3)
        self.not_enter_ui = not_enter_ui
        self.is_enter_ui = is_enter_ui
        self.confi = 0.5
        self.time = 0
        self.std = 10
        self.progressPos = 0.00
        self.ui.pushButton_addVideo.clicked.connect(
            lambda: self.load_video1(self.ui.pushButton_addVideo,
                                     self.ui.label_24)
        )

        self.ui.show()

    def mult_one_photo(self):
        self.page_id = 7
        self.is_draw_line = ''
        self.show_ui("mult_one_photo.ui")
        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget_2)
        self.come_back = self.mult_menu
        self.have_show_video = 1
        self.ui.pushButton_addVideo.clicked.connect(
            lambda: self.load_video1(self.ui.pushButton_addVideo
                                     , self.ui.label_24)
        )
        self.ui.pushButton_13.clicked.connect(self.come_back)
        self.not_enter_ui = "mult_one_photo_working.ui"
        self.confi = 0.5
        self.time = 0
        self.std = 10
        self.progressPos = 0.00
        self.ui.show()


    def mult_small_object(self):
        self.page_id = 8
        self.show_ui("mult_small_object.ui")
        self.is_draw_line = ''
        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget_2)
        self.come_back = self.mult_menu
        self.have_show_video = 1
        self.ui.pushButton_addVideo.clicked.connect(
            lambda: self.load_video1(self.ui.pushButton_addVideo
                                     , self.ui.label_24)
        )
        self.ui.pushButton_13.clicked.connect(self.come_back)
        # note：初始时加载的界面错了，此处做了调整
        self.not_enter_ui = "mult_small_object_working.ui"
        self.confi = 0.5
        self.time = 0
        self.std = 10
        self.progressPos = 0.00
        self.ui.show()

    def one_photo_change_enter(self):
        """
        每一次改变是否切换出入口，要先：
        1.配置基本需要用代码配置的ui
        2.手动调整的值要从原来的复制过去
        每个控件的值，除了手动调整的，其他都是根据推理结果更新，不用管
        3.将暂停键之类的各种键配置好
        :return:
        """
        result = []
        result.append(self.lineEditConfi.text())
        # result.append(self.ui.lineEdit_2.text())
        # print(self.ui.lineEdit_2.text())


        if self.is_enter == False:
            self.is_enter = True
            self.is_enter_surely = 1
            self.is_draw_line = '--do_entrance_counting'
            self.init_base_ui_for_one_photo_changing_enter(self.is_enter_ui)
        elif self.is_enter == True:
            self.is_enter = False
            self.is_enter_surely = 0
            self.is_draw_line = ''
            self.init_base_ui_for_one_photo_changing_enter(self.not_enter_ui)

        self.lineEditConfi.setText("0.5")
        # self.ui.lineEdit_2.setText(result[1])

        # note:无法选择按钮暂时变灰
        self.ui.pushButton_2.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        self.ui.pushButton_3.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        self.ui.pushButton_8.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")

        self.cap4 = cv2.VideoCapture(self.video_path[0])
        ret, frame = self.cap4.read()
        self.have_show_time = 0
        self.Display_Image(frame, self.ui.label_7)

        # to do: 解决出入口界面的问题
        # self.is_enter_surely = 1
        print(self.is_enter_surely)

        self.load_video_controller()
        self.load_control_for_one_photo()
        return

    def init_base_ui_for_double_photo(self, ui_location):
        self.show_ui(ui_location)
        s = """QLineEdit{\nwidth: 80px;\nheight: 40px;\nbackground: #FFFFFF;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\n\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #333333;\nline-height: 26px;\nfont-weight:bold;\n}"""
        self.lineEditConfi = MyLineEdit(self.ui.label_confi_tip, s
                                        , 0, 352, 930, 57, 42, self.ui)
        # s = """QPushButton{\nwidth: 120px;\nheight: 40px;\nborder-radius: 4px;\nborder: 1px solid #4E4EF2;\nfont-weight:bold;\n\nfont-size: 16px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #4E4EF2;\nline-height: 24px;\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(255, 255, 255, 204);\nborder-radius: 4px;\nborder: 1px solid rgba(78, 78, 242, 204);\n\nfont-weight:bold;\nfont-size: 16px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: rgba(78, 78, 242, 204);\nline-height: 24px;\n}"""
        # self.output_txt = MyPushButton(self.ui.label_txt_tip, s
        #                                , "导出文件", 1507.5, 290, 126, 44, self.ui)

        self.help_set_shadow(0, 0, 50, QColor(0, 0, 0, 0.06 * 255)
                             , self.ui.widget_2)

        if self.have_show_video == 2:
            self.listWidget = QListWidget(self.ui)
            self.listWidget.setStyleSheet("""QListWidget{border:0px;}QListWidget:item{margin:10px 0px 10px 0px;}""")
            self.listWidget.move(1322, 358 + 16 + 36)
            self.listWidget.resize(370, 540 - 16 - 40)

        self.ui.pushButton_13.clicked.connect(self.come_back)

        # note:无法选择按钮暂时变灰
        self.ui.pushButton_2.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        self.ui.pushButton_3.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        self.ui.pushButton_8.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        # note:初始时隐藏当前视频帧数显示，点击结果显示按钮后才显示出来
        self.ui.label_22.setVisible(False)
        self.ui.label_frames.setVisible(False)
        self.ui.show()
        # note: 添加双镜头显示视频图片：
        if(len(self.video_path)==2):
            self.cap4 = cv2.VideoCapture(self.video_path[0])
            ret, frame = self.cap4.read()
            self.have_show_time = 0
            self.Display_Image(frame, self.ui.label_7)
            self.cap5 = cv2.VideoCapture(self.video_path[1])
            ret, frame = self.cap5.read()
            self.have_show_time = 0
            self.Display_Image(frame, self.ui.label_14)
        elif(len(self.video_path)==1):
            self.cap4 = cv2.VideoCapture(self.video_path[0])
            ret, frame = self.cap4.read()
            self.have_show_time = 0
            self.Display_Image(frame, self.ui.label_7)

    def init_base_ui_for_one_photo_changing_enter(self, ui_location):
        self.show_ui(ui_location)
        s = """QLineEdit{\nwidth: 80px;\nheight: 40px;\nbackground: #FFFFFF;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\n\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #333333;\nline-height: 26px;\nfont-weight:bold;\n}"""
        self.lineEditConfi = MyLineEdit(self.ui.label_confi_tip, s
                                        , 0, 352, 930, 57, 42, self.ui)
        # s = """QPushButton{\nwidth: 126px;\nheight: 44px;\nbackground: #FFFFFF;\nborder-radius: 4px;\nborder: 1px solid #4E4EF2;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #4E4EF2;\nline-height: 26px;\nfont-weight:bold;\n}"""
        # self.output_txt = MyPushButton(self.ui.label_txt_tip, s
        #                                , "导出文件", 1507.5, 290, 126, 44, self.ui)
        self.help_set_shadow(0, 4, 0, QColor(221, 221, 221, 0.3 * 255)
                             , self.ui.label_3)
        self.help_set_shadow(0, 0, 50, QColor(221, 221, 221, 0.3 * 255)
                             , self.ui.widget_2, self.ui.widget_3)
        # note:无法选择按钮暂时变灰
        self.ui.pushButton_2.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        self.ui.pushButton_3.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")
        self.ui.pushButton_8.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")

        self.ui.pushButton_10.clicked.connect(self.one_photo_change_enter)
        self.ui.pushButton_13.clicked.connect(self.come_back)
        # note:初始时隐藏当前视频帧数显示，点击结果显示按钮后才显示出来
        self.ui.label_22.setVisible(False)
        self.ui.label_frames.setVisible(False)
        self.ui.show()

        # note：添加显示视频图片
        self.cap3 = cv2.VideoCapture(self.video_path[0])
        ret, frame = self.cap3.read()
        self.have_show_time = 0
        self.Display_Image(frame, self.ui.label_7)


    def load_control_for_double_photo(self):
        self.help_set_spinBox(self.lineEditConfi,
                              self.ui.pushButton_7,
                              self.ui.pushButton_11,
                              0.01)

    def load_control_for_one_photo(self):
        self.help_set_spinBox(self.lineEditConfi,
                              self.ui.pushButton_7,
                              self.ui.pushButton_11,
                              0.01)

        # 可视化界面： 时段长度和人流密度标准添加限制
        if self.is_enter_surely == 0:
            self.help_set_spinBox(self.ui.lineEdit_2,
                                  self.ui.pushButton_5,
                                  self.ui.pushButton_6,
                                  1)
            self.ui.lineEdit_3.textChanged.connect(lambda: self.help_set_edit_by_hand_new(self.ui.lineEdit_3))

        return

    def load_control_for_one_mult_photo(self):
        self.help_set_spinBox(self.lineEditConfi, self.ui.pushButton_7
                              , self.ui.pushButton_11, 0.01)

        # self.help_set_spinBox(self.ui.lineEdit_2, self.ui.pushButton_5
        #                       , self.ui.pushButton_6, 1)
        return

    def load_video(self, control_hide, control_label):
        """
        :param video_count: 要导入视频的数量，单镜头是1，跨境是2
        :return:
        """
        num_now = len(self.file_path)
        filePath = self.open_one_file_dialog("选择视频", 0)
        if filePath == "":
            return
        self.file_path.append(filePath)
        # note: 保存选择的视频路径
        self.video_path.append(filePath)

        if len(self.file_path) < self.have_show_video:
            # 数量对不上就return，说明没有给够
            return

        self.time = 2
        self.std = 10

        # note: 判断是否打开出入口界面并进行跳转
        if self.have_show_video == 1 and self.is_mult == False:
            self.is_enter = False
            self.init_base_ui_for_one_photo_changing_enter(self.not_enter_ui)
        else:
            self.init_base_ui_for_double_photo(self.not_enter_ui)

        self.lineEditConfi.setText("0.5")

        self.model_file_path = self.file_path[0]

        file_temp_split_path = self.file_path[0].split('.')
        self.file_name = file_temp_split_path[0]

        # note: 修改使得支持多视频格式
        # self.file_path[0] = 'output/' + file_temp_split_path[0].split('/')[-1] + '.mp4'
        self.file_path[0] = 'output/' + self.file_path[0].split('/')[-1]

        # 结果文件默认输出路径
        self.video_output_path = self.file_path[0]
        if self.page_id == 7 or self.page_id == 8:
            self.txt_output_path = 'output/' + file_temp_split_path[0].split('/')[-1] + '.txt'
        else:
            self.txt_output_path = 'output/' + file_temp_split_path[0].split('/')[-1] + '.txt'
            self.txt_statistic_output_path = 'output/' + file_temp_split_path[0].split('/')[-1] + '_flow_statistic.txt'
        print(self.txt_output_path)

        if self.page_id == 7:
            pic = QPixmap('source/second/mul_one.png')
            self.ui.label_9.setPixmap(pic)
            self.ui.label_9.setScaledContents(True)
        elif self.page_id == 8:
            # note：初始时加载路径错了，进行修正
            pic = QPixmap('source/second/small_mul.png')
            self.ui.label_9.setPixmap(pic)
            self.ui.label_9.setScaledContents(True)

        self.open_video()

    def load_model(self):
        if self.is_enter_surely == 0:
            # 获取时段长度值
            period_length = self.ui.lineEdit_2.text()
            period = '--secs_interval=%s'%(period_length)
            print(period)
            # 时段长度失效
            self.ui.pushButton_5.setEnabled(False)
            self.ui.pushButton_6.setEnabled(False)
            self.ui.lineEdit_2.setEnabled(False)
            text = self.ui.lineEdit_2.text()
            if not text.isdigit():
                QMessageBox.warning(self.ui, '错误提示', '人流密度值只能为整形数字！')
                return
        else:
            period = ''
            print(period)

        print('加载单类别模型')
        print(self.file_name)
        file_name_test = self.file_name.split('/')
        file_path_test = self.file_path[0].split('/')
        file_name_test_start = file_name_test[len(file_name_test) - 1]
        self.file_name = file_name_test_start + '.mp4'
        self.end_file_name = self.file_name

        # self.ui.label_23.setFixedSize \
        #     (self.ui.label_23.width(), self.ui.label_23.height())

        # note：获取取消轨迹复选框状态，判断是否取消轨迹
        if self.ui.checkBox.checkState() == Qt.Checked:
            self.is_tracking = ''
        else:
            self.is_tracking = '--draw_center_traj'

        # 模型开始运行及运行完成后让按钮及复选框失效掉
        self.ui.checkBox.setEnabled(False)  # 取消轨迹复选框
        # 阈值调试失效
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_11.setEnabled(False)
        self.lineEditConfi.setEnabled(False)

        # 让人流密度指标调整失效
        if self.is_enter_surely == 0:
            self.standard = self.ui.lineEdit_3.text()
            self.ui.lineEdit_3.setEnabled(False)

        self.ui.pushButton_10.setEnabled(False)  # 让开关出入口失效

        # 将开关出入口设置为灰色，表示不可选
        self.ui.pushButton_10.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 40px;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-weight:bold;\nwidth: 80px;\nheight: 24px;\nfont-size: 16px;\nfont-family:\nAlibabaPuHuiTi_2_65_Medium;\nline-height: 24px;\ncolor: #888888;\n}")

        starttime = datetime.datetime.now()
        # note：添加异常捕获
        try:
            #判断是行人模型还是车辆模型
            print("*******************************************************")
            print(self.confi)
            # draw_center_traj
            print(self.is_draw_line)
            print(self.is_tracking)
            print("lzclzclzclzclzclzc")
            python_exe = os.environ['PYTHON_EXE']
            if self.page_id == 1:
                print("当前是行人模型")
                val = os.system(
                    '%s deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/fairmot_hrnetv2_w18_dlafpn_30e_576x320 --video_file=%s   --save_mot_txts --device=GPU --threshold=%s %s %s %s' \
                    % (python_exe, self.model_file_path, self.confi, self.is_tracking, self.is_draw_line, period))
            elif self.page_id == 2:
                print("当前是车辆模型")
                val = os.system(
                    '%s deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/fairmot_hrnetv2_w18_dlafpn_30e_576x320_bdd100kmot_vehicle --video_file=%s  --save_mot_txts --device=GPU --threshold=%s %s %s %s' \
                    % (python_exe, self.model_file_path, self.confi, self.is_tracking, self.is_draw_line, period))
            elif self.page_id == 3:
                print("当前是行人小目标跟踪模型")
                val = os.system(
                    '%s deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/fairmot_hrnetv2_w18_dlafpn_30e_1088x608_visdrone_pedestrian --video_file=%s   --save_mot_txts --device=GPU --threshold=%s %s %s %s' \
                    % (python_exe, self.model_file_path, self.confi, self.is_tracking, self.is_draw_line, period))
            elif self.page_id == 5:
                print("当前是车辆小目标跟踪模型")
                val = os.system(
                    '%s deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/fairmot_hrnetv2_w18_dlafpn_30e_576x320_visdrone_vehicle --video_file=%s  --save_mot_txts --device=GPU --threshold=%s %s %s %s' \
                    % (python_exe, self.model_file_path, self.confi, self.is_tracking, self.is_draw_line, period))
            elif self.page_id == 7:
                val = os.system(
                    '%s deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/mcfairmot_hrnetv2_w18_dlafpn_30e_576x320_bdd100k_mcmot --video_file=%s  --save_mot_txts --device=GPU --threshold=%s %s %s' \
                    % (python_exe, self.model_file_path, self.confi, self.is_tracking, self.is_draw_line))
            else:
                val = os.system(
                    '%s deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/mcfairmot_hrnetv2_w18_dlafpn_30e_1088x608_visdrone --video_file=%s  --save_mot_txts --device=GPU --threshold=%s %s %s' \
                    % (python_exe, self.model_file_path, self.confi, self.is_tracking, self.is_draw_line))
        except Exception as e:
            print(e)  # 打印所有异常到屏幕
            QMessageBox.warning(self.ui, '错误提示', '模型运行发生异常!\n报错信息:' + e)
            return

        endtime = datetime.datetime.now()
        starttime_count = starttime.hour * 3600 + starttime.minute * 60 + starttime.second
        endtime_count = endtime.hour * 3600 + endtime.minute * 60 + endtime.second
        self.final_time = str(endtime_count - starttime_count)
        self.ui.label_28.setText(str((endtime_count - starttime_count)))

        # note: 优化FPS显示问题
        if self.is_enter_surely == 0:
            self.cap1 = cv2.VideoCapture(self.file_path[0])
            self.ui.label_26.setText(str(round(self.cap1.get(cv2.CAP_PROP_FPS))))
            # self.ui.label_26.setText(str(round(self.cap1.get(cv2.CAP_PROP_FPS))))

        # self.synthesis_vide(val, self.file_name)
        if self.is_enter_surely == 0:
            self.read_txt_file()
        else:
            self.read_enter_txt_file()

        pic = QPixmap('source/second/model_ok.png')
        self.ui.label_7.setFixedSize(960, 540)
        self.ui.label_7.move(60, 108)
        self.ui.label_7.setPixmap(pic)
        self.ui.label_7.setScaledContents(True)

        # note：运行结束重新把按钮由灰变蓝
        self.ui.pushButton_2.setStyleSheet("QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #4E4EF2;;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF;\nline-height: 26px;\nfont-weight:bold\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(78, 78, 242, 204);\nborder-radius: 4px;\nopacity: 0.8;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF; \nline-height: 26px;\nfont-weight: bold;}")
        self.ui.pushButton_3.setStyleSheet("QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #4E4EF2;;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF;\nline-height: 26px;\nfont-weight:bold\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(78, 78, 242, 204);\nborder-radius: 4px;\nopacity: 0.8;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF; \nline-height: 26px;\nfont-weight: bold;}")
        self.ui.pushButton_8.setStyleSheet("QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #4E4EF2;;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF;\nline-height: 26px;\nfont-weight:bold\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(78, 78, 242, 204);\nborder-radius: 4px;\nopacity: 0.8;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF; \nline-height: 26px;\nfont-weight: bold;}")

        # note: 运行结束后重新开放开启出入口功能
        self.ui.pushButton_10.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 40px;\nborder-radius: 4px;\nborder: 1px solid #4E4EF2;\nfont-weight:bold;\nfont-size: 16px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #4E4EF2;\nline-height: 24px;\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: #FFFFFF;\nborder-radius: 4px;\nborder: 1px solid #4E4EF2;\nfont-weight:bold;\nfont-size: 16px;\nfont-family:AlibabaPuHuiTi_2_65_Medium;\ncolor: #4E4EF2;\nline-height: 24px;\n}")
        self.ui.pushButton_10.setEnabled(True)

        # 模型运行结束后开放功能
        self.ui.pushButton_2.setEnabled(True)  # 结果显示
        self.ui.pushButton_3.setEnabled(True)  # 停止运行
        self.ui.pushButton_8.setEnabled(True)  # 导出结果

    def load_model_mult(self):
        print('加载多类别模型')

        print(self.file_name)
        file_name_test = self.file_name.split('/')
        file_path_test = self.file_path[0].split('/')
        file_name_test_start = file_name_test[len(file_name_test) - 1]
        self.file_name = file_name_test_start + '.mp4'
        self.end_file_name = self.file_name

        # self.ui.label_23.setFixedSize \
        #     (self.ui.label_23.width(), self.ui.label_23.height())

        # note：获取取消轨迹复选框状态，判断是否取消轨迹
        if self.ui.checkBox.checkState() == Qt.Checked:
            self.is_tracking = ''
        else:
            self.is_tracking = '--draw_center_traj'

        # 模型开始运行及运行完成后让按钮及复选框失效掉
        self.ui.checkBox.setEnabled(False)  # 取消轨迹复选框
        # 阈值调试失效
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_11.setEnabled(False)
        self.lineEditConfi.setEnabled(False)

        starttime = datetime.datetime.now()
        # note: 添加异常捕获
        try:
            # 判断是行人模型还是车辆模型
            print("*******************************************************")
            print(self.confi)
            # draw_center_traj
            print(self.is_draw_line)
            print(self.is_tracking)
            print("lzclzclzclzclzclzc")
            if self.page_id == 7:
                val = os.system(
                    'python deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/mcfairmot_hrnetv2_w18_dlafpn_30e_576x320_bdd100k_mcmot --video_file=%s  --save_mot_txts --device=GPU --threshold=%s %s %s' \
                    % (self.model_file_path, self.confi, self.is_tracking, self.is_draw_line))
            else:
                val = os.system(
                    'python deploy/pptracking/python/mot_jde_infer.py --model_dir=output_inference/mcfairmot_hrnetv2_w18_dlafpn_30e_1088x608_visdrone --video_file=%s  --save_mot_txts --device=GPU --threshold=%s %s %s' \
                    % (self.model_file_path, self.confi, self.is_tracking, self.is_draw_line))
        except Exception as e:
            print(e)  # 打印所有异常到屏幕
            QMessageBox.warning(self.ui, '错误提示', '模型运行发生异常!\n报错信息:' + e)
            return

        endtime = datetime.datetime.now()
        starttime_count = starttime.hour * 3600 + starttime.minute * 60 + starttime.second
        endtime_count = endtime.hour * 3600 + endtime.minute * 60 + endtime.second

        pic = QPixmap('source/second/model_ok.png')
        self.ui.label_7.setFixedSize(960, 540)
        self.ui.label_7.move(60, 108)
        self.ui.label_7.setPixmap(pic)
        self.ui.label_7.setScaledContents(True)

        # self.synthesis_vide(val, self.file_name)
        # self.ui.label_17.setText("运行时间" + str((endtime_count - starttime_count)) /
        #                          +"运行FPS" + str(round(self.cap1.get(cv2.CAP_PROP_FPS))))

        # note：运行结束重新把按钮由灰变蓝
        self.ui.pushButton_2.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #4E4EF2;;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF;\nline-height: 26px;\nfont-weight:bold\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(78, 78, 242, 204);\nborder-radius: 4px;\nopacity: 0.8;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF; \nline-height: 26px;\nfont-weight: bold;}")
        self.ui.pushButton_3.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #4E4EF2;;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF;\nline-height: 26px;\nfont-weight:bold\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(78, 78, 242, 204);\nborder-radius: 4px;\nopacity: 0.8;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF; \nline-height: 26px;\nfont-weight: bold;}")
        self.ui.pushButton_8.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #4E4EF2;;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF;\nline-height: 26px;\nfont-weight:bold\n}\nQPushButton:hover{\nwidth: 120px;\nheight: 44px;\nbackground: rgba(78, 78, 242, 204);\nborder-radius: 4px;\nopacity: 0.8;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #FFFFFF; \nline-height: 26px;\nfont-weight: bold;}")
        # 模型运行结束后开放功能
        self.ui.pushButton_2.setEnabled(True)  # 结果显示
        self.ui.pushButton_3.setEnabled(True)  # 停止运行
        self.ui.pushButton_8.setEnabled(True)  # 导出结果

    # note: 添加导出结果功能：选择输出文件夹，将结果文件拷贝到该路径下
    def output_result(self):
        # 选择目录，返回选中的路径
        output_path = QFileDialog.getExistingDirectory(self.ui,
                                                       "选择文件输出路径",
                                                       r"./")
        if output_path is None:
            return
        else:
            print('导出文件路径:' + output_path)

        # ps:后续添加完善选择输出文件路径
        video = self.file_path[0].split('/')[-1]
        if self.page_id == 7 or self.page_id == 8:
            shutil.copy(self.video_output_path, output_path)
            shutil.copy(self.txt_output_path, output_path)
            temp = self.file_path[0].split('.')
            txt = temp[0].split('/')[-1] + '.txt'
            QMessageBox.information(self.ui, 'success', '结果导出成功！\n效果视频：' + video + '\n结果文件：' + txt)
        else:
            shutil.copy(self.video_output_path, output_path)
            shutil.copy(self.txt_output_path, output_path)
            shutil.copy(self.txt_statistic_output_path, output_path)
            temp = self.file_path[0].split('.')
            txt = temp[0].split('/')[-1] + '.txt'
            txt_statistic = temp[0].split('/')[-1] + '_flow_statistic.txt'
            if self.page_id == 1 or self.page_id == 3:
                if self.is_enter_surely == 0:
                    shutil.copy('output/people_image.png', output_path)
                    QMessageBox.information(self.ui, 'success', '结果导出成功！\n效果视频：' + video + '\n结果文件：' + txt + '\n数据统计文件：' + txt_statistic + '\n可视化绘图：people_image.png')
                else:
                    QMessageBox.information(self.ui, 'success',
                                            '结果导出成功！\n效果视频：' + video + '\n结果文件：' + txt + '\n数据统计文件：' + txt_statistic)
            elif self.page_id == 3 or self.page_id == 5:
                if self.is_enter_surely == 0:
                    shutil.copy('output/car_image.png', output_path)
                    QMessageBox.information(self.ui, 'success', '结果导出成功！\n效果视频：' + video + '\n结果文件：' + txt + '\n数据统计文件：' + txt_statistic + '\n可视化绘图：car_image.png')
                else:
                    QMessageBox.information(self.ui, 'success',
                                            '结果导出成功！\n效果视频：' + video + '\n结果文件：' + txt + '\n数据统计文件：' + txt_statistic)
            else:
                QMessageBox.information(self.ui, 'success', '结果导出成功！\n效果视频：' + video + '\n结果文件：' + txt + '\n数据统计文件：' + txt_statistic)

    def read_enter_txt_file(self):
        self.ui.label_26.setText(str(self.final_time))
        end_file_name_list = self.end_file_name.split('.')
        self.end_file_name = end_file_name_list[0]
        f = open('output/' + self.end_file_name + '_flow_statistic.txt', 'r')
        with open('output/' + self.end_file_name + '_flow_statistic.txt', 'r') as f1:
            list = f1.readlines()
        current_count_list_y = []
        current_count_list_x = []
        for i in range(len(list)):
            new_temp_list = list[i].strip('\n').split(' ')
            current_count = new_temp_list[8]
            current_count_in = current_count.split(',')
            current_count_in_true = current_count_in[0]
            current_count_1 = new_temp_list[11]
            current_count_2 = new_temp_list[5].split(',')
            self.current_count = current_count_2[0]
            current_count_out = current_count_1.split(',')
            current_count_out_true = current_count_out[0]
            current_count = new_temp_list[len(new_temp_list) - 1]
            current_count_list_y.append(current_count)
            current_count_list_x.append(i)
        self.end_line_enter_one_eidt = int(float(self.lineEditConfi.text()))
        print(self.current_count)
        self.ui.label_28.setText(str(self.current_count))
        self.ui.label_32.setText(str(self.current_count))
        self.ui.label_34.setText(str(current_count_in_true))
        self.ui.label_36.setText(str(current_count_out_true))

    def read_txt_file_mult(self):
        end_file_name_list = self.end_file_name.split('.')
        self.end_file_name = end_file_name_list[0]
        f = open('output/' + self.end_file_name + '_flow_statistic.txt', 'r')
        with open('output/' + self.end_file_name + '_flow_statistic.txt', 'r') as f1:
            list = f1.readlines()
        current_count_list_y = []
        current_count_list_x = []
        y_test = []
        line_text_2 = self.ui.lineEdit_2.text()
        test = int(int(line_text_2) / 50) + 1
        iter = 0
        for i in range(test):
            new_temp_list = list[iter - 1].strip('\n').split(' ')
            current_count = new_temp_list[len(new_temp_list) - 1]
            print(new_temp_list)
            temp_current_count = current_count.split(',')
            print(temp_current_count[0])
            current_count = int(temp_current_count[0])
            current_count_list_y.append(current_count)
            current_count_list_x.append(i)
            iter = iter + 50
        for i in range(len(current_count_list_y)):
            y_test.append(10)
        plt.plot(current_count_list_x,current_count_list_y, mec='r', mfc='w', label='people')
        plt.plot(current_count_list_x, y_test, ms=10, label='Boundary')
        plt.legend()  # 让图例生效
        plt.margins(0)
        plt.subplots_adjust(bottom=0.10)
        plt.savefig('output/people_image.png')
        # plt.show()

        # 当前的人数计数
        self.current_count = current_count_list_y[len(current_count_list_y) - 1]
        f.close()
        frames_num = self.cap1.get(7)
        fps = int(round(self.cap1.get(cv2.CAP_PROP_FPS)))

    def read_txt_file(self):
        end_file_name_list = self.end_file_name.split('.')
        self.end_file_name = end_file_name_list[0]
        f = open('output/' + self.end_file_name + '_flow_statistic.txt', 'r')
        with open('output/' + self.end_file_name + '_flow_statistic.txt', 'r') as f1:
            list = f1.readlines()

        current_count_list_y = []
        current_count_list_x = []

        # 人流密度标准
        standard = int(self.standard)
        # 时段长度
        interval = int(self.ui.lineEdit_2.text())

        first = list[0].split(' ')[-1].replace("\n", "")
        current_count_list_y.append(int(first))
        current_count_list_x.append(0)

        y_test = []
        iter = 1
        for i in range(len(list)):
            judge = list[i].split(' ')[-2]
            if judge == 'secs:':
                count = list[i].split(' ')[-1].replace("\n", "")
                count = int(count)
                current_count_list_y.append(count)
                current_count_list_x.append(iter * interval)
                iter += 1

        for i in range(len(current_count_list_y)):
            y_test.append(standard)

        # 判断是人流还是车流
        if self.page_id == 1 or self.page_id == 3:
            plt.plot(current_count_list_x, current_count_list_y, c='blue', mec='r', mfc='w', label='Pedestrian volume')
            plt.plot(current_count_list_x, y_test, c='brown', ms=standard, label='Density standard')
            below_threshold = np.array(current_count_list_y) < int(standard)
            plt.scatter(np.array(current_count_list_x)[below_threshold],
                        np.array(current_count_list_y)[below_threshold],
                        color='green', marker='^', linewidths=4)
            above_threshold = np.logical_not(below_threshold)
            plt.scatter(np.array(current_count_list_x)[above_threshold],
                        np.array(current_count_list_y)[above_threshold],
                        color='red', marker='v', linewidths=4)
            min = np.array(current_count_list_y).min()
            max = np.array(current_count_list_y).max()
            if min > standard:
                min = standard
            if max < standard:
                max = standard
            plt.ylim(min - 2, max + 2)
            plt.legend()  # 让图例生效
            plt.margins(0)
            # plt.subplots_adjust(bottom=0.10)
            plt.savefig('output/people_image.png')
            # plt.show()
            pic = QPixmap('output/people_image.png')

        elif self.page_id == 2 or self.page_id == 5:
            plt.plot(current_count_list_x, current_count_list_y, c='blue', mec='r', mfc='w', label='Car volume')
            plt.plot(current_count_list_x, y_test, c='brown', ms=standard, label='Density standard')
            below_threshold = np.array(current_count_list_y) < int(standard)
            plt.scatter(np.array(current_count_list_x)[below_threshold],
                        np.array(current_count_list_y)[below_threshold],
                        color='green', marker='^', linewidths=4)
            above_threshold = np.logical_not(below_threshold)
            plt.scatter(np.array(current_count_list_x)[above_threshold],
                        np.array(current_count_list_y)[above_threshold],
                        color='red', marker='v', linewidths=4)
            min = np.array(current_count_list_y).min()
            max = np.array(current_count_list_y).max()
            if min > standard:
                min = standard
            if max < standard:
                max = standard
            plt.ylim(min - 2, max + 2)
            plt.legend()  # 让图例生效
            plt.margins(0)
            # plt.subplots_adjust(bottom=0.10)
            plt.savefig('output/car_image.png')
            # plt.show()
            pic = QPixmap('output/car_image.png')

        self.ui.label_33.setPixmap(pic)
        self.ui.label_33.setScaledContents(True)

        # 当前的人数计数
        # self.current_count = current_count_list_y[len(current_count_list_y) - 1]

        totalcount = list[-1].split(',')[1].split(' ')[-1]
        print('total: ' + totalcount)
        self.ui.label_30.setText(str(totalcount))
        f.close()
        # print(self.cap1[0])
        # frames_num = self.cap1.get(7)
        # fps = int(round(self.cap1.get(cv2.CAP_PROP_FPS)))

    def synthesis_vide(self, val, video_name):
        video_name_list = video_name.split('.')
        video_name = video_name_list[0]
        if val == 0:
            self.img_root = 'output/' + video_name + '/'
            fps = 13
            test_size = self.img_root + "00000.png"
            file_size_path = Image.open(test_size)
            img = file_size_path.size  # 获取文件尺寸
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.vW = cv2.VideoWriter(video_name + '_output_test.mp4', fourcc, fps, img)
            self.video_factory(len(os.listdir(self.img_root)))  # 合成视频

    def video_factory(self, n):
        for i in range(1, n):
            s = '%05d' % i
            print(s)
            frame = cv2.imread(self.img_root + str(s) + '.png')
            self.vW.write(frame)
        self.vW.release()

    def load_video1(self, control_hide, control_label):
        self.load_video(control_hide, control_label)

    def load_video2(self, control_hide, control_label):
        self.load_video(control_hide, control_label)

    def open_video(self):
        self.have_show_time=0
        self.frame1 = []
        self.cap1 = []
        self.timer_camera1 = []
        self.ui.label_7.setFixedSize\
            (self.ui.label_7.width(), self.ui.label_7.height())
        print(self.file_path[0])
        self.frame_count = 0
        self.timer_camera1 = QTimer()
        self.load_video_controller()
        if self.have_show_video==1 and self.is_mult==False:self.load_control_for_one_photo()
        if self.have_show_video==1 and self.is_mult==True:self.load_control_for_one_mult_photo()
        if self.have_show_video==2:
            self.frame2 = []
            self.cap2 = []
            self.timer_camera2 = []
            self.ui.label_14.setFixedSize \
                (self.ui.label_14.width(), self.ui.label_14.height())
            self.cap2 = cv2.VideoCapture(self.file_path[1])
            self.timer_camera2 = QTimer()
            self.load_control_for_double_photo()

    def load_video_controller(self):
        self.ui.pushButton.clicked.connect(self.video_pause)
        self.ui.pushButton_2.clicked.connect(self.video_start)
        self.ui.pushButton_3.clicked.connect(self.video_stop)
        self.ui.pushButton_8.clicked.connect(self.output_result)

    def video_stop(self):
        self.timer_camera1.stop()
        if self.cap1 is not None:
            self.cap1.release()
        if self.have_show_video == 2:
            self.timer_camera2.stop()
            if self.cap2 is not None:
                self.cap2.release()
        # 可以让视频被清除掉，或者一些其他的功能

    def video_start(self):
        print('视频开始播放!')
        self.frame_count = 0
        self.cap1 = cv2.VideoCapture(self.file_path[0])
        # note: 点击结果显示按钮后显示当前视频播放的视频帧数
        self.ui.label_22.setVisible(True)
        self.ui.label_frames.setVisible(True)

        if self.page_id == 8 or self.page_id == 7:
            self.frame_count = 0
        else:
            self.ui.label_26.setText(str(round(self.cap1.get(cv2.CAP_PROP_FPS))))
        self.timer_camera1.start(120)
        self.timer_camera1.timeout.connect(self.OpenFrame1)
        if self.have_show_video == 2:
            self.timer_camera2.start(100)
            self.timer_camera2.timeout.connect(self.OpenFrame2)

    def video_start_mult(self):
        # note: 点击结果显示按钮后显示当前视频播放的视频帧数
        self.ui.label_22.setVisible(True)
        self.ui.label_frames.setVisible(True)
        self.frame_count = 0
        self.cap1 = cv2.VideoCapture(self.file_path[0])
        self.timer_camera1.start(120)
        self.timer_camera1.timeout.connect(self.OpenFrame1)
        if self.have_show_video == 2:
            self.timer_camera2.start(100)
            self.timer_camera2.timeout.connect(self.OpenFrame2)

    def video_pause(self):

        # note: 检测对应预测模型存不存在，并弹窗提示
        # 行人跟踪模型
        if self.page_id == 1 and not os.path.exists('output_inference/fairmot_hrnetv2_w18_dlafpn_30e_576x320'):
            QMessageBox.warning(self.ui, '错误提示', '行人跟踪预测模型不存在，请先下载预测模型到./output_inference目录下!')
            return
        # 行人小目标跟踪模型
        elif self.page_id == 3 and not os.path.exists('output_inference/fairmot_hrnetv2_w18_dlafpn_30e_1088x608_visdrone_pedestrian'):
            QMessageBox.warning(self.ui, '错误提示', '行人小目标跟踪预测模型不存在，请先下载预测模型到./output_inference目录下!')
            return
        # 车辆跟踪模型
        elif self.page_id == 2 and not os.path.exists('output_inference/fairmot_hrnetv2_w18_dlafpn_30e_576x320_bdd100kmot_vehicle'):
            QMessageBox.warning(self.ui, '错误提示', '车辆跟踪预测模型不存在，请先下载预测模型到./output_inference目录下!')
            return
        # 车辆小目标跟踪模型
        elif self.page_id == 5 and not os.path.exists('output_inference/fairmot_hrnetv2_w18_dlafpn_30e_576x320_visdrone_vehicle'):
            QMessageBox.warning(self.ui, '错误提示', '车辆小目标跟踪预测模型不存在，请先下载预测模型到./output_inference目录下!')
            return
        # 多类别跟踪模型
        elif self.page_id == 7 and not os.path.exists('output_inference/mcfairmot_hrnetv2_w18_dlafpn_30e_576x320_bdd100k_mcmot'):
            QMessageBox.warning(self.ui, '错误提示', '多类别跟踪预测模型不存在，请先下载预测模型到./output_inference目录下!')
            return
        # 多类别小目标跟踪模型
        elif self.page_id == 8 and not os.path.exists('output_inference/mcfairmot_hrnetv2_w18_dlafpn_30e_1088x608_visdrone'):
            QMessageBox.warning(self.ui, '错误提示', '多类别小目标跟踪预测模型不存在，请先下载预测模型到./output_inference目录下!')
            return

        if self.page_id == 4 or self.page_id == 6:
            QMessageBox.information(self.ui, '提示', '跨境头功能尚在完善中，敬请期待!')
            return

        # note：运行后显示运行中
        # pic = QPixmap('source/second/loading.png')
        # self.ui.label_7.setPixmap(pic)
        # self.ui.label_7.setScaledContents(True)

        # note: 后续可尝试添加显示动态gif
        self.movie = QMovie('source/second/pp.gif')
        self.ui.label_7.setMovie(self.movie)
        self.ui.label_7.setFixedSize(320, 320)
        self.ui.label_7.move(350, 195)
        self.movie.start()

        # self.timer_camera1.stop()
        # if self.have_show_video == 2:
        #     self.timer_camera2.stop()

        self.ui.pushButton.setStyleSheet(
            "QPushButton{\nwidth: 120px;\nheight: 44px;\nbackground: #F5F5F5;\nborder-radius: 4px;\nborder: 1px solid #CCCCCC;\nfont-size: 18px;\nfont-family: AlibabaPuHuiTi_2_65_Medium;\ncolor: #B8B8B8;\nline-height: 26px;\nfont-weight:bold\n}")

        if self.page_id == 8 or self.page_id == 7:
            self.t1 = threading.Thread(target=self.load_model_mult)
            self.t1.start()
        else:
            self.t1 = threading.Thread(target=self.load_model)
            self.t1.start()

    def OpenFrame1(self):
        ret, frame = self.cap1.read()
        if ret:
            self.Display_Image(frame, self.ui.label_7)
            self.frame_count = self.frame_count + 1
            self.ui.label_frames.setText(str(self.frame_count))
        else:
            print("播放结束")
            self.cap1.release()
            self.timer_camera1.stop()

    def OpenFrame2(self):
        ret, frame = self.cap2.read()
        if ret:
            self.Display_Image(frame, self.ui.label_14)
        else:
            print("播放结束")
            self.cap2.release()
            self.timer_camera2.stop()


    def clear_video(self):
        self.file_path = []
        self.video_path = []
        if self.have_show_video==1 or self.have_show_video==2:
            if hasattr(self,"cap1") == False:return
            if self.timer_camera1 == []:return
            # note:添加空判定
            if self.timer_camera1 is None:return
            self.timer_camera1.stop()
            # note:暂时注释掉改行
            # self.cap1.release()
            self.timer_camera1=None
            self.cap1=None
        if self.have_show_video==2:
            # note:添加空判定
            if self.timer_camera2 is None: return
            self.timer_camera2.stop()
            self.cap2.release()
            self.timer_camera2 = None
            self.cap2 = None
        self.have_show_video=0

    def Display_Image(self, image, controller):
        """
        ！！！！！！！！！！！！！！！！！！这里一定要看
        最关键的是这个函数
        参数image就是要展示在页面里的视频

        除此之外，对各种展示信息的更新，直接在这个函数里对相应控件进行更新就可以

        然后所有需要手动设置的参数，阙值和时间长度，只要在页面上设置好，这里就能知道
        阙值：self.confi
        时间: self.time
        :param image:
        :param controller:
        :return:
        """
        self.have_show_time=self.have_show_time + 1
        if (len(image.shape) == 3):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            Q_img = QImage(image.data,
                           image.shape[1],
                           image.shape[0],
                           QImage.Format_RGB888)
        elif (len(image.shape) == 1):
            Q_img = QImage(image.data,
                           image.shape[1],
                           image.shape[0],
                           QImage.Format_Indexed8)
        else:
            Q_img = QImage(image.data,
                           image.shape[1],
                           image.shape[0],
                           QImage.Format_RGB888)
        controller.setPixmap(QtGui.QPixmap(Q_img))
        controller.setScaledContents(True)
        if (self.have_show_time/self.have_show_video) % 50 == 0 and self.have_show_video == 2:
            # 这里只针对多镜头检测
            item = QListWidgetItem()
            self.listWidget.addItem(item)
            item.setSizeHint(QSize(330, 70))
            widget = QWidget()
            widget.resize(330, 70)
            # f = open('test.txt', 'r')
            first_info="source/second/menu_car.PNG"
            second_info="source/second/menu_car.PNG"
            id_num=self.id_num
            self.id_num=self.id_num+1
            """
            !!!!!!!!!!!!!!!!!!!!
            这里的注释必看！！！！！
            如果是随着视频播放，检测数据进行更新的话，这里将会进行更新
            first_info是跨境头检测的，检测数据的，第一张图片
            second_info是第二章图片
            id_num是第几个也就是id
            """
            label1 = double_photo_show_label(widget, 0, first_info
                                             , 10, 0, 100, 70)
            label2 = double_photo_show_label(widget, 0, second_info
                                             , 126, 0, 100, 70)
            label3 = double_photo_show_label(widget, 1, id_num
                                             , 242, 17, 98, 36)
            self.listWidget.setItemWidget(item, widget)



    def chose_all_self_picture(self):
        """
        全选
        :return:
        """
        count = self.ui.listWidget.count()
        for i in range(count):
            self.ui.listWidget.itemWidget(self.ui.listWidget.item(i))\
                .setChecked(True)

    def save_self_picture(self):
        """
        保存图片
        :return:
        """
        count = self.ui.listWidget.count()
        # 得到QListWidget的总个数
        cb_list = [self.ui.listWidget.itemWidget(self.ui.listWidget.item(i))
                   for i in range(count)]
        # 得到QListWidget里面所有QListWidgetItem中的QCheckBox
        # print(cb_list)
        chooses = []  # 存放被选择的数据
        for cb in cb_list:  # type:QCheckBox
            if cb.isChecked():
                chooses.append(cb.text())
        print(chooses)

    def clean_self_list_widget(self):
        self.ui.listWidget.clear()

    def switchType(self, type):
        """
        :param type: 1的话是图片 0的话是视频
        :return:
        """
        if type == 1:
            return "图片类型 (*.png *.jpg *.bmp)"
        else:
            # note:添加支持选择更多视频及文件格式
            return "视频类型 (*.mp4 *.avi *.mov *.rmvb *.flac)"

    """
    ------------------------------打开单个文件的函数
    """

    def open_one_file_dialog(self, title, type):
        """
        :param title: 标题
        :param type: 类型 1的话是图片 0的话是视频
        :return:
        """
        type = self.switchType(type)
        filePath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            title,  # 标题
            r"./",  # 起始目录
            type  # 选择类型过滤项，过滤内容在括号中
        )
        return filePath

    def open_count_file_dialog(self, title, type, limit=-1):
        """
        :param title: 标题
        :param type: 类型
        :return:
        """
        type = self.switchType(type)
        filePath, _ = QFileDialog.getOpenFileNames(
            self.ui,  # 父窗口对象
            title,  # 标题
            r"C:\Users\Administrator\Desktop\university",  # 起始目录
            type  # 选择类型过滤项，过滤内容在括号中
        )
        if len(filePath) > limit and limit != -1:
            QMessageBox.critical(
                self.ui,
                '错误',
                '你选择的文件数量过多')

if __name__ == '__main__':

    app = QApplication([])
    MainWindow=QMainWindow()
    statu = status()
    statu.ui.show()
    app.exec_()



