import argparse
import shutil
import sys, os
from functools import partial

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.uic.properties import QtCore

import videoview
from PyQt5.QtCore import Qt, QUrl, QThread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import videoview

# 여러가지 라이브러리
import datetime, random

# json 파일 출력 라이브러리 사용
import json
from collections import OrderedDict

# 영상들 프레임 추출하기 위해 opencv 사용할 것.
import cv2
from natsort import natsorted, ns
from toolBar import ToolBar

from libs.canvas import Canvas
from libs.shape import Shape
from libs.utils import *
from libs.hashableQListWidgetItem import *
from libs.request import Request
from libs.transforms import *
from toolBar import ToolButton

DEFAULT_OBJ = ["person", "bicycle", "bus", "car", "truck", "motocycle", "carrier", "signage", "bollard", "potted_plant", "chair", "table", "fire_hydrant", "pole"]
DEFAULT_TRANSFORM = ["border_light",  # black border
                     "=====================",
                     "brightness_light", "brightness_medium", "brightness_heavy",  # 밝기 변화
                     "=====================",
                     "crop_light", "crop_medium", "crop_heavy",  # 자르기
                     "=====================",
                     "flip_light",  # 반전
                     "=====================",
                     "format_light",  # 파일 형식 변경
                     "=====================",
                     "framerate_light", "framerate_medium", "framerate_heavy",  # framerate 감소
                     "=====================",
                     "grayscale_light",  # 흑백 변환
                     "=====================",
                     "logo_light", "logo_medium", "logo_heavy",  # 로고 추가
                     "=====================",
                     "resolution_light", "resolution_medium",  # resolution 변경
                     "=====================",
                     "rotate_light"]  # 회전


class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName('{}ToolBar'.format(title))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        print("ㅗㅗ")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        print("ㅎㅎ")
        return toolbar


def newAction(parent, text, slot=None, shortcut=None,
              tip=None, icon=None, checkable=False,
              enable=True):
    a = QAction(text, parent)

    if icon is not None:
        a.setIcon(QIcon(icon))
    if shortcut is not None:
        a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)

    a.setEnabled(enable)
    print("a :", a)
    return a

def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


