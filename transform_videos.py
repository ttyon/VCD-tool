import argparse
import json
import shutil
import signal
import subprocess
import os
import cv2
import random
import glob
from collections import OrderedDict
import time
import numpy as np

from moviepy.video.io.VideoFileClip import VideoFileClip

res = {
    'SqCIF': ('128', '96'),
    'qCIF': ('176', '144'),
    'CIF': ('352', '288'),
    'qVGA': ('320', '240'),
    'VGA': ('640', '480'),  # SD, 480p와 동일
}


def resolution(inputpath, outputpath, width, height, fps, level='Light'):
    re_width, re_height = None, None
    if level == 'Light':
        re_width, re_height = res['CIF']
    else:
        re_width, re_height = res['qCIF']

    # re_width, re_height = res[level]

    command = [
        'ffmpeg', '-y',
        '-i', inputpath,
        '-vf', 'scale=' + str(re_width) + ':' + str(re_height),
        outputpath
    ]
    # os.system(command)
    subprocess.run(command)


def framerate(inputpath, outputpath, width, height, fps, level='Light'):
    re_fps = level

    command = 'ffmpeg -y -i ' + inputpath + ' -vf "setpts=1.25*PTS" -r ' + str(re_fps) + ' ' + outputpath
    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def format(inputpath, outputpath, level='Light'):
    if level == '.mp4':
        new_ext = '.mp4'
    else:
        new_ext = '.avi'
    # outputpath = outputpath + new_ext
    command = ''
    if new_ext == '.avi':
        command = 'ffmpeg -y -i ' + inputpath + ' -ar 22050 -b 2048k ' + outputpath
    elif new_ext == '.mp4':
        command = 'ffmpeg -y -i ' + inputpath + ' ' + outputpath
    # command = 'ffmpeg -y -i ' + inputpath + ' -codec copy ' + outputpath
    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def crop(inputpath, outputpath, width, height, fps, level='Light'):
    # crop_rate = random.choice(np.arange(0.5, 0.8, 0.1))
    # crop_locate = random.choice(np.arange(0.1, 0.25, 0.05))

    crop_locate = level / 1000
    # if level == 'Light':
    # 	crop_locate = 0.025
    # elif level == 'Medium':
    # 	crop_locate = 0.06
    # elif level == 'Heavy':
    # 	crop_locate = 0.1

    crop_rate = 1 - crop_locate

    crop_width = width * crop_rate
    crop_height = height * crop_rate
    crop_x = width * crop_locate / 2
    crop_y = height * crop_locate / 2
    #
    # print(f"crop_width : {crop_width}, crop_height : {crop_height}, crop_x : {crop_x}, crop_y : {crop_y}")

    command = 'ffmpeg -y -i ' + inputpath + ' -filter:v "crop= ' + str(crop_width) + ':' + str(crop_height) + ':' + str(
        crop_x) + ':' + str(crop_y) + '" ' + outputpath

    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def rotate(inputpath, outputpath, width, height, fps, level='Light'):
    if level == 90:
        transpose = '"transpose=1"'
    elif level == 180:
        transpose = '"transpose=2,transpose=2"'
    elif level == 270:
        transpose = '"transpose=2"'
    # rotate_list = ['"transpose=1"', '"transpose=2"', '"transpose=2,transpose=2"']
    # transpose = random.choice(rotate_list)
    command = 'ffmpeg -y -i ' + inputpath + ' -vf ' + transpose + ' ' + outputpath
    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def video_info(videopath):
    width, height, fps = None, None, None
    vcap = cv2.VideoCapture(videopath)
    if vcap.isOpened():
        width = vcap.get(3)
        height = vcap.get(4)
    # fps = vcap.get(5)
    video = VideoFileClip(videopath)

    return [width, height, round(video.fps)]


