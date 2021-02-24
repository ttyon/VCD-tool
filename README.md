# 비디오 변형 옵션파일 생성 및 변형 제작도구 설치 및 실행
- 10가지 변형에 대해 json option file 생성 및 로드
- tool 내부에서 변형된 영상 썸네일 간략히 출력
- command line을 통한 하나의 디렉토리 안의 동영상들 변형 기능

## 프로그램 요구사항
### 요구사항
* Window
* FFMPEG 4.3.1
* Python 3.6
* Anaconda3 
### Requirements
- requirements.txt 참조 

## 프로그램 설치 및 실행 방법
### 프로그램 다운로드
```
cd [프로그램 다운 받을 디렉토리 경로]          ex) cd C:/Users/jslee/Desktop
git clone https://github.com/ttyon/VCD-tool.git
```

### conda 가상 환경 구성
```
conda create -n [VideoTransform] python=3.6 -y (가상 환경 이름은 사용자 마음대로)
conda activate [VideoTransform]
cd [프로그램 경로]                           ex) cd C:/Users/jslee/Desktop/VCD-tool
pip install -r requirements.txt
```
 
### 프로그램 실행 방법
```
cd [프로그램 경로]                           ex) cd C:/Users/jslee/Desktop/VCD-tool
conda activate [VideoTransform]
python app.py
```

## How to use
### 변형 option file 생성

<img width="926" alt="KakaoTalk_20200923_174424241" src="https://user-images.githubusercontent.com/46225226/108618700-8f518200-7463-11eb-943a-18dfea4e5bf6.png">

#### 1. 변형의 예시를 보기 위해 'Open Video'를 통해 비디오를 선택

#### 2. 변형이 된  동영상 예시 섬네일 출력

#### 3. 원본 동영상 파일의 정보 출력

#### 4. 10가지 변형에 대하여 level 사용자화 가능

```
10가지 변형의 level

border
CIF : 캡쳐 후 CIF급 저장(352, 288)
VGA : 캡쳐 후 VGA급 저장(640, 480)

brightness
-36, -18, -9, +9, +18, +36 밝기 조절

crop
영상의 0 ~ 0.5 자르기 조절

flip
ver : 상하 반전
hor : 좌우 반전

format
.mp4 : mp4 영상으로 변환
.avi : avit 영상으로 변환

framerate
영상의 framerate를 5, 10, 20으로 조절

gray scale
(0.299, 0.587, 0.114) 흑백 변환

add logo
logo의 크기는 Light, Medium, Heavy
x, y축 바를 조절하여 로고의 위치 변환 가능

resolution
CIF : 영상의 해상도를 CIF로 변환 (352, 288)
QCIF : 영상의 해상도를 QCIF로 변환 (176, 144)

rotate
90 : 시계 방향으로 90도 영상 변환
180 : 시계 방향으로 180도 영상 변환
270 : 시계 방향으로 270도 영상 변환   

* add logo 변환과 rotate 변환을 같이 적용시 주의할 점 *
2개의 변환을 같이 적용 시, logo의 넓이와 길이가 rotate된 영상의 넓이와 길이보다 크다면
변환이 rotate 변환이 불가능 합니다. 
```

#### 5. 
#### 'Save' : 프로그램내에서 사용자화한 option 파일을 json 파일 형식으로 저장
#### 'Load' : 이미 존재한 json option 파일을 불러와 수정 가능


### command line을 통한 하나의 디렉토리 안의 동영상들 변형

```
video 들이 저장되어 있는 디렉토리의 구성 (--video_dir_path의 형태)
(DIRECTORY)
├── aaa.flv
├── bbb.flv
├── ccc.flv
├── ddd.flv
├── eee.flv
├── fff.flv
├── ...
└── zzz.flv

usage: transform_videos.py [-h] --video_dir_path VIDEO_DIR_PATH \
                           --save_dir_path SAVE_DIR_PATH \
                           --json_file_path JSON_FILE_PATH 

ex) python transform_videos.py --video_dir_path [변형할 비디오 디렉토리 경로] --save_dir_path [변형된 비디오 저장 디렉토리 경로] --json_file_path [json option 파일 경로]
```

```
프로젝트 내의 videos 폴더에 여러 가지 변형들이 적용된 동영상들이 있습니다. 해당 videos 폴더를 삭제하지 말아주세요.
프로젝트 내의 각 변형이 적용된 영상들이 필요 없다면
python deletevideos.py 를 실행하세요.
```

 