class TagWindow(QDialog, WindowMixin):
    def __init__(self, parent):
        # # 이 클래스에서 사용될 변수들
        self.optionFilepath = None
        self.image = None

        # info
        self.filePath = None
        self.fileName = None
        self.videoWidth = None
        self.videoHeight = None
        self.videoDuration = None
        self.videoFrames = None
        self.videoFps = None

        # transform available
        self.borderIs = False
        self.brightnessIs = False
        self.cropIs = False
        self.flipIs = False
        self.formatIs = False
        self.framerateIs = False
        self.grayscaleIs = False
        self.addlogoIs = False
        self.resolutionIs = False
        self.rotateIs = False

        # transform level
        self.border = 0
        self.brightness = 0
        self.crop = 0
        self.flip = None
        self.format = None
        self.framerate = None
        self.grayscale = None
        self.addlogoLevel = None
        self.addlogoX = 0
        self.addlogoY = 0
        self.resolution = None
        self.rotate = None
        # # 이 클래스에서 사용될 변수들

        super(TagWindow, self).__init__(parent)
        # self.resize(1500, 639)
        self.setWindowTitle("transform")

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout_18 = QtWidgets.QVBoxLayout()
        self.verticalLayout_18.setObjectName("verticalLayout_18")

        self.openVideoBtn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openVideoBtn.sizePolicy().hasHeightForWidth())
        self.openVideoBtn.setSizePolicy(sizePolicy)
        self.openVideoBtn.setMinimumSize(80, 60)
        self.openVideoBtn.setMaximumSize(80, 60)
        self.openVideoBtn.setObjectName("openVideoBtn")
        self.verticalLayout_18.addWidget(self.openVideoBtn)

        self.saveVideoBtn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveVideoBtn.sizePolicy().hasHeightForWidth())
        self.saveVideoBtn.setSizePolicy(sizePolicy)
        self.saveVideoBtn.setMinimumSize(80, 60)
        self.saveVideoBtn.setMaximumSize(80, 60)
        self.saveVideoBtn.setObjectName("saveVideoBtn")
        self.verticalLayout_18.addWidget(self.saveVideoBtn)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_18.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_18)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # canvas
        # image load
        self.canvas = Canvas()

        scroll = QScrollArea()
        scroll.setMinimumSize(650, 500)
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }

        self.verticalLayout.addWidget(scroll)


        # info
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.a1 = QtWidgets.QLabel()
        self.a1.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a1.setFont(font)
        self.a1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a1.setObjectName("a1")
        self.horizontalLayout_3.addWidget(self.a1)

        self.filePathLabel = QtWidgets.QLabel()
        self.filePathLabel.setText("")
        self.filePathLabel.setObjectName("filePathLabel")
        self.horizontalLayout_3.addWidget(self.filePathLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        self.a2 = QtWidgets.QLabel()
        self.a2.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a2.setFont(font)
        self.a2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a2.setObjectName("a2")
        self.horizontalLayout_6.addWidget(self.a2)

        self.fileNameLabel = QtWidgets.QLabel()
        self.fileNameLabel.setText("")
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.horizontalLayout_6.addWidget(self.fileNameLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")

        self.a3 = QtWidgets.QLabel()
        self.a3.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a3.setFont(font)
        self.a3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a3.setObjectName("a3")
        self.horizontalLayout_7.addWidget(self.a3)

        self.widthLabel = QtWidgets.QLabel()
        self.widthLabel.setText("")
        self.widthLabel.setObjectName("widthLabel")
        self.horizontalLayout_7.addWidget(self.widthLabel)

        self.a4 = QtWidgets.QLabel()
        self.a4.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a4.setFont(font)
        self.a4.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a4.setObjectName("a4")
        self.horizontalLayout_7.addWidget(self.a4)

        self.heightLabel = QtWidgets.QLabel()
        self.heightLabel.setText("")
        self.heightLabel.setObjectName("heightLabel")
        self.horizontalLayout_7.addWidget(self.heightLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")

        self.a5 = QtWidgets.QLabel()
        self.a5.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a5.setFont(font)
        self.a5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a5.setObjectName("a5")
        self.horizontalLayout_8.addWidget(self.a5)

        self.durationLabel = QtWidgets.QLabel()
        self.durationLabel.setText("")
        self.durationLabel.setObjectName("durationLabel")
        self.horizontalLayout_8.addWidget(self.durationLabel)

        self.a6 = QtWidgets.QLabel()
        self.a6.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a6.setFont(font)
        self.a6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a6.setObjectName("a6")
        self.horizontalLayout_8.addWidget(self.a6)

        self.framesLabel = QtWidgets.QLabel()
        self.framesLabel.setText("")
        self.framesLabel.setObjectName("framesLabel")
        self.horizontalLayout_8.addWidget(self.framesLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")

        self.a7 = QtWidgets.QLabel()
        self.a7.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.a7.setFont(font)
        self.a7.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.a7.setObjectName("a7")
        self.horizontalLayout_9.addWidget(self.a7)

        self.fpsLabel = QtWidgets.QLabel()
        self.fpsLabel.setText("")
        self.fpsLabel.setObjectName("fpsLabel")
        self.horizontalLayout_9.addWidget(self.fpsLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")

        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.borderLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.borderLabel.setFont(font)
        self.borderLabel.setObjectName("borderLabel")
        self.verticalLayout_4.addWidget(self.borderLabel)

        self.borderSlider = QtWidgets.QSlider()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.borderSlider.sizePolicy().hasHeightForWidth())
        self.borderSlider.setSizePolicy(sizePolicy)
        self.borderSlider.setOrientation(QtCore.Qt.Horizontal)
        self.borderSlider.setObjectName("borderSlider")
        self.verticalLayout_4.addWidget(self.borderSlider)
        self.horizontalLayout_13.addLayout(self.verticalLayout_4)

        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.brightnessLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.brightnessLabel.setFont(font)
        self.brightnessLabel.setObjectName("brightnessLabel")
        self.verticalLayout_3.addWidget(self.brightnessLabel)

        self.brightnessSlider = QtWidgets.QSlider()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.brightnessSlider.sizePolicy().hasHeightForWidth())
        self.brightnessSlider.setSizePolicy(sizePolicy)
        self.brightnessSlider.setOrientation(QtCore.Qt.Horizontal)
        self.brightnessSlider.setObjectName("brightnessSlider")
        self.verticalLayout_3.addWidget(self.brightnessSlider)
        self.horizontalLayout_13.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")

        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")

        self.cropLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.cropLabel.setFont(font)
        self.cropLabel.setObjectName("cropLabel")
        self.verticalLayout_7.addWidget(self.cropLabel)

        self.cropSlider = QtWidgets.QSlider()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cropSlider.sizePolicy().hasHeightForWidth())
        self.cropSlider.setSizePolicy(sizePolicy)
        self.cropSlider.setOrientation(QtCore.Qt.Horizontal)
        self.cropSlider.setObjectName("cropSlider")
        self.verticalLayout_7.addWidget(self.cropSlider)
        self.horizontalLayout_14.addLayout(self.verticalLayout_7)

        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.flipLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.flipLabel.setFont(font)
        self.flipLabel.setObjectName("flipLabel")
        self.verticalLayout_5.addWidget(self.flipLabel)

        # flip radio button
        self.flipGroup = QGroupBox()
        self.flipRadioOff = QRadioButton("off")
        self.flipRadioOff.setChecked(True)
        self.flipRadioVer = QRadioButton("ver")
        self.flipRadioHor = QRadioButton("hor")
        lbx = QHBoxLayout()
        lbx.addWidget(self.flipRadioOff)
        lbx.addWidget(self.flipRadioVer)
        lbx.addWidget(self.flipRadioHor)
        self.flipGroup.setLayout(lbx)
        self.verticalLayout_5.addWidget(self.flipGroup)
        self.horizontalLayout_14.addLayout(self.verticalLayout_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")

        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")

        self.formatLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.formatLabel.setFont(font)
        self.formatLabel.setObjectName("formatLabel")
        self.verticalLayout_11.addWidget(self.formatLabel)

        # format radio button
        self.formatGroup = QGroupBox()
        self.formatOff = QRadioButton("off")
        self.formatOff.setChecked(True)
        self.formatFlv = QRadioButton("flv")
        self.formatMp4 = QRadioButton("mp4")
        self.formatAvi = QRadioButton("avi")
        lbx = QHBoxLayout()
        lbx.addWidget(self.formatOff)
        lbx.addWidget(self.formatFlv)
        lbx.addWidget(self.formatMp4)
        lbx.addWidget(self.formatAvi)
        self.formatGroup.setLayout(lbx)
        self.verticalLayout_11.addWidget(self.formatGroup)
        self.horizontalLayout_15.addLayout(self.verticalLayout_11)

        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.framerateLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.framerateLabel.setFont(font)
        self.framerateLabel.setObjectName("framerateLabel")
        self.verticalLayout_10.addWidget(self.framerateLabel)

        # framerate radio
        self.framerateGroup = QGroupBox()
        self.framerateOff = QRadioButton("off")
        self.framerateOff.setChecked(True)
        self.framerate5 = QRadioButton("5")
        self.framerate10 = QRadioButton("10")
        self.framerate20 = QRadioButton("20")
        lbx = QHBoxLayout()
        lbx.addWidget(self.framerateOff)
        lbx.addWidget(self.framerate5)
        lbx.addWidget(self.framerate10)
        lbx.addWidget(self.framerate20)
        self.framerateGroup.setLayout(lbx)
        self.verticalLayout_10.addWidget(self.framerateGroup)

        self.horizontalLayout_15.addLayout(self.verticalLayout_10)
        self.verticalLayout_2.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")

        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")

        self.grayscaleLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.grayscaleLabel.setFont(font)
        self.grayscaleLabel.setObjectName("grayscaleLabel")
        self.verticalLayout_14.addWidget(self.grayscaleLabel)

        # grayscale on/off
        self.grayscaleGroup = QGroupBox()
        self.grayscaleOff = QRadioButton("off")
        self.grayscaleOff.setChecked(True)
        self.grayscaleOn = QRadioButton("on")
        lbx = QHBoxLayout()
        lbx.addWidget(self.grayscaleOff)
        lbx.addWidget(self.grayscaleOn)
        self.grayscaleGroup.setLayout(lbx)
        self.verticalLayout_14.addWidget(self.grayscaleGroup)

        self.horizontalLayout_10.addLayout(self.verticalLayout_14)

        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")

        self.logoLayout = QHBoxLayout()
        self.logoLayout.setObjectName("logoLayout")

        self.logoLevelBox = QComboBox()
        self.logoLevelBox.addItems(["off", "Light", "Medium", "Heavy"])

        self.addlogoLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.addlogoLabel.setFont(font)
        self.addlogoLabel.setObjectName("addlogoLabel")
        # self.verticalLayout_12.addWidget(self.addlogoLabel)

        self.logoLayout.addWidget(self.addlogoLabel)
        self.logoLayout.addWidget(self.logoLevelBox)
        self.verticalLayout_12.addLayout(self.logoLayout)

        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")

        self.adjustXLabel = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.adjustXLabel.sizePolicy().hasHeightForWidth())
        self.adjustXLabel.setSizePolicy(sizePolicy)
        self.adjustXLabel.setObjectName("adjustXLabel")
        self.horizontalLayout_16.addWidget(self.adjustXLabel)

        self.addlogoXslider = QtWidgets.QSlider()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addlogoXslider.sizePolicy().hasHeightForWidth())
        self.addlogoXslider.setSizePolicy(sizePolicy)
        self.addlogoXslider.setOrientation(QtCore.Qt.Horizontal)
        self.addlogoXslider.setObjectName("addlogoXslider")
        self.horizontalLayout_16.addWidget(self.addlogoXslider)
        self.verticalLayout_12.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")

        self.adjustYLabel = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.adjustYLabel.sizePolicy().hasHeightForWidth())
        self.adjustYLabel.setSizePolicy(sizePolicy)
        self.adjustYLabel.setObjectName("adjustYLabel")
        self.horizontalLayout_17.addWidget(self.adjustYLabel)

        self.addlogoYslider = QtWidgets.QSlider()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addlogoYslider.sizePolicy().hasHeightForWidth())
        self.addlogoYslider.setSizePolicy(sizePolicy)
        self.addlogoYslider.setOrientation(QtCore.Qt.Horizontal)
        self.addlogoYslider.setObjectName("addlogoYslider")
        self.horizontalLayout_17.addWidget(self.addlogoYslider)
        self.verticalLayout_12.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_10.addLayout(self.verticalLayout_12)
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")

        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")

        self.resolutionLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.resolutionLabel.setFont(font)
        self.resolutionLabel.setObjectName("resolutionLabel")
        self.verticalLayout_16.addWidget(self.resolutionLabel)

        # resolution radio button
        self.resolutionGroup = QGroupBox()
        self.resolutionOff = QRadioButton("off")
        self.resolutionOff.setChecked(True)
        self.resolutionCIF = QRadioButton("CIF")
        self.resolutionQCIF = QRadioButton("QCIF")
        lbx = QHBoxLayout()
        lbx.addWidget(self.resolutionOff)
        lbx.addWidget(self.resolutionCIF)
        lbx.addWidget(self.resolutionQCIF)
        self.resolutionGroup.setLayout(lbx)
        self.verticalLayout_16.addWidget(self.resolutionGroup)
        self.horizontalLayout_11.addLayout(self.verticalLayout_16)

        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")

        self.rotateLabel = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(10)
        self.rotateLabel.setFont(font)
        self.rotateLabel.setObjectName("rotateLabel")
        self.verticalLayout_15.addWidget(self.rotateLabel)

        # rotate radio button
        self.rotateGroup = QGroupBox()
        self.rotateOff = QRadioButton("off")
        self.rotateOff.setChecked(True)
        self.rotate90 = QRadioButton("90")
        self.rotate180 = QRadioButton("180")
        self.rotate270 = QRadioButton("270")
        lbx = QHBoxLayout()
        lbx.addWidget(self.rotateOff)
        lbx.addWidget(self.rotate90)
        lbx.addWidget(self.rotate180)
        lbx.addWidget(self.rotate270)
        self.rotateGroup.setLayout(lbx)
        self.verticalLayout_15.addWidget(self.rotateGroup)
        self.horizontalLayout_11.addLayout(self.verticalLayout_15)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")

        self.previewBtn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.previewBtn.sizePolicy().hasHeightForWidth())
        self.previewBtn.setSizePolicy(sizePolicy)
        self.previewBtn.setMinimumSize(QtCore.QSize(130, 0))
        self.previewBtn.setMaximumSize(QtCore.QSize(130, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.previewBtn.setFont(font)
        self.previewBtn.setObjectName("previewBtn")
        self.horizontalLayout_12.addWidget(self.previewBtn)

        self.saveBtn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveBtn.sizePolicy().hasHeightForWidth())
        self.saveBtn.setSizePolicy(sizePolicy)
        self.saveBtn.setMinimumSize(QtCore.QSize(130, 0))
        self.saveBtn.setMaximumSize(QtCore.QSize(130, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.saveBtn.setFont(font)
        self.saveBtn.setObjectName("saveBtn")
        self.horizontalLayout_12.addWidget(self.saveBtn)

        self.loadBtn = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadBtn.sizePolicy().hasHeightForWidth())
        self.loadBtn.setSizePolicy(sizePolicy)
        self.loadBtn.setMinimumSize(QtCore.QSize(130, 0))
        self.loadBtn.setMaximumSize(QtCore.QSize(130, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.loadBtn.setFont(font)
        self.loadBtn.setObjectName("loadBtn")
        self.horizontalLayout_12.addWidget(self.loadBtn)

        self.verticalLayout_2.addLayout(self.horizontalLayout_12)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        # # 함수들
        self.openVideoBtn.clicked.connect(self.openVideo)
        self.saveVideoBtn.clicked.connect(self.saveVideo)

        self.logoLevelBox.currentTextChanged.connect(self.addlogoLevel_change)

        self.flipRadioOff.toggled.connect(self.flip_change)
        self.flipRadioVer.toggled.connect(self.flip_change)
        self.flipRadioHor.toggled.connect(self.flip_change)

        self.formatOff.toggled.connect(self.format_change)
        self.formatFlv.toggled.connect(self.format_change)
        self.formatAvi.toggled.connect(self.format_change)
        self.formatMp4.toggled.connect(self.format_change)

        self.framerateOff.toggled.connect(self.framerate_change)
        self.framerate5.toggled.connect(self.framerate_change)
        self.framerate10.toggled.connect(self.framerate_change)
        self.framerate20.toggled.connect(self.framerate_change)

        self.grayscaleOff.toggled.connect(self.grayscale_change)
        self.grayscaleOn.toggled.connect(self.grayscale_change)

        self.resolutionOff.toggled.connect(self.resolution_change)
        self.resolutionCIF.toggled.connect(self.resolution_change)
        self.resolutionQCIF.toggled.connect(self.resolution_change)

        self.rotateOff.toggled.connect(self.rotate_change)
        self.rotate90.toggled.connect(self.rotate_change)
        self.rotate180.toggled.connect(self.rotate_change)
        self.rotate270.toggled.connect(self.rotate_change)

        self.borderSlider.valueChanged.connect(self.border_change)
        self.brightnessSlider.valueChanged.connect(self.brightness_change)
        self.cropSlider.valueChanged.connect(self.crop_change)
        self.addlogoXslider.valueChanged.connect(self.addlogoX_change)
        self.addlogoYslider.valueChanged.connect(self.addlogoY_change)

        # # 시스템 변수 초기 셋팅

        self.setLayout(self.gridLayout_2)
        self.retranslateUi()
        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.openVideoBtn.setText(_translate("Dialog", "Open\n""Video"))
        self.saveVideoBtn.setText(_translate("Dialog", "Save\n""Video"))
        self.a1.setText(_translate("Dialog", "file path :"))
        self.a2.setText(_translate("Dialog", "file name :"))
        self.a3.setText(_translate("Dialog", "width :"))
        self.a4.setText(_translate("Dialog", "height :"))
        self.a5.setText(_translate("Dialog", "time :"))
        self.a6.setText(_translate("Dialog", "frames :"))
        self.a7.setText(_translate("Dialog", "fps :"))
        self.borderLabel.setText(_translate("Dialog", "border"))
        self.brightnessLabel.setText(_translate("Dialog", "brightness"))
        self.cropLabel.setText(_translate("Dialog", "crop"))
        self.flipLabel.setText(_translate("Dialog", "flip"))
        self.formatLabel.setText(_translate("Dialog", "format"))
        self.framerateLabel.setText(_translate("Dialog", "framerate"))
        self.grayscaleLabel.setText(_translate("Dialog", "gray scale"))
        self.addlogoLabel.setText(_translate("Dialog", "add logo"))
        self.adjustXLabel.setText(_translate("Dialog", "x:"))
        self.adjustYLabel.setText(_translate("Dialog", "y:"))
        self.resolutionLabel.setText(_translate("Dialog", "resolution"))
        self.rotateLabel.setText(_translate("Dialog", "rotate"))
        self.previewBtn.setText(_translate("Dialog", "Priview"))
        self.saveBtn.setText(_translate("Dialog", "Save"))
        self.loadBtn.setText(_translate("Dialog", "Load"))

    def openVideo(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Choose video', '.', "Video Files (*.avi *.mp4 *.flv)")
        if filepath:
            filename = os.path.basename(filepath)
            meta_data = videoInfo(filepath)

            width = str(meta_data[0])
            height = str(meta_data[1])
            frames = str(meta_data[2])
            fps = str(meta_data[3])
            duration = str(int(meta_data[2] / meta_data[3]))

            image = meta_data[5]
            h, w, c = image.shape
            qImg = QtGui.QImage(image.data, w, h, w * c, QtGui.QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qImg).scaled(640, 480)
            # pixmap = QPixmap.fromImage(qImg).scaled(self.canvas.size())

            self.canvas.loadPixmap(pixmap)
            self.update()
            self.filePathLabel.setText(filepath)
            self.fileNameLabel.setText(filename)
            self.widthLabel.setText(width)
            self.heightLabel.setText(height)
            self.durationLabel.setText(f'{duration}s')
            self.framesLabel.setText(frames)
            self.fpsLabel.setText(fps)


    def saveVideo(self):
        print("save video")

    def transformVideo(self):
        saveDirPath = QFileDialog.getExistingDirectory()
        tempSaveDirPath = "./videos"

        index = self.videoList.count()
        for i in range(0, index):
            videopath = self.videoList.item(i).text()
            base = os.path.basename(videopath)

            count = 1
            for t in self.transforms:
                transform = t.split("_")[0]
                level = t.split("_")[1]
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                # path = tempSaveDirPath + "/" + base + "_" + str(count)
                meta_data = video_info(videopath)

                if transform == 'border': # 1
                    add_border(videopath, path, *meta_data, level="Light")
                elif transform == 'brightness': # 3
                    if level == 'light':
                        brightness(videopath, path, *meta_data, level="Light")
                    elif level == 'medium':
                        brightness(videopath, path, *meta_data, level="Medium")
                    elif level == 'heavy':
                        brightness(videopath, path, *meta_data, level="Heavy")
                elif transform == 'crop': # 3
                    if level == 'light':
                        crop(videopath, path, *meta_data, level="Light")
                    elif level == 'medium':
                        crop(videopath, path, *meta_data, level="Medium")
                    elif level == 'heavy':
                        crop(videopath, path, *meta_data, level="Heavy")
                elif transform == 'flip': # 1
                    flip(videopath, path, *meta_data, level="Light")
                elif transform == 'format': # 1
                    format(videopath, path, level="Light")
                elif transform == 'framerate': # 3
                    if level == 'light':
                        framerate(videopath, path, *meta_data, level="Light")
                    elif level == 'medium':
                        framerate(videopath, path, *meta_data, level="Medium")
                    elif level == 'heavy':
                        framerate(videopath, path, *meta_data, level="Heavy")
                elif transform == 'grayscale': # 1
                    grayscale(videopath, path, *meta_data, level="Heavy")
                elif transform == 'logo': # 3
                    if level == 'light':
                        add_logo(videopath, path, *meta_data, level="Light")
                    elif level == 'medium':
                        add_logo(videopath, path, *meta_data, level="Medium")
                    elif level == 'heavy':
                        add_logo(videopath, path, *meta_data, level="Heavy")
                elif transform == 'resolution': # 2
                    if level == 'light':
                        resolution(videopath, path, *meta_data, level="Light")
                    elif level == 'medium':
                        resolution(videopath, path, *meta_data, level="Medium")
                elif transform == 'rotate': # 1
                    rotate(videopath, path, *meta_data, level="Light")

                videopath = path
                count += 1

            base = base.split('.')[0] + "_" + str(count-1) + "." + base.split('.')[1]
            finalvideoPath = os.path.join(tempSaveDirPath, base)
            temp = saveDirPath + "/" + base
            # temp = os.path.join(saveDirPath, base)
            shutil.copyfile(finalvideoPath, temp)

        # for file in os.listdir(tempSaveDirPath):
        #     path = os.path.join(tempSaveDirPath, file)
        #     if os.path.isfile(path):
        #         print("삭제")
        #         os.remove(path)
        #         print("삭제완료")

    def border_change(self):
        self.border = self.borderSlider.value()

        if self.border == 0:
            self.borderIs = False
            print("border OFF")
        else:
            print("value :", self.border)

    def brightness_change(self):
        self.brightness = self.brightnessSlider.value()
        if self.brightness == 0:
            self.brightnessIs = False
            print("brightness OFF")
        else:
            print("value :", self.brightness)

    def crop_change(self):
        self.crop = self.borderSlider.value()
        if self.crop == 0:
            self.cropIs = False
            print("crop OFF")
        else:
            print("value :", self.crop)

    def flip_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print("flip :", radioBtn.text())

    def format_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print("format :", radioBtn.text())

    def framerate_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print("framerate :", radioBtn.text())

    def grayscale_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print("grayscale :", radioBtn.text())

    def addlogoX_change(self):
        self.addlogoX = self.addlogoXslider.value()
        if self.addlogoX == 0 and self.addlogoY == 0:
            self.brightnessIs = False
            print("add logo OFF")
        else:
            print("value :", self.addlogoX)

    def addlogoY_change(self):
        self.addlogoY = self.addlogoYslider.value()
        if self.addlogoX == 0 and self.addlogoY == 0:
            self.addlogoIs = False
            print("add logo OFF")
        else:
            print("value :", self.addlogoY)

    def addlogoLevel_change(self):
        print("current :", self.logoLevelBox.currentText())

    def resolution_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print("resolution_change :", radioBtn.text())

    def rotate_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print("rotate :", radioBtn.text())

    def jsonUpload(self):
        filename, _ = QFileDialog.getOpenFileNames(self, "Open Video")

        try:
            filename = filename[0]

            with open(filename, 'r') as f:
                json_data = json.load(f)
            # print("json_data :", json_data)
            transforms = json_data['transforms']

            self.transformList.clear()
            self.transforms = []

            for t in transforms:
                # print("t :", t)
                transform = t['transform']
                level = t['level']

                item = QListWidgetItem()
                item.setText(transform + '_' + level)
                self.transformList.addItem(item)
                self.transforms.append(transform + '_' + level)

        except:
            print("error")

    def jsonDown(self):
        filePath, _ = QFileDialog.getSaveFileName()

        if not ".json" in filePath:
            filePath = filePath + ".json"
        try :
            data = OrderedDict()
            transformData = []

            index = self.transformList.count()
            for i in range(0, index):
                item = self.transformList.item(i).text()
                transform = item.split("_")[0]
                level = item.split("_")[1]

                transformData.append({"transform": transform,
                                      "level": level})

            data["transforms"] = transformData

            with open(filePath, 'w', encoding='utf-8') as make_file:
                json.dump(data, make_file, indent="\t")

        except:
            print("error")


def videoInfo(filepath):
    cap = cv2.VideoCapture(filepath)

    if not cap.isOpened():
        print("could not open :", filepath)
        return

    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = round(cap.get(cv2.CAP_PROP_FPS), 2)
    duration = int(cap.get(cv2.CAP_PROP_POS_MSEC) * 1000)
    count = int(frames / 10)
    ret, img = None, None

    for i in range(0, count):
        ret, img = cap.read()

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return width, height, frames, fps, duration, img


def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


def parse_arguments():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(description='Request generator')
    parser.add_argument("--url", dest='url', help='URL of analysis-site', type=str, default='http://mltwins.sogang.ac.kr:8777/analyzer/')
    parser.add_argument("--image_dir", dest='image_dir', help='Image dir to send as request', type=str, default=os.path.join(os.getcwd(), "images"))
    parser.add_argument("--result_dir", dest='result_dir', help='result dir to save', type=str, default=os.path.join(os.getcwd(), "result"))
    parser.add_argument("--modules", dest='modules', help='names of analysis-module', type=str, default="faster-rcnn-cctv")

    return parser


def load_binary_image(image_path) :
    b_image = open(image_path, 'rb')
    return b_image