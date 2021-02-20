# 비디오 변형 옵션파일 생성 및 변형 제작도구 설치 및 실행


## 프로그램 요구사항


### 요구사항

* Ubuntu 16.04/18.04

* CUDA 9.2/10.1

* Python 3.6

* cuDNN 7.x

* GCC 4.9 이상

# Video Transform tool
- 10가지 변형에 대해 json option file 생성 및 로드
- tool 내부에서 변형된 영상 섬네일 간략히 출력
- cmd 라인을 통한 여러 동영상들 변형 기능


## Requirements
- python 3.6
- pyqt 5
- ffmpeg
- k-lite codec pack ( http://www.codecguide.com/download_kl.htm )
- requirements.txt 참조 

## How to use
### video crop and merge
<img width="926" alt="KakaoTalk_20200923_174424241" src="https://user-images.githubusercontent.com/46225226/93990911-a746ac00-fdc6-11ea-8432-c693abd204e7.png">

1. 영상에 자를 비디오 선택
2. 비디오 목록에서 삭제
3. 리스트에서 더블클릭하면 영상 재생 준비
4. 이벤트 추가 및 삭제, 삭제하려면 삭제하려는 이벤트 선택해야함
5. 자르기 전에 json에 입력할 이벤트 선택, 선택된 이벤트는 빨간색으로 변함
6. 영상 준비가 되고 누르면 영상 재생
7. crop할 시작시점 설정, 옆 input 칸에서 입력 가능
8. crop할 종료시점 설정, 옆 input 칸에서 입력 가능
9. 영상이 선택되고, 이벤트가 선택되면 crop list에 추가
10. crop list에 있는 목록들을 수정 가능. ▲, ▼ 눌러 순서 변경 가능, refresh 눌러 cutList 초기화, 초기화는 영상을 다 만들고 나서 초기화버튼을 누른다.
11. cut list에 있는 목록들을 random 배치, video 생성, json 생성
-> video, json을 생성할 때 반드시 파일 이름에 .mp4, .json이 들어가야함
12. 옆 칸을 통해 원하는 프레임을 추출하거나, 그냥 tagging 툴로 이동


* * *

 

