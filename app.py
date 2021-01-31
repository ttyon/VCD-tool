import sys, os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.uic.properties import QtCore

import videoview
from PyQt5.QtCore import Qt, QUrl, QThread
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# 여러가지 라이브러리
import datetime, random

# json 파일 출력 라이브러리 사용
import json
from collections import OrderedDict

# 영상들 프레임 추출하기 위해 opencv 사용할 것.
import cv2
from natsort import natsorted, ns

from tagWindow import *

form_class = uic.loadUiType("design.ui")[0]
DEFAULT_EVENT = ["assault", "pedestrian_abnormal_behavior_fall", "wanderer", "kidnapping", "risk_factors", "reid_objecttracking"]


class MyWindow(QMainWindow, form_class):
    # def __init__(self, parent=None):
    #     super(MyWindow, self).__init__(parent)
    #     self.ui = form_class
    #     self.ui.setupUi(self)
    def __init__(self):
        super().__init__()

        # 자른 video들 관리하는 객체 videoAdmin
        self.videoAdmin = VideoAdmin()

        # Qdialog로 프레임 저장된 디렉토리
        self.save_photo_dir = ""

        self.setGeometry(500, 100, 2500, 600)  # 원래 1400 -> 700, 1000 -> 500, 전체 크기 설정 이걸로 하셈

        self.setupUi(self)
        self.startText.setText("0:00:00")
        self.endText.setText("0:00:00")
        self.startFrameText.setText("0")
        self.endFrameText.setText("0")

        # eventList 기능
        self.eventAdd.clicked.connect(self.addListWidget)
        self.eventName.returnPressed.connect(self.addListWidget)
        self.eventSubtract.clicked.connect(self.deleteEvent)
        self.eventList.doubleClicked.connect(self.saveEvent)  # 더블클릭하면 이벤트 선택 색상 변경

        # videoList 기능
        self.videoAdd.clicked.connect(self.load_files)
        self.videoSubtract.clicked.connect(self.deleteFile)
        self.videoList.doubleClicked.connect(self.videoPlay)

        # cutList 기능
        self.cutRefresh.clicked.connect(self.refreshCutList)
        # 추가할 것 : cutList에서 목록 바꾸는 거
        self.vidUp.clicked.connect(self.videoUpList)
        self.vidDown.clicked.connect(self.videoDownList)

        # video cut 기능
        self.startBtn.clicked.connect(self.inputStart)
        self.endBtn.clicked.connect(self.inputEnd)
        self.cutBtn.clicked.connect(self.cutVideo)

        # object tag 기능
        self.tagBtn.clicked.connect(self.newTaggingPage)

        # random, video, json 출력 기능
        self.randomBtn.clicked.connect(self.randomFunction)
        self.videoBtn.clicked.connect(self.videoCreate)
        self.jsonBtn.clicked.connect(self.jsonCreate)

        self.worker = Worker(parent=self)

        for event in DEFAULT_EVENT:
            self.eventList.addItem(str(event))
        # 이거 실행할 코드에 넣기 self.worker.start()

    def newTaggingPage(self):

        # 프레임 추출한 거 어디에 저장할래?
        self.save_photo_dir = QFileDialog.getExistingDirectory()
        try:
            print("dir : " + self.save_photo_dir)
            filename = self.videoAdmin.selectedVideo
            print("filename: " + filename)
            if len(filename) > 0:
                cap = cv2.VideoCapture(filename)
                # 현재 재생되고 있는 영상의 정보
                # length: 프레임 단위 동영상 길이
                # width: 동여상상
                length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)

                print("length: ", str(length))
                print("width: " + str(width))
                print("height: " + str(height))
                print("fps: ", str(fps))

                frame_start = int(self.startFrameText.text())
                frame_end = int(self.endFrameText.text())
                print("frame_start : ", frame_start)
                print("frame_end : ", frame_end)

                ########## opencv 이용해 영상에서 프레임 추출

                print("opencv2써서 프레임 추출해봐")
                count = 0;
                print("123")

                while True:
                    ret, frame = cap.read()
                    if count > frame_end:
                        break;
                    if ret:
                        if frame_start <= count <= frame_end:
                            # print("안되네",count)
                            print(self.save_photo_dir+"/"+self.videoAdmin.selectedVideo.split("/")[-1].split(".")[0]+"_"+str(count)+".jpg")
                            cv2.imwrite(self.save_photo_dir+"/"+self.videoAdmin.selectedVideo.split("/")[-1].split(".")[0]+"_"+str(count)+".jpg", frame)
                    else:
                        break
                    count += 1

            ########## opencv 이용해 영상에서 프레임 추출

            photonames = os.listdir(self.save_photo_dir)
            print("photonames: ",photonames)
            # for photo in photonames:
            #     temp = "1: "+photo
            #     self.cutList.addItem(temp)

            self.videoAdmin.photos_to_tag = os.listdir(self.save_photo_dir)
            print(self.videoAdmin.photos_to_tag)
            self.videoAdmin.photos_to_tag = natsorted(self.videoAdmin.photos_to_tag, alg=ns.IGNORECASE)
            print(self.videoAdmin.photos_to_tag)

            child = TagWindow(self)
            # setFocusPolicy 를 해서 keyboard이벤트를 이 녀석한테 맞추기
            child.setFocusPolicy(Qt.StrongFocus)
        except:  # 예외가 실행됐을 때, 이 기능에서는 대부분 filedialog 닫았을 때 발생한다.
            print("filedialog 닫은 오류")
            print("오류")

    # 버튼 누르면 event 항목 추가
    def addListWidget(self):
        inputEvent = self.eventName.text()

        if len(inputEvent) != 0:
            print("이벤트 추가")
            print("inputName : " + inputEvent)
            self.eventList.addItem(self.eventName.text())
            self.eventName.clear()
            self.eventName.repaint()
        else:
            print("Not add")

    # 이벤트 삭제
    def deleteEvent(self):
        print("이벤트 삭제")
        print("삭제하는 이벤트 : " + str(self.eventList.currentItem().text()))
        print("선택된 이벤트 : " + str(self.videoAdmin.selectedEvent))
        # 삭제하는 이벤트
        delete_event_name = str(self.eventList.currentItem().text())
        # 선택된 이벤트
        selected_event_name = str(self.videoAdmin.selectedEvent)

        if delete_event_name == selected_event_name:
            print("선택한 이벤트 초기화한당")
            self.videoAdmin.selectedEvent = ""

        row = self.eventList.currentRow()
        # print(row)
        self.eventList.takeItem(row)

    # cutting할 영상의 이벤트를 선택한다.
    # 이벤트 클릭하면 색상 바뀌는 거 해야할 듯
    def saveEvent(self):
        count = self.eventList.count()
        row = self.eventList.currentRow()

        print(count)
        for i in range(count):
            self.eventList.item(i).setBackground(QColor('#ffffff'))

        item = self.eventList.currentItem()
        item.setBackground(QColor('#ff0000'))
        self.videoAdmin.setEvent(item)
        self.eventList.item(row).setSelected(False)
        self.eventList.repaint()

    # videoList 기능
    # 파일 불러오기
    def load_files(self):
        print("파일 불러오기")

        filename = QFileDialog.getOpenFileNames(self, "Open Video")

        for filename in filename[0]:
            self.videoList.addItem(filename)
        # fname = QFileDialog.getOpenFileName(self)
        # if len(fname[0]) > 0:
        #     self.videoList.addItem(fname[0])

    # 파일 삭제하기
    def deleteFile(self):
        print("파일 삭제하기")
        row = self.videoList.currentRow()
        # print(row)
        self.videoList.takeItem(row)

    def videoPlay(self):

        filename = self.videoList.currentItem().text()
        cap = cv2.VideoCapture(filename)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fps = cap.get(cv2.CAP_PROP_FPS)

        video_time = str(datetime.timedelta(seconds=round(length / fps)))
        print("어디가 문제니3")

        print('length : ', length)
        print('width : ', width)
        print('height : ', height)
        print('fps : ', fps)
        print('video time : ', video_time)
        print("어디가 문제니4")
        if filename != '':
            self.videoView.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.videoView.playBtn.setEnabled(True)
            self.videoAdmin.setVideo(filename)


    # cutList기능
    # cutlist 다 삭제하기
    def refreshCutList(self):
        self.cutList.clear()

        print("cutlist 다 삭제")
        self.videoAdmin.refreshList()

    # cutList 목록 바꾸기
    def videoUpList(self):
        row = self.cutList.currentRow()
        print(row)

        if row > 0:
            self.videoAdmin.cutList[row - 1], self.videoAdmin.cutList[row] = self.videoAdmin.cutList[row], \
                                                                             self.videoAdmin.cutList[row - 1]

            self.cutList.clear()
            cutList = self.videoAdmin.cutList

            for new in cutList:
                temp = "[" + str(new.index) + "]" + new.event + "_" + new.filename.split('/')[-1]
                self.cutList.addItem(temp)

            self.cutList.item(row - 1).setSelected(True)
            self.cutList.setCurrentRow(row - 1)

    # cutList 목록 순서 바꾸기
    def videoDownList(self):
        row = self.cutList.currentRow()
        print(row)

        if row < len(self.videoAdmin.cutList) - 1:
            self.videoAdmin.cutList[row + 1], self.videoAdmin.cutList[row] = self.videoAdmin.cutList[row], \
                                                                             self.videoAdmin.cutList[row + 1]

            self.cutList.clear()
            cutList = self.videoAdmin.cutList

            for new in cutList:
                temp = "[" + str(new.index) + "]" + new.event + "_" + new.filename.split('/')[-1]
                self.cutList.addItem(temp)

            self.cutList.item(row + 1).setSelected(True)
            self.cutList.setCurrentRow(row + 1)

    # video cut 기능
    def inputStart(self):
        print("inputStart")

        time = self.videoView.mediaPlayer.position() / 1000
        frame = str(int(time * 29.97))
        time = str(datetime.timedelta(seconds=round(time)))

        self.startText.setText(time)
        self.startFrameText.setText(frame)
        self.startText.repaint()
        self.startFrameText.repaint()

    def inputEnd(self):
        print("inputEnd")
        6
        time = self.videoView.mediaPlayer.position() / 1000
        frame = str(int(time * 29.97))
        time = str(datetime.timedelta(seconds=round(time)))

        self.endText.setText(time)
        self.endFrameText.setText(frame)
        self.startText.repaint()
        self.endFrameText.repaint()

    def cutVideo(self):
        print("cutting")
        startTimeString = self.startText.text()
        endTimeString = self.endText.text()

        startDateTime = datetime.datetime.strptime(startTimeString, "%H:%M:%S")
        endDateTime = datetime.datetime.strptime(endTimeString, "%H:%M:%S")

        # print(startDateTime)
        # print(endDateTime)

        startSecond = (startDateTime - datetime.datetime(1900, 1, 1)).total_seconds()
        endSecond = (endDateTime - datetime.datetime(1900, 1, 1)).total_seconds()

        print(endSecond - startSecond)
        videoLen = endSecond - startSecond

        if videoLen > 0 and len(self.videoAdmin.selectedEvent) > 0 and len(self.videoAdmin.selectedVideo) > 0:
            # 영상 길이가 0초 초과여야  컷리스트에 넣을 것
            print("cutList에 추가")
            videoName = self.videoAdmin.selectedVideo
            eventName = self.videoAdmin.selectedEvent
            print(videoName)
            print(eventName)
            self.cutList.addItem(self.videoAdmin.addCutList(videoLen, startSecond, endSecond))

    # 마지막 기능
    def randomFunction(self):
        self.cutList.clear()
        cutList = self.videoAdmin.randomList()

        for new in cutList:
            temp = "[" + str(new.index) + "]" + new.event + "_" + new.filename.split('/')[-1]
            self.cutList.addItem(temp)

        print("random")

    def videoCreate(self):
        print("video")
        self.worker.start()
        # 나중에 이거 fileNum 올라가는 거 video 생성 한 번, json 생성 한 번 하고 나서 올라가게 바꿔야 함
        # 지금은 video 생성할 때 json도 같이 생성하는 걸로 바꿈
        # self.videoAdmin.fileNum += 1

    def jsonCreate(self):
        # self.videoAdmin.jsonFile()
        self.videoAdmin.jsonFile()
        # print("video 생성을 하면 json 파일도 같이 생성 됩니다.")
        # print("json")