def add_border(videopath, outputpath, width, height, fps, level='Light'):
    if level == 'VGA':
        re_width, re_height = res['CIF']
        width, height = res['VGA']
    elif level == 'CIF':
        re_width, re_height = res['qCIF']
        width, height = res['CIF']

    command = [
        'ffmpeg', '-y',
        '-i', videopath,
        '-vf', 'scale=' + str(re_width) + ':' + str(re_height),
        'temp.flv'
    ]
    subprocess.run(command)

    command = 'ffmpeg -y -i ' + \
              'temp.flv' + \
              ' -vf "scale=\'min(' + width + ',iw)\':min\'(' + height + ',ih)\':force_original_aspect_ratio=decrease,pad=' + width + ':' + height + ':(ow-iw)/2:(oh-ih)/2" ' + \
              outputpath

    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)
# command = 'ffmpeg -y -i ' + \
# 		  outputpath + \
# 		  ' -vf scale=' + str(width) + ':' + str(height) + ' ' + \
# 		  outputpath

# subprocess.call(command, shell=True)


def add_logo(videopath, outputpath, width, height, fps, xlocation, ylocation, level='Light'):
    # if level == 'Light':
    #     logopath = random.choice(glob.glob(os.path.join('logo', 'Light', '*')))
    # elif level == 'Medium':
    #     logopath = random.choice(glob.glob(os.path.join('logo', 'Medium', '*')))
    # elif level == 'Heavy':
    #     logopath = random.choice(glob.glob(os.path.join('logo', 'Heavy', '*')))

    logopath = random.choice(glob.glob(os.path.join('.\\', 'logo', '*')))

    logoImg = cv2.imread(logopath, -1)
    level = int(level.replace('%', '')) / 100
    new_w = int(int(width) * level)
    new_h = int(int(height) * level)
    logoImg = cv2.resize(logoImg, dsize=(new_w, new_h), interpolation=cv2.INTER_AREA)
    cv2.imwrite('./temp.png', logoImg)

    temp_x = logoImg.shape[1]
    temp_y = logoImg.shape[0]

    # logo_x = width * 0.05
    # logo_y = height * 0.05
    logo_x = (width - temp_x) * xlocation
    logo_y = (height - temp_y) * ylocation

    command = 'ffmpeg -y -i ' + videopath + ' -i ' + logopath + ' -filter_complex "overlay=' + str(logo_x) + ":" + str(
        logo_y) + '" ' + outputpath

    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def brightness(videopath, outputpath, level):
    rate = level / 100

    command = 'ffmpeg -y -i ' + videopath + ' -vf eq=brightness=' + str(rate) + ' -c:a copy ' + outputpath
    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def flip(videopath, outputpath, width, height, fps, level='Light'):
    if level == 'hflip':
        command = 'ffmpeg -y -i ' + videopath + ' -filter:v "hflip" -c:a copy ' + outputpath
    else:
        command = 'ffmpeg -y -i ' + videopath + ' -filter:v "vflip" -c:a copy ' + outputpath

    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def grayscale(videopath, outputpath, width, height, fps, level='Light'):
    command = 'ffmpeg -y -i ' + videopath + ' -vf format=gray ' + outputpath
    # os.system(command)
    subprocess.call(command, shell=True, stdin=None)


