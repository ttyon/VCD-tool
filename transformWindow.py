import argparse
import shutil
import sys, os
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

from libs.canvas import Canvas
from libs.shape import Shape
from libs.utils import *
from libs.hashableQListWidgetItem import *
from libs.request import Request
from libs.transforms import *

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


class TagWindow(QDialog):
    def __init__(self, parent):
        # 이 클래스에서 사용될 변수들
        self.transforms = []

        # 이 클래스에서 사용될 변수들

        super(TagWindow, self).__init__(parent)
        self.resize(1500, 639)
        self.setWindowTitle('tagging')

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.transformBtn = QtWidgets.QPushButton()
        self.transformBtn.setObjectName("transformBtn")
        self.verticalLayout.addWidget(self.transformBtn)
        # self.nextBtn = QtWidgets.QPushButton()
        # self.nextBtn.setObjectName("nextBtn")
        # self.verticalLayout.addWidget(self.nextBtn)
        # self.prevBtn = QtWidgets.QPushButton()
        # self.prevBtn.setObjectName("prevBtn")
        # self.verticalLayout.addWidget(self.prevBtn)
        # self.detectBtn = QtWidgets.QPushButton()
        # self.detectBtn.setObjectName("detectBtn")
        # self.verticalLayout.addWidget(self.detectBtn)
        # self.jsonBtn = QtWidgets.QPushButton()
        # self.jsonBtn.setObjectName("jsonBtn")
        # self.verticalLayout.addWidget(self.jsonBtn)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        # 여기 이 부분에 캔버스 넣기~~~

        # self.videoView = videoview()
        # self.videoView.setMinimumSize(QtCore.QSize(500, 0))
        # self.videoView.setObjectName("videoView")
        self.canvas = Canvas()

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.gridLayout.addWidget(scroll, 0, 1, 1, 1)
        # 여기 이 부분에 캔버스 넣기~~~

        self.videoList = QtWidgets.QListWidget()
        self.videoList.setObjectName("videoList")
        self.videoList.setFixedWidth(180)
        self.gridLayout.addWidget(self.videoList, 0, 2, 1, 1)

        self.transformList = QtWidgets.QListWidget()
        self.transformList.setObjectName("transformList")
        self.transformList.setFixedWidth(180)
        self.gridLayout.addWidget(self.transformList, 0, 3, 1, 1)

        self.defaultList = QtWidgets.QListWidget()
        self.defaultList.setObjectName("defaultList")
        self.defaultList.setFixedWidth(180)
        self.gridLayout.addWidget(self.defaultList, 0, 4, 1, 1)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem5 = QtWidgets.QSpacerItem(100, 20, 100, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)

        self.videoAddBtn = QtWidgets.QPushButton()
        self.videoAddBtn.setObjectName("videoAddBtn")
        self.videoAddBtn.setFixedWidth(40)
        self.horizontalLayout.addWidget(self.videoAddBtn)

        self.videoSubBtn = QtWidgets.QPushButton()
        self.videoSubBtn.setObjectName("videoSubBtn")
        self.videoSubBtn.setFixedWidth(40)
        self.horizontalLayout.addWidget(self.videoSubBtn)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 2, 1, 1)

        # 체크박스 만들기
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setObjectName("horizontalLayout")

        spacerItem2 = QtWidgets.QSpacerItem(100, 20, 100, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout2.addItem(spacerItem2)

        self.loadBtn = QtWidgets.QPushButton()
        self.loadBtn.setObjectName("loadBtn")
        self.loadBtn.setFixedWidth(45)
        self.horizontalLayout2.addWidget(self.loadBtn)

        self.extBtn = QtWidgets.QPushButton()
        self.extBtn.setObjectName("extBtn")
        self.extBtn.setFixedWidth(45)
        self.horizontalLayout2.addWidget(self.extBtn)

        self.gridLayout.addLayout(self.horizontalLayout2, 1, 3, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.setLayout(self.gridLayout_2)

        # 함수들
        self.transformBtn.clicked.connect(self.transformVideo)
        # self.nextBtn.clicked.connect(self.showNextPhoto)
        # self.prevBtn.clicked.connect(self.showPrePhoto)
        # self.detectBtn.clicked.connect(self.detectOBJ)
        # self.jsonBtn.clicked.connect(self.jsonSave)

        # addObjBtn subObjBtn addLabel subLabel
        self.videoAddBtn.clicked.connect(self.addVideo)
        self.videoSubBtn.clicked.connect(self.subVideo)

        # self.videoList.doubleClicked.connect(self.setLabel)
        self.transformList.doubleClicked.connect(self.delTransform)
        self.defaultList.doubleClicked.connect(self.addTransform)

        self.loadBtn.clicked.connect(self.jsonUpload)
        self.extBtn.clicked.connect(self.jsonDown)

        self.transformBtn.setText("transform")
        self.videoAddBtn.setText("+")
        self.videoSubBtn.setText("-")
        self.loadBtn.setText("load")
        self.extBtn.setText("extract")

        self.setWindowTitle('tagging')
        self.show()

        # 기본 셋팅 라벨 디폴트 값 설정
        # for tempObj in DEFAULT_OBJ:
        #     item = QListWidgetItem()
        #     item.setText(tempObj)
        #     item.setBackground(generateColorByText(tempObj))
        #     self.videoList.addItem(item)

        # default transform and level setting
        for temp in DEFAULT_TRANSFORM:
            item = QListWidgetItem()
            item.setText(temp)
            self.defaultList.addItem(item)

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

                print("videopath :", videopath)
                print("savepath :", path)
                print("transform :", transform)

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
            shutil.copyfile(finalvideoPath, temp)

        for file in os.listdir(tempSaveDirPath):
            path = os.path.join(tempSaveDirPath, file)
            print("path :", path)




        ## 마지막에는 tempSaveDirPath에 저장되어 있는 애들을 saveDirPath로 옮겨야함


    def addVideo(self):
        print("addVideo")
        filename = QFileDialog.getOpenFileNames(self, "Open Video")

        for filename in filename[0]:
            self.videoList.addItem(filename)

    def subVideo(self):
        print("subVideo")
        row = self.videoList.currentRow()
        # print(row)
        self.videoList.takeItem(row)

    def addTransform(self):
        transform_name = self.defaultList.currentItem().text()
        if not "===" in transform_name and not transform_name in self.transforms:
            item = QListWidgetItem()
            item.setText(transform_name)
            self.transformList.addItem(item)
            self.transforms.append(transform_name)

    def delTransform(self):
        index = self.transformList.currentRow()
        self.transformList.takeItem(index)
        del self.transforms[index]

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

    # addLabel subLabel
    def addLabel(self):
        input = self.objText.text()

        if len(input) > 0:
            item = QListWidgetItem()
            item.setText(input)
            item.setBackground(generateColorByText(input))
            self.labelList.addItem(item)
        else:
            print("Not Add")

    def subLabel(self):
        row = self.labelList.currentRow()
        self.labelList.takeItem(row)
        self.labelList.repaint()

        
    def allShow(self):
        for shape in self.canvas.shapes:
            if shape.label is not None:
                item = self.shapesToItems[shape]
                item.setCheckState(Qt.Checked)

    def allDisapear(self):
        for shape in self.canvas.shapes:
            if shape.label is not None:
                item = self.shapesToItems[shape]
                item.setCheckState(Qt.Unchecked)

    def selectShape(self):
        for shape in self.canvas.shapes:
            shape.selected = False
            self.canvas.repaint()

        print("shape 클릭")
        item = self.photoLabels.currentItem()
        print("item : ", item)
        shape = self.itemsToShapes[item]
        shape.selected = True
        self.canvas.repaint()

    def deleteLabel(self):
        shape = self.canvas.selectedShape
        if shape.label is not None:
            item = self.shapesToItems[shape]
            # 선택된 shape의 item을 list에서 삭제합니다.
            self.photoLabels.takeItem(self.photoLabels.row(item))
            self.photoLabels.repaint()

    def lableItemChanged(self, item):
        print("변경 될 때")
        shape = self.itemsToShapes[item]
        self.canvas.setShapeVisible(shape, item.checkState() == Qt.Checked)
        print("shape의 label : ", shape.label)

    def setLabel(self):
        print("라벨을 설정합니다.")
        label = self.labelList.currentItem().text()
        shape = self.canvas.selectedShape

        # 레이블만 더블클릭 했을 때.
        if shape is None:
            return

        # 선택한 shape의 레이블이 존재하면 레이블을 수정하는 걸로하고
        if shape.label is not None:
            print("label 수정")
            shape.label = label
            shape.line_color = generateColorByText(shape.label)

            item = self.shapesToItems[shape]
            item.setBackground(generateColorByText(shape.label))
            item.setText(shape.label)

            self.photoLabels.repaint()
            self.canvas.repaint()
        # 선택한 shape의 레이블이 존재하지 않으면 내가 레이블을 새로 만들어서 넣는다.
        else:
            print("label 생성")
            shape.label = label
            shape.paintLabel = True

            shape.line_color = generateColorByText(shape.label)

            item = HashableQListWidgetItem(shape.label)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setBackground(generateColorByText(shape.label))

            self.itemsToShapes[item] = shape
            self.shapesToItems[shape] = item

            self.canvas.repaint()
            self.labelShowList()

    # shape들의 label이 새로 생성이 되었을 때
    def labelShowList(self):
        # shape의 어찌구와 label의 순서를 똑같이 생각할 것.. 아니면 버그 생긴다.
        # self.shapesToItems를 이용해 canvas들의 label이 존재한다면, list에 다시 각자 shape의 item을 list로 뿌려주기.
        for shape in self.canvas.shapes:
            if shape.label is not None:
                item = self.shapesToItems[shape]
                self.photoLabels.addItem(item)

    def jsonLoad(self):
        # json파일을 load하면서 canvas에도 shape 추가해주어야함.
        # json파일을 load하는 것은 image를 load할 때만 한다.
        # json 파일이 없으면 jsonload는 하지 않는다. 체크
        annofiles = os.listdir(self.saveLabelDir)
        jsonfile = self.currentFilePath.split("/")[-1].split(".")[0] + ".json"

        # save label dir에 json파일이
        if jsonfile in annofiles:
            if len(self.saveLabelDir) > 0:
                print("self.currentFilePath : ", self.currentFilePath)
                print("frame ano 저장 폴더 : ", self.saveLabelDir)
                currentImageName = self.currentFilePath.split("/")[-1].split(".")[0]
                file_path = self.saveLabelDir + "/" + self.currentFilePath.split("/")[-1].split(".")[0] + ".json"

                with open(file_path, "r") as json_file:
                    json_data = json.load(json_file)
                    results = json_data["results"][0]

                    for detect in results["detection_result"]:
                        shape = Shape()

                        description = detect["label"][0]["description"]
                        print("label : ", description)

                        shape.paintLabel = True
                        shape.label = description
                        shape.line_color = generateColorByText(shape.label)

                        points = detect["position"]
                        x = points["x"]
                        y = points["y"]
                        w = points["w"]
                        h = points["h"]
                        p0 = QPointF(x, y)
                        p1 = QPointF(x+w, y)
                        p2 = QPointF(x+w, y+h)
                        p3 = QPointF(x, y+h)

                        shape.points.append(p0)
                        shape.points.append(p1)
                        shape.points.append(p2)
                        shape.points.append(p3)
                        shape.close()

                        # 추가된 shape를 item으로 설정한다.
                        item = HashableQListWidgetItem(shape.label)
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                        item.setCheckState(Qt.Checked)
                        item.setBackground(generateColorByText(shape.label))

                        self.itemsToShapes[item] = shape
                        self.shapesToItems[shape] = item

                        self.canvas.shapes.append(shape)
                self.canvas.repaint()

                # json으로 읽은 shape들 어떻게 itemlist로 출력할래?
                self.labelShowList()

    def jsonSave(self):
        # canvas에 label이 지정된 모든 shape들을 json 파일로 저장한다.
        print("self.currentFilePath : ", self.currentFilePath)
        print("frame ano 저장 폴더 : ", self.saveLabelDir)
        currentImageName = self.currentFilePath.split("/")[-1].split(".")[0]
        print("currentImageName : ", currentImageName)

        # save labe dir이 지정되어야 json으로 저장가능
        if len(self.saveLabelDir) > 0:
            data = OrderedDict()
            data["image_path"] = self.saveLabelDir + "/" + self.currentFilePath.split("/")[-1]

            results = []
            detection_result = OrderedDict()
            temp_result = []

            for shape in self.canvas.shapes:
                if shape.label is not None:
                    detect = OrderedDict()
                    label = []
                    label.append({"description": shape.label,
                                  "score": 100
                                  })

                    x = int(shape.points[0].x())
                    y = int(shape.points[0].y())
                    w = int(shape.points[2].x() - shape.points[0].x())
                    h = int(shape.points[2].y() - shape.points[0].y())
                    position = OrderedDict()
                    position["x"] = x
                    position["y"] = y
                    position["w"] = w
                    position["h"] = h

                    detect["label"] = label
                    detect["position"] = position

                    temp_result.append(detect)

            detection_result["detection_result"] = temp_result
            temp_arr = []
            temp_arr.append(detection_result)
            data["results"] = temp_arr

            st_json = json.dumps(data, indent=4)
            print(st_json)

            print(self.saveLabelDir + '/' + currentImageName +'.json')
            with open(self.saveLabelDir + '/' + currentImageName +'.json', 'w', encoding='utf-8') as make_file:
                json.dump(data, make_file, indent="\t")

    def detectOBJ(self):
        try:
            # 사진 한 장으로 수정하기
            args = parse_arguments().parse_args()
            request = Request()

            result_dir = self.saveLabelDir

            image_dir = self.save_photo_dir
            image_name = self.currentFilePath.split("/")[-1]

            image_path = os.path.join(image_dir, image_name)
            result_path = os.path.join(result_dir, image_name.split(".")[0] + ".json")
            b_image = load_binary_image(image_path)

            print("INFO: module={} / image_name={}\t======\t".format(args.modules, image_name), end="")
            request.set_request_attr(url=args.url, image_path=b_image, modules=args.modules)
            response = request.send_request_message()
            print("success\t======\t", end='')

            with open(result_path, 'w') as result_file:
                json.dump(response, result_file)
            print("saved", end='')

            self.jsonLoad()
            self.canvas.repaint()


        except:
            print(" / fail")

    def selectSaveDir(self):
        self.saveLabelDir = QFileDialog.getExistingDirectory()
        if len(self.saveLabelDir) > 0:
            self.saveDir.setStyleSheet("background-color: red")

    def loadFile(self, filePath=None):
        """Load the specified file, or the last opened file if None."""
        self.resetState()
        # json으로 저장할 때
        self.currentFilePath = filePath

        filePath = filePath
        unicodeFilePath = filePath
        unicodeFilePath = os.path.abspath(unicodeFilePath)
        imageData = read(unicodeFilePath, None)
        image = QImage.fromData(imageData)
        self.canvas.loadPixmap(QPixmap.fromImage(image))
        if len(self.saveLabelDir) > 0:
            self.jsonLoad()

    def showPhoto(self):
        photo_name = self.photoList.currentItem().text()
        self.loadFile(photo_name)

    def showNextPhoto(self):
        row = self.photoList.currentRow()

        if row < len(self.photoList) - 1:
            item = self.photoList.item(row+1)
            self.loadFile(item.text())

            self.photoList.item(row + 1).setSelected(True)
            self.photoList.setCurrentRow(row + 1)

    def showPrePhoto(self):
        row = self.photoList.currentRow()

        if row > 0:
            item = self.photoList.item(row - 1)
            self.loadFile(item.text())

            self.photoList.item(row - 1).setSelected(True)
            self.photoList.setCurrentRow(row - 1)

    def keyPressEvent(self, e):
        def isPrintable(key):
            printable = [Qt.Key_Space, Qt.Key_Exclam, Qt.Key_QuoteDbl, Qt.Key_NumberSign, Qt.Key_Dollar,
                                   Qt.Key_Percent, Qt.Key_Ampersand, Qt.Key_Apostrophe, Qt.Key_ParenLeft,
                                   Qt.Key_ParenRight, Qt.Key_Asterisk, Qt.Key_Plus, Qt.Key_Comma, Qt.Key_Minus,
                                   Qt.Key_Period, Qt.Key_Slash, Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4,
                                   Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_Colon, Qt.Key_Semicolon,
                                   Qt.Key_Less, Qt.Key_Equal, Qt.Key_Greater, Qt.Key_Question, Qt.Key_At, Qt.Key_A,
                                   Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I,
                                   Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q,
                                   Qt.Key_R, Qt.Key_S, Qt.Key_T, Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y,
                                   Qt.Key_Z, Qt.Key_BracketLeft, Qt.Key_Backslash, Qt.Key_BracketRight,
                                   Qt.Key_AsciiCircum, Qt.Key_Underscore, Qt.Key_QuoteLeft, Qt.Key_BraceLeft,
                                   Qt.Key_Bar, Qt.Key_BraceRight, Qt.Key_AsciiTilde ]
            if key in printable:
                return True
            else:
                return False
        control = False
        if e.modifiers() & Qt.ControlModifier:
            print('Control')
            control = True
        if e.modifiers() & Qt.ShiftModifier:
            print('Shift')
        if e.modifiers() & Qt.AltModifier:
            print('Alt')
        if e.key() == Qt.Key_Delete:
            print('Delete')
        elif e.key() == Qt.Key_Backspace:
            print('Backspace')
        elif e.key() in [Qt.Key_Return, Qt.Key_Enter]:
            print('Enter')
        elif e.key() == Qt.Key_Escape:
            print('Escape')
        elif e.key() == Qt.Key_Right:
            print('Right')
        elif e.key() == Qt.Key_Left:
            print('Left')
        elif e.key() == Qt.Key_Up:
            print('Up')
        elif e.key() == Qt.Key_Down:
            print('Down')
        elif e.key() == Qt.Key_A:
            self.showPrePhoto()
        elif e.key() == Qt.Key_D:
            self.showNextPhoto()
        # if not control and isPrintable(e.key()):
        #     print(e.text())

    def resetState(self):
        self.photoLabels.clear()
        self.itemsToShapes.clear()
        self.shapesToItems.clear()
        self.canvas.resetState()


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