class VideoAdmin:
    def __init__(self):
        self.selectedVideo = ""
        self.selectedEvent = ""
        self.cutList = []
        # cutList에 넣는 index
        self.index = 1
        # 프로그램 꺼지면 주의하셈 나중에 json 파일 load 기능 생기면 여기도 처리해야함
        # fileNum은 json파일과 video를 둘 다 내보냈으면 증가하는 형식으로 바꿀 것.
        self.fileNum = 1  # 프로그램 꺼지면 주의하셈 나중에 json 파일 load 기능 생기면 여기도 처리해야함
        self.photos_to_tag = []

        # photo 저장할 거 ..

    def setEvent(self, item):
        self.selectedEvent = item.text()
        print("setEvent : " + self.selectedEvent)

    def setVideo(self, vidName):
        self.selectedVideo = vidName
        print(self.selectedVideo)

    def addCutList(self, videoLen, startSecond, endSecond):
        print("cutlist에 추가 1")
        start_time = "0" + str(datetime.timedelta(seconds=round(startSecond)))
        end_time = "0" + str(datetime.timedelta(seconds=round(endSecond)))
        video = CutVideo(self.index, self.selectedEvent, self.selectedVideo, videoLen, start_time, end_time)
        print(self.selectedEvent)
        print("cutlist에 추가 1")
        print(self.selectedVideo)
        print("cutlist에 추가 2")
        print(self.selectedVideo.split('/')[-1])
        self.cutList.append(video)
        print("videoadmin의 cutList : " + str(self.cutList[-1].videoLen))
        print("cutlist에 추가 3")
        # videoname = videoname.split('/')[len(videoname.split('/'))]
        # print("cutlist에 추가 4")

        cutname = "[" + str(self.index) + "]" + self.selectedEvent + "_" + self.selectedVideo.split('/')[-1]
        # print("cutlist에 추가 5")
        print(cutname)
        self.index += 1
        return cutname
        # print("cutlist에 추가 6")

    def randomList(self):
        random.shuffle(self.cutList)
        return self.cutList

    def refreshList(self):
        del self.cutList[:]
        self.index = 1

    # json 파일을 내보낼 때 time으로 작성해서 내보내는 거
    # def jsonFileByTime(self):
    #     videoFullTime = 0
    #     currentTime = 0
    #
    #     file_path = "./" + str(self.fileNum) + "_360p.json"
    #     print("file_path : " + file_path)
    #
    #     # str(datetime.timedelta(seconds=round(time)))
    #
    #     for vid in self.cutList:
    #         videoFullTime += vid.videoLen
    #
    #     frameNum = videoFullTime * 29.97
    #
    #     videoFullTime = datetime.timedelta(seconds=round(videoFullTime))
    #
    #     data = OrderedDict()
    #     eventData = OrderedDict()
    #
    #     data["video_name"] = str(self.fileNum) + "_360p"
    #
    #     data["length"] = "0" + str(videoFullTime)
    #     data["frame_num"] = str(int(frameNum))
    #     eventData = []
    #
    #     # data["event"][0] = vid
    #
    #     for vid in self.cutList:
    #         # 원래 파일이름, 이벤트 이름, 시작 시간, 종료 시간
    #         temp_time = currentTime + vid.videoLen
    #         eventData.append({"event": vid.event,
    #                           "start_time": "0" + str(datetime.timedelta(seconds=round(currentTime))),
    #                           "end_time": "0" + str(datetime.timedelta(seconds=round(temp_time))),
    #                           "origin_file_name": vid.filename.split('/')[-1]})
    #         currentTime += vid.videoLen
    #
    #     data["event"] = eventData
    #
    #     st_json = json.dumps(data, indent=4)
    #     print(st_json)
    #
    #     with open('./annotations/' + str(self.fileNum) + '_360p.json', 'w', encoding='utf-8') as make_file:
    #         json.dump(data, make_file, indent="\t")
    #
    #     # self.fileNum += 1
    #
    #     # json 파일이랑 video 파일이랑 내보냈으면 증가시킬 것 이거를

    # frame 단위로 내보내는 거
    def jsonFile(self):
        filePath, _ = QFileDialog.getSaveFileName()

        if not ".json" in filePath:
            filePath = filePath + ".json"

        print("filePath : " + filePath)
        try:
            videoFullTime = 0
            currentTime = 0

            for vid in self.cutList:
                videoFullTime += vid.videoLen

            frameNum = videoFullTime * 29.97

            videoFullTime = datetime.timedelta(seconds=round(videoFullTime))

            data = OrderedDict()

            data["video_name"] = filePath.split("/")[-1].split(".")[0] + "_360p"

            data["length"] = "0" + str(videoFullTime)
            data["frame_num"] = str(int(frameNum))
            eventData = []

            for vid in self.cutList:
                # 원래 파일이름, 이벤트 이름, 시작 시간, 종료 시간
                temp_time = currentTime + vid.videoLen
                print("temp_time: " + str(temp_time))
                current_frame = int(currentTime * 29.97) + 1
                temp_frame = int(temp_time * 29.97)
                eventData.append({"event": vid.event,
                                  "start_time": "0" + str(datetime.timedelta(seconds=round(currentTime))),
                                  "end_time": "0" + str(datetime.timedelta(seconds=round(temp_time))),
                                  "start_frame": str(current_frame),
                                  "end_frame": str(temp_frame),
                                  "origin_file_name": vid.filename.split('/')[-1]})
                currentTime += vid.videoLen

            data["event"] = eventData

            st_json = json.dumps(data, indent=4)

            with open(filePath, 'w', encoding='utf-8') as make_file:
                json.dump(data, make_file, indent="\t")

            print("json success")
        except:
            print("json failed /")


