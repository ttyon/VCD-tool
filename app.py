import argparse
import shutil
import sys, os
from functools import partial

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.uic.properties import QtCore

from PyQt5.QtCore import Qt, QUrl, QThread
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

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
from libs.utils import *
from libs.request import Request
from libs.transforms import *
from toolBar import ToolButton

res = {
    'SqCIF': (128, 96),
    'qCIF': (176, 144),
    'CIF': (352, 288),
    'qVGA': (320, 240),
    'VGA': (640, 480), # SD, 480p와 동일
    }


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
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
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
    return a

def addActions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


class TagWindow(QDialog):
    def __init__(self):
        # # 이 클래스에서 사용될 변수들
        self.videoPath = None
        self.videoName = None
        self.optionFilepath = None
        self.image = None
        self.qImg = None
        self.pixmap = None
        self.progress = None
        self.logoPath = None

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

        super().__init__()
        # self.resize(1500, 639)
        self.setWindowTitle("transform")

        # system layout
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

        self.borderGroup = QGroupBox()
        self.borderOff = QRadioButton("off")
        self.borderOff.setChecked(True)
        self.borderCIF = QRadioButton("CIF")
        self.borderVGA = QRadioButton("VGA")
        lbx = QHBoxLayout()
        lbx.addWidget(self.borderOff)
        lbx.addWidget(self.borderCIF)
        lbx.addWidget(self.borderVGA)
        self.borderGroup.setLayout(lbx)
        self.verticalLayout_4.addWidget(self.borderGroup)

        # self.borderSlider = QtWidgets.QSlider()
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.borderSlider.sizePolicy().hasHeightForWidth())
        # self.borderSlider.setSizePolicy(sizePolicy)
        # self.borderSlider.setOrientation(QtCore.Qt.Horizontal)
        # self.borderSlider.setObjectName("borderSlider")
        # self.verticalLayout_4.addWidget(self.borderSlider)
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

        self.brightnessBox = QComboBox()
        self.brightnessBox.addItems(["-36", "-18", "-9", "0", "9", "18", "36"])

        self.brightnessBox.setCurrentIndex(3)
        self.verticalLayout_3.addWidget(self.brightnessBox)

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
        self.cropSlider.setMinimum(0)
        self.cropSlider.setMaximum(100)
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
        # self.formatFlv = QRadioButton(".flv")
        self.formatMp4 = QRadioButton(".mp4")
        self.formatAvi = QRadioButton(".avi")
        lbx = QHBoxLayout()
        lbx.addWidget(self.formatOff)
        # lbx.addWidget(self.formatFlv)
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
        self.brightnessBox.currentTextChanged.connect(self.brightness_change)

        self.borderOff.toggled.connect(self.border_change)
        self.borderVGA.toggled.connect(self.border_change)
        self.borderCIF.toggled.connect(self.border_change)

        self.flipRadioOff.toggled.connect(self.flip_change)
        self.flipRadioVer.toggled.connect(self.flip_change)
        self.flipRadioHor.toggled.connect(self.flip_change)

        self.formatOff.toggled.connect(self.format_change)
        # self.formatFlv.toggled.connect(self.format_change)
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

        # self.borderSlider.valueChanged.connect(self.border_change)
        self.cropSlider.valueChanged.connect(self.crop_change)
        self.addlogoXslider.valueChanged.connect(self.addlogoX_change)
        self.addlogoYslider.valueChanged.connect(self.addlogoY_change)

        self.saveBtn.clicked.connect(self.jsonSave)
        self.loadBtn.clicked.connect(self.jsonLoad)

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
        self.saveBtn.setText(_translate("Dialog", "Save"))
        self.loadBtn.setText(_translate("Dialog", "Load"))

    def openVideo(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Choose video', '.', "Video Files (*.avi *.mp4 *.flv)")
        if filepath:
            filename = os.path.basename(filepath)
            self.videoPath = filepath
            self.videoName = filename

            meta_data = videoInfo(filepath)

            width = str(meta_data[0])
            height = str(meta_data[1])
            frames = str(meta_data[2])
            fps = str(meta_data[3])
            duration = str(int(meta_data[2] / meta_data[3]))

            image = meta_data[5]
            h, w, c = image.shape
            qImg = QtGui.QImage(image.data, w, h, w * c, QtGui.QImage.Format_RGB888)
            self.qImg = qImg
            self.image = image

            # pixmap = QPixmap.fromImage(qImg).scaled(640, 480)
            pixmap = QPixmap.fromImage(qImg)
            # pixmap = QPixmap.fromImage(qImg).scaled(self.canvas.size())
            self.pixmap = pixmap

            self.canvas.loadPixmap(pixmap)
            self.update()
            self.filePathLabel.setText(filepath)
            self.fileNameLabel.setText(filename)
            self.widthLabel.setText(width)
            self.heightLabel.setText(height)
            self.durationLabel.setText(f'{duration}s')
            self.framesLabel.setText(frames)
            self.fpsLabel.setText(fps)

    def changeImage(self, qImg):
        pixmap = QPixmap.fromImage(qImg)
        self.canvas.loadPixmap(pixmap)

    def preview(self):
        if self.qImg is not None:
            # src = QtGui.QImage(src.data, src.shape[1], src.shape[0], QtGui.QImage.Format_RGB32)
            cvImage = self.image

            if self.brightnessIs:
                if self.brightness > 0:
                    array = np.full(cvImage.shape, (self.brightness, self.brightness, self.brightness), dtype=np.uint8)
                    cvImage = cv2.add(cvImage, array)
                else:
                    array = np.full(cvImage.shape, (-self.brightness, -self.brightness, -self.brightness), dtype=np.uint8)
                    cvImage = cv2.subtract(cvImage, array)

            if self.cropIs:
                height = cvImage.shape[0]
                width = cvImage.shape[1]

                re_height = int(height - (height * self.crop))
                re_width = int(width - (width * self.crop))

                y_start = (height - re_height) / 2
                x_start = (width - re_width) / 2

                y_end = height - y_start
                x_end = width - x_start

                temp = cvImage[int(y_start):int(y_end), int(x_start):int(x_end)]
                dst = temp.copy()
                dst[0:re_height, 0:re_width] = temp
                cvImage = dst
            if self.flipIs:
                if self.flip == 'vflip':
                    cvImage = cv2.flip(cvImage, 0)
                elif self.flip == 'hflip':
                    cvImage = cv2.flip(cvImage, 1)
            if self.grayscaleIs:
                temp = cvImage.copy()

                b = temp[:, :, 0]
                g = temp[:, :, 1]
                r = temp[:, :, 2]

                result = ((0.299 * r) + (0.587 * g) + (0.114 * b))

                temp = result.astype(np.uint8)
                cvImage = temp
                # cvImage = cv2.cvtColor(cvImage, cv2.COLOR_RGB2GRAY)
                # print(cvImage.shape)
            if self.rotateIs:
                if not self.addlogoIs:
                    if self.rotate == 90:
                        cvImage = cv2.rotate(cvImage, cv2.ROTATE_90_CLOCKWISE)
                    elif self.rotate == 180:
                        cvImage = cv2.rotate(cvImage, cv2.ROTATE_180)
                    elif self.rotate == 270:
                        cvImage = cv2.rotate(cvImage, cv2.ROTATE_90_COUNTERCLOCKWISE)
                else:
                    if self.rotate == 90:
                        temp_w = int(self.heightLabel.text())
                        temp_h = int(self.widthLabel.text())
                    elif self.rotate == 180:
                        temp_w = int(self.widthLabel.text())
                        temp_h = int(self.heightLabel.text())
                    elif self.rotate == 270:
                        temp_w = int(self.heightLabel.text())
                        temp_h = int(self.widthLabel.text())

                    logoImg = cv2.imread(self.logoPath)
                    logo_w = logoImg.shape[1]
                    logo_h = logoImg.shape[0]

                    if temp_w > logo_w and temp_h > logo_h:
                        if self.rotate == 90:
                            cvImage = cv2.rotate(cvImage, cv2.ROTATE_90_CLOCKWISE)
                        elif self.rotate == 180:
                            cvImage = cv2.rotate(cvImage, cv2.ROTATE_180)
                        elif self.rotate == 270:
                            cvImage = cv2.rotate(cvImage, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    else:
                        self.rotateIs = False
                        self.rotateOff.setChecked(True)
            if self.addlogoIs:
                logoImg = cv2.imread(self.logoPath, -1)
                dst = cvImage.copy()

                # y_offset = int(cvImage.shape[0] * self.addlogoY / 100)
                # x_offset = int(cvImage.shape[1] * self.addlogoX / 100)

                y_offset = int((cvImage.shape[0] - logoImg.shape[0]) * self.addlogoY / 100)
                x_offset = int((cvImage.shape[1] - logoImg.shape[1]) * self.addlogoX / 100)

                y1, y2 = y_offset, y_offset + logoImg.shape[0]
                x1, x2 = x_offset, x_offset + logoImg.shape[1]

                alpha_s_logo = logoImg[:, :, 3] / 255.0
                alpha_l_logo = 1.0 - alpha_s_logo

                if self.grayscaleIs:
                    for c in range(0, 3):
                        dst[y1:y2, x1:x2] = (alpha_s_logo * logoImg[:, :, c] + alpha_l_logo * dst[y1:y2, x1:x2])
                else:
                    for c in range(0, 3):
                        dst[y1:y2, x1:x2, c] = (alpha_s_logo * logoImg[:, :, c] + alpha_l_logo * dst[y1:y2, x1:x2, c])

                cvImage = dst
            if self.borderIs:
                if self.border == 'VGA':
                    re_width, re_height = res['CIF']
                    width, height = res['VGA']
                elif self.border == 'CIF':
                    re_width, re_height = res['qCIF']
                    width, height = res['CIF']

                temp = cv2.resize(cvImage, dsize=(re_width, re_height))
                x = int((width - re_width) / 2)
                y = int((height - re_height) / 2)
                temp = cv2.copyMakeBorder(temp, y, y, x, x, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                cvImage = temp

            if self.grayscaleIs:
                qImg = QtGui.QImage(cvImage.data, cvImage.shape[1], cvImage.shape[0], cvImage.strides[0], QtGui.QImage.Format_Grayscale8)
            else:
                qImg = QtGui.QImage(cvImage.data, cvImage.shape[1], cvImage.shape[0], cvImage.strides[0], QtGui.QImage.Format_RGB888)

            self.changeImage(qImg)

    def saveVideo(self):
        # self.printCurrentTransform()
        saveDirPath = QFileDialog.getExistingDirectory()

        if self.videoPath:
            tempSaveDirPath = "./videos"
            filepath = self.videoPath
            base = os.path.basename(filepath)
            savePath = saveDirPath + '/' + self.videoName
            meta_data = video_info(filepath)

            count = 1

            if self.brightnessIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])

                brightness(filepath, path, level=self.brightness)

                filepath = path
                count += 1
            if self.cropIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                crop(filepath, path, *meta_data, level=self.crop)

                filepath = path
                count += 1
            if self.flipIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                flip(filepath, path, *meta_data, level=self.flip)

                filepath = path
                count += 1
            if self.formatIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                format(filepath, path, *meta_data, level=self.format)

                filepath = path
                count += 1
            if self.framerateIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                framerate(filepath, path, *meta_data, level=self.framerate)

                filepath = path
                count += 1
            if self.grayscaleIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                grayscale(filepath, path, *meta_data, level='Light')

                filepath = path
                count += 1
            if self.resolutionIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                resolution(filepath, path, *meta_data, level=self.resolution)

                filepath = path
                count += 1
            if self.rotateIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                rotate(filepath, path, *meta_data, level=self.rotate)

                filepath = path
                count += 1
            if self.addlogoIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                add_logo(filepath, path, *meta_data, self.addlogoX / 100, self.addlogoY / 100, level=self.addlogoLevel)

                filepath = path
                count += 1
            if self.borderIs:
                path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
                add_border(filepath, path, *meta_data, level=self.border)

                filepath = path
                count += 1

            finalBase = base
            temp = saveDirPath + "/" + finalBase
            base = base.split('.')[0] + "_" + str(count - 1) + "." + base.split('.')[1]
            finalVideoPath = os.path.join(tempSaveDirPath, base)
            shutil.copyfile(finalVideoPath, temp)

    def border_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.border = radioBtn.text()
            # print("self.border :", self.border)
            if self.border is None or self.border == 'off':
                self.borderIs = False
                self.preview()
            else:
                self.borderIs = True
                self.preview()

    def brightness_change(self):
        self.brightness = int(self.brightnessBox.currentText())

        if self.brightness == 'off' or self.brightness == 0:
            self.brightnessIs = False
        else:
            self.brightnessIs = True
            self.brightness = int(self.brightness)

        self.preview()

    def crop_change(self):
        self.crop = self.cropSlider.value() / 1000 * 5 # 0.5 까지 조절 가능하도록
        if self.crop == 0:
            self.cropIs = False
        else:
            self.cropIs = True

        self.preview()

    def flip_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.flip = radioBtn.text()
            if self.flip is None or self.flip == 'off':
                self.flipIs = False
                self.preview()
            else:
                self.flipIs = True
                if self.flip == "ver":
                    self.flip = "vflip"
                elif self.flip == "hor":
                    self.flip = "hflip"
                self.preview()

    def format_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.format = radioBtn.text()
            if self.format is None or self.format == 'off':
                self.formatIs = False
                self.preview()
            else:
                self.formatIs = True
                self.preview()

    def framerate_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.framerate = radioBtn.text()
            if self.framerate is None or self.framerate == 'off':
                self.framerateIs = False
            else:
                self.framerateIs = True
                self.framerate = int(self.framerate)
            self.preview()

    def grayscale_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.grayscale = radioBtn.text()
            if self.grayscale is None or self.grayscale == 'off':
                self.grayscaleIs = False
            else:
                self.grayscaleIs = True
                self.grayscale = "Light"
            self.preview()

    def addlogoX_change(self):
        self.addlogoX = self.addlogoXslider.value()

        self.preview()

    def addlogoY_change(self):
        self.addlogoY = self.addlogoYslider.value()

        self.preview()

    def addlogoLevel_change(self):
        self.addlogoLevel = self.logoLevelBox.currentText()

        if self.addlogoLevel == 'off':
            self.addlogoIs = False
        else:
            self.addlogoIs = True
            self.logoPath = random.choice(glob.glob(os.path.join('.\\', 'logo', self.addlogoLevel, '*')))
        self.preview()

    def resolution_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.resolution = radioBtn.text()
            if self.resolution is None or self.resolution == 'off':
                self.resolutionIs = False
                self.preview()
            else:
                self.resolutionIs = True
                self.preview()

    def rotate_change(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.rotate = radioBtn.text()
            if self.rotate is None or self.rotate == 'off':
                self.rotateIs = False
                self.preview()
            else:
                self.rotateIs = True
                self.rotate = int(self.rotate)
                self.preview()

    def jsonSave(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Option File", ".", "Json files (*.json)")

        try:
            data = OrderedDict()
            transformData = []

            if self.brightnessIs:
                transform = "brightness"
                level = self.brightness
                transformData.append({"transform": transform,
                                      "level": level})
            if self.cropIs:
                transform = "crop"
                level = self.crop
                transformData.append({"transform": transform,
                                      "level": level})
            if self.flipIs:
                transform = "flip"
                level = self.flip
                transformData.append({"transform": transform,
                                      "level": level})
            if self.framerateIs:
                transform = "framerate"
                level = self.framerate
                transformData.append({"transform": transform,
                                      "level": level})
            if self.grayscaleIs:
                transform = "grayscale"
                level = "Light"
                transformData.append({"transform": transform,
                                      "level": level})
            if self.resolutionIs:
                transform = "resolution"
                level = self.resolution
                transformData.append({"transform": transform,
                                      "level": level})
            if self.rotateIs:
                transform = "rotate"
                level = self.rotate
                transformData.append({"transform": transform,
                                      "level": level})
            if self.addlogoIs:
                transform = "addlogo"
                level = self.addlogoLevel
                location_x = str(self.addlogoX) + "%"
                location_y = str(self.addlogoY) + "%"
                transformData.append({"transform": transform,
                                      "level": level,
                                      "location_x": location_x,
                                      "location_y": location_y})
            if self.borderIs:
                transform = "border"
                level = self.border
                transformData.append({"transform": transform,
                                      "level": level})
            if self.formatIs:
                transform = "format"
                level = self.format
                transformData.append({"transform": transform,
                                      "level": level})

            data["transforms"] = transformData

            with open(filepath, 'w', encoding='utf-8') as make_file:
                json.dump(data, make_file, indent="\t")
        except:
            print("error")

    def jsonLoad(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Option File", ".", "Json files (*.json)")

        try:
            self.transformClear()

            with open(filepath, 'r') as f:
                json_data = json.load(f)
            transforms = json_data['transforms']

            for t in transforms:
                transform = t['transform']
                level = t['level']

                if transform == 'border': # 1
                    self.borderIs = True
                    self.border = level
                    self.borderSlider.setValue(level)
                elif transform == 'brightness': # 3
                    self.brightnessIs = True
                    self.brightness = level
                    length = len(self.brightnessBox)

                    for i in range(0, length):
                        if self.brightness == int(self.brightnessBox.itemText(i)):
                            self.brightnessBox.setCurrentIndex(i)
                elif transform == 'crop': # 3
                    self.cropIs = True
                    self.crop = level * 1000

                    self.cropSlider.setValue(self.crop)
                elif transform == 'flip': # 1
                    self.flipIs = True
                    self.flip = level

                    if self.flip == 'vflip':
                        self.flipRadioVer.setChecked(True)
                    elif self.flip == 'hflip':
                        self.flipRadioHor.setChecked(True)
                    else:
                        self.flipRadioOff.setChecked(True)
                elif transform == 'format': # 1
                    self.formatIs = True
                    self.format = level

                    if self.format == '.mp4':
                        self.formatMp4.setChecked(True)
                    elif self.format == '.avi':
                        self.formatAvi.setChecked(True)
                elif transform == 'framerate': # 3
                    self.framerateIs = True
                    self.framerate = level

                    if self.framerate == 5:
                        self.framerate5.setChecked(True)
                    elif self.framerate == 10:
                        self.framerate10.setChecked(True)
                    elif self.framerate == 20:
                        self.framerate20.setChecked(True)
                elif transform == 'grayscale':
                    self.grayscaleIs = True
                    self.grayscale = level
                    self.grayscaleOn.setChecked(True)
                elif transform == 'addlogo': # 3
                    self.addlogoIs = True
                    self.addlogoLevel = level
                    self.addlogoX = t['location_x']
                    self.addlogoY = t['location_y']

                    self.addlogoX = int(self.addlogoX.replace('%', ''))
                    self.addlogoY = int(self.addlogoY.replace('%', ''))

                    length = len(self.logoLevelBox)

                    for i in range(0, length):
                        if self.addlogoLevel == self.logoLevelBox.itemText(i):
                            self.logoLevelBox.setCurrentIndex(i)

                    self.addlogoXslider.setValue(self.addlogoX)
                    self.addlogoYslider.setValue(self.addlogoY)
                elif transform == 'resolution': # 2
                    self.resolutionIs = True
                    self.resolution = level

                    if self.resolution == 'CIF':
                        self.resolutionCIF.setChecked(True)
                    elif self.resolution == 'QCIF':
                        self.resolutionQCIF.setChecked(True)
                elif transform == 'rotate': # 1
                    self.rotateIs = True
                    self.rotate = level

                    if self.rotate == 90:
                        self.rotate90.setChecked(True)
                    elif self.rotate == 180:
                        self.rotate180.setChecked(True)
                    elif self.rotate == 270:
                        self.rotate270.setChecked(True)


        except:
            print("error")

    def transformClear(self):
        self.borderSlider.setValue(0)
        self.brightnessBox.setCurrentIndex(3)
        self.cropSlider.setValue(0)

        self.flipRadioOff.setChecked(True)
        self.flipRadioVer.setChecked(False)
        self.flipRadioHor.setChecked(False)

        self.formatOff.setChecked(True)
        self.formatMp4.setChecked(False)
        self.formatAvi.setChecked(False)

        self.framerateOff.setChecked(True)
        self.framerate5.setChecked(False)
        self.framerate10.setChecked(False)
        self.framerate20.setChecked(False)

        self.grayscaleOff.setChecked(True)
        self.grayscaleOn.setChecked(False)

        self.logoLevelBox.setCurrentIndex(0)
        self.addlogoXslider.setValue(0)
        self.addlogoYslider.setValue(0)
        self.resolutionOff.setChecked(True)
        self.resolutionCIF.setChecked(False)
        self.resolutionQCIF.setChecked(False)
        self.rotateOff.setChecked(True)
        self.rotate90.setChecked(False)
        self.rotate180.setChecked(False)
        self.rotate270.setChecked(False)

    def printCurrentTransform(self):
        print("==========================")
        print(f'border : {self.borderIs} / {self.border}')

        print(f'brightness : {self.brightnessIs} / {self.brightness}')

        print(f'crop : {self.cropIs} / {self.crop}')

        print(f'flip : {self.flipIs} / {self.flip}')

        print(f'format : {self.formatIs} / {self.format}')

        print(f'framerate : {self.framerateIs} / {self.framerate}')

        print(f'grayscale : {self.grayscaleIs} / {self.grayscale}')

        print(f'addlogoLevel : {self.addlogoIs} / {self.addlogoLevel}')
        print("logo x :", self.addlogoX)
        print("logo y :", self.addlogoY)

        print(f'resolution : {self.resolutionIs} / {self.resolution}')

        print(f'rotate : {self.rotateIs} / {self.rotate}')
        print("==========================")


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


def load_binary_image(image_path) :
    b_image = open(image_path, 'rb')
    return b_image


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TagWindow()
    window.show()
    app.exec_()