def transform_videos(vid_path, save_path, json_path):

    if not os.path.isdir("./videos"):
        os.makedirs("./videos")

    formatIs = False
    formatLevel = None

    filepath = vid_path
    filebase = os.path.basename(filepath)
    tempSaveDirPath = "./videos/"
    finalSavePath = save_path + '/' + os.path.basename(vid_path)
    # meta_data = video_info(vid_path)
    count = 1

    with open(json_path, 'r') as f:
        json_data = json.load(f)
    transforms = json_data['transforms']

    data = OrderedDict()
    data["video_name"] = filebase
    transformData = []

    for t in transforms:
        transform = t['transform']
        level = t['level']

        meta_data = video_info(filepath)

        if transform == 'brightness':  # 3
            brightness_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("brightness path :", path)
            brightness(filepath, path, level=brightness_level)
            json_transform = "brightness"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'crop':  # 3
            crop_level = level * 1000
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("crop path :", path)
            crop(filepath, path, *meta_data, level=crop_level)
            json_transform = "crop"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'flip':  # 1
            flip_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("flip path :", path)
            flip(filepath, path, *meta_data, level=flip_level)
            json_transform = "flip"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'framerate':  # 3
            framerate_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("framerate path :", path)
            framerate(filepath, path, *meta_data, level=framerate_level)
            json_transform = "framerate"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'grayscale':
            grayscale_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("grayscale path :", path)
            grayscale(filepath, path, *meta_data, level='Light')
            json_transform = "grayscale"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'resolution':  # 2
            resolution_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("resolution path :", path)
            resolution(filepath, path, *meta_data, level=resolution_level)
            json_transform = "resolution"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'rotate':  # 1
            rotate_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("rotate path :", path)
            rotate(filepath, path, *meta_data, level=rotate_level)
            json_transform = "rotate"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'addlogo':  # 3
            addlogo_level = level
            addlogo_x = int(t['location_x'].replace('%', ''))
            addlogo_y = int(t['location_y'].replace('%', ''))

            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("addlogo path :", path)
            add_logo(filepath, path, *meta_data, addlogo_x / 100, addlogo_y / 100, level=addlogo_level)
            json_transform = "addlogo"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'border':  # 1
            border_level = level
            # path = os.path.join(tempSaveDirPath, filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1])
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1]
            # print("border path :", path)
            add_border(filepath, path, *meta_data, level=border_level)
            json_transform = "border"
            transformData.append({"transform": json_transform,
                                  "level": level})
        elif transform == 'format':  # 1
            format_level = level
            path = tempSaveDirPath + filebase.split('.')[0] + "_" + str(count) + "." + filebase.split('.')[1] + format_level
            # print("format path :", path)
            # print("format_level :", format_level)
            format(filepath, path, level=format_level)

            json_transform = "format"
            transformData.append({"transform": json_transform,
                                  "level": level})

            formatIs = True
            formatLevel = format_level

        filepath = path
        count += 1

    finalBase = filebase

    data["transforms"] = transformData
    with open(save_path + '/' + finalBase + '.json', 'w', encoding='utf-8') as make_file:
        json.dump(data, make_file, indent="\t")

    if formatIs:
        base = filebase.split('.')[0] + "_" + str(count - 1) + "." + filebase.split('.')[1] + formatLevel
        finalVideoPath = tempSaveDirPath + base

        finalSavePath = finalSavePath + formatLevel
    else:
        base = filebase.split('.')[0] + "_" + str(count - 1) + "." + filebase.split('.')[1]
        finalVideoPath = tempSaveDirPath + base

    shutil.copyfile(finalVideoPath, finalSavePath)


parser = argparse.ArgumentParser(description='transform videos')

# parser.add_argument('--video_dir_path', required=False, default="C:/Users/jslee/Desktop/VCDB", help="video directory path")
# parser.add_argument('--save_dir_path', required=False, default="C:/Users/jslee/Desktop/vvv", help="save directory path")
# parser.add_argument('--json_file_path', required=False, default="C:/Users/jslee/ttyon/VCD-tool/test/realfinaltest.json", help="json file path")
parser.add_argument('--video_dir_path', required=True, help="video directory path")
parser.add_argument('--save_dir_path', required=True, help="save directory path")
parser.add_argument('--json_file_path', required=True, help="json file path")

args = parser.parse_args()
video_dir_path = args.video_dir_path
save_dir_path = args.save_dir_path
json_file_path = args.json_file_path

video_dir_path = video_dir_path.replace("\\", "/")
save_dir_path = save_dir_path.replace("\\", "/")
json_file_path = json_file_path.replace("\\", "/")

for vid in os.listdir(video_dir_path):
    vid_path = os.path.join(video_dir_path, vid)
    transform_videos(vid_path, save_dir_path, json_file_path)