class CutVideo:
    def __init__(self, index, event, filename, videoLen, start_time, end_time):
        self.index = index
        self.event = event
        self.filename = filename
        self.videoLen = videoLen
        self.start_time = start_time
        self.end_time = end_time


# 쓰레드 관리 클래스 쓰레드 안에서 영상 자르고 자른 영상들 txt파일로 만들고 concat 한다.
class Worker(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.main = parent

    def __del__(self):
        print(".... end thread.....")
        del self
        # self.wait()


    # 여기서 영상 자르고 만드는 기능 구현
    def run(self):
        # 영상 자르기
        print("영상 자를거야")

        filePath, _ = QFileDialog.getSaveFileName()

        if not ".mp4" in filePath:
            filePath = filePath + ".mp4"

        print("test path : ", filePath.split("/"))
        fileName = filePath.split('/')[-1]
        dirArr = filePath.split("/")[0:len(filePath.split("/"))-1]
        dirPath = ""

        for temp in dirArr:
            dirPath = dirPath + temp
            dirPath = dirPath + "/"

        print("filePath : " + filePath)
        print("dirPath : ", dirPath)
        print("fileName : ", fileName)

        # 영상 자르기
        idx = 0
        for video in self.main.videoAdmin.cutList:
            # print(str(idx) + "번째 영상 ")
            # print("자를 영상 시작 시간 : " + video.start_time)
            # print("자를 영상 끝날 시간 : " + video.end_time)

            command = "ffmpeg -i " + video.filename + " -ss " + video.start_time + " -to " + video.end_time + " "+ dirPath + "trash_" + str(idx) + "_" + video.filename.split('/')[-1]
            # command = "ffmpeg -i " + video.filename + " -ss " + video.start_time + " -to " + video.end_time + " " + filePath
            print(command)
            os.system(command)
            idx += 1

        # 자른 영상들의 fps를 29.97로 바꾼다.
        videonames = os.listdir(dirPath)
        print(videonames)

        for video in videonames:
            if 'trash' in video:
                print(video)
                command = "ffmpeg -i " + dirPath + video + " -r 29.97 -y " + dirPath + "29.97_" + video
                os.system(command)
                print("흐음 : ", filePath+video)
                os.remove(dirPath + video)
                print(command)


        # # 자른 영상들 txt 파일로 저장하기
        videonames = os.listdir(dirPath)
        print(videonames)

        f = open(dirPath+'videotext.txt', mode='wt', encoding='utf-8')
        for video in videonames:
            if '29.97_' in video:
                print(video)
                data = "file " + dirPath + video + "\n"
                print("txt data : " + data)
                f.write(data)
        f.close()

        # 자른 영상들 merge하기
        command = "ffmpeg -f concat -safe 0 -i "+dirPath+"videotext.txt -c copy " + filePath
        print(command)
        os.system(command)

        # 영상들 만들고 후처리
        # 이어 붙이고 잘라진 영상들 다 삭제하고 txt 파일 삭제해야함
        for video in videonames:
            if 'trash' in video:
                os.remove(dirPath + video)

        os.remove(dirPath+'videotext.txt')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()

    ######## event name #########
    # assault
    # pedestrian_abnormal_behavior_fall
    # wanderer
    # kidnapping
    # risk_factors
    # reid_objecttracking