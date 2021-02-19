import argparse
import json
import shutil
import subprocess
import os
import cv2
import random
import glob
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
    subprocess.run(command)


def framerate(inputpath, outputpath, width, height, fps, level='Light'):
    re_fps = level

    command = 'ffmpeg -y -i ' + inputpath + ' -vf "setpts=1.25*PTS" -r ' + str(re_fps) + ' ' + outputpath
    subprocess.call(command, shell=True)


def format(inputpath, outputpath, level='Light'):
    if level == '.mp4':
        new_ext = '.mp4'
    else:
        new_ext = '.avi'
    outputpath = outputpath + new_ext
    command = ''
    if new_ext == '.avi':
        command = 'ffmpeg -y -i ' + inputpath + ' -ar 22050 -b 2048k ' + outputpath
    elif new_ext == '.mp4':
        command = 'ffmpeg -y -i ' + inputpath + ' ' + outputpath
    # command = 'ffmpeg -y -i ' + inputpath + ' -codec copy ' + outputpath
    subprocess.call(command, shell=True)


def crop(inputpath, outputpath, width, height, fps, level='Light'):
    # crop_rate = random.choice(np.arange(0.5, 0.8, 0.1))
    # crop_locate = random.choice(np.arange(0.1, 0.25, 0.05))

    crop_locate = level
    # if level == 'Light':
    # 	crop_locate = 0.025
    # elif level == 'Medium':
    # 	crop_locate = 0.06
    # elif level == 'Heavy':
    # 	crop_locate = 0.1

    crop_rate = 1 - crop_locate

    crop_width = width * crop_rate
    crop_height = height * crop_rate
    crop_x = width * crop_locate
    crop_y = height * crop_locate

    command = 'ffmpeg -y -i ' + inputpath + ' -filter:v "crop= ' + str(crop_width) + ':' + str(crop_height) + ':' + str(
        crop_x) + ':' + str(crop_y) + '" ' + outputpath
    subprocess.call(command, shell=True)


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
    subprocess.call(command, shell=True)


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
    subprocess.call(command, shell=True)
# command = 'ffmpeg -y -i ' + \
# 		  outputpath + \
# 		  ' -vf scale=' + str(width) + ':' + str(height) + ' ' + \
# 		  outputpath

# subprocess.call(command, shell=True)


def add_logo(videopath, outputpath, width, height, fps, xlocation, ylocation, level='Light'):
    print("level :", level)
    if level == 'Light':
        logopath = random.choice(glob.glob(os.path.join('logo', 'Light', '*')))
    elif level == 'Medium':
        logopath = random.choice(glob.glob(os.path.join('logo', 'Medium', '*')))
    elif level == 'Heavy':
        logopath = random.choice(glob.glob(os.path.join('logo', 'Heavy', '*')))

    logoImg = cv2.imread(logopath, -1)
    temp_x = logoImg.shape[1]
    temp_y = logoImg.shape[0]

    # logo_x = width * 0.05
    # logo_y = height * 0.05
    logo_x = (width - temp_x) * xlocation
    logo_y = (height - temp_y) * ylocation

    command = 'ffmpeg -y -i ' + videopath + ' -i ' + logopath + ' -filter_complex "overlay=' + str(logo_x) + ":" + str(
        logo_y) + '" ' + outputpath

    print("command :", command)
    subprocess.call(command, shell=True)


def brightness(videopath, outputpath, level):
    print("level :", level)
    rate = level / 100
    print("rate :", rate)

    command = 'ffmpeg -y -i ' + videopath + ' -vf eq=brightness=' + str(rate) + ' -c:a copy ' + outputpath
    subprocess.call(command, shell=True)


def flip(videopath, outputpath, width, height, fps, level='Light'):
    if level == 'hflip':
        command = 'ffmpeg -y -i ' + videopath + ' -filter:v "hflip" -c:a copy ' + outputpath
    else:
        command = 'ffmpeg -y -i ' + videopath + ' -filter:v "vflip" -c:a copy ' + outputpath

    subprocess.call(command, shell=True)


def grayscale(videopath, outputpath, width, height, fps, level='Light'):
    command = 'ffmpeg -y -i ' + videopath + ' -vf format=gray ' + outputpath
    subprocess.call(command, shell=True)


def transform_videos(vid_path, save_path, json_path):
    filepath = vid_path
    tempSaveDirPath = "./videos"
    finalSavePath = save_path + '\\' + os.path.basename(vid_path)
    base = os.path.basename(vid_path)
    meta_data = video_info(vid_path)
    count = 1

    with open(json_path, 'r') as f:
        json_data = json.load(f)
    transforms = json_data['transforms']

    for t in transforms:
        transform = t['transform']
        level = t['level']

        if transform == 'brightness':  # 3
            brightness_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            brightness(filepath, path, level=brightness_level)
            filepath = path
            count += 1
            print("brightness")
        elif transform == 'crop':  # 3
            crop_level = level * 1000
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            crop(filepath, path, *meta_data, level=crop_level)

            filepath = path
            count += 1
            print("crop")
        elif transform == 'flip':  # 1
            flip_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            flip(filepath, path, *meta_data, level=flip_level)
            filepath = path
            count += 1
            print("flip")
        elif transform == 'format':  # 1
            format_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            format(filepath, path, *meta_data, level=format_level)
            filepath = path
            count += 1
            print("format")
        elif transform == 'framerate':  # 3
            framerate_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            framerate(filepath, path, *meta_data, level=framerate_level)
            filepath = path
            count += 1
            print("framerate")
        elif transform == 'grayscale':
            grayscale_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            grayscale(filepath, path, *meta_data, level='Light')
            filepath = path
            count += 1
            print("grayscale")
        elif transform == 'resolution':  # 2
            resolution_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            resolution(filepath, path, *meta_data, level=resolution_level)
            filepath = path
            count += 1
            print("resolution")
        elif transform == 'rotate':  # 1
            rotate_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            rotate(filepath, path, *meta_data, level=rotate_level)
            filepath = path
            count += 1
            print("rotate")
        elif transform == 'addlogo':  # 3
            print("왜 안 됨?")
            addlogo_level = level
            addlogo_x = int(t['location_x'].replace('%', ''))
            addlogo_y = int(t['location_y'].replace('%', ''))

            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            add_logo(filepath, path, *meta_data, addlogo_x / 100, addlogo_y / 100, level=addlogo_level)

            filepath = path
            count += 1
            print("addlogo")
        elif transform == 'border':  # 1
            border_level = level
            path = os.path.join(tempSaveDirPath, base.split('.')[0] + "_" + str(count) + "." + base.split('.')[1])
            add_border(filepath, path, *meta_data, level=border_level)
            filepath = path
            count += 1
            print("border")

        base = base.split('.')[0] + "_" + str(count - 1) + "." + base.split('.')[1]
        finalVideoPath = os.path.join(tempSaveDirPath, base)
        print("finalVideoPath :", finalVideoPath)
        print("finalSavePath :", finalSavePath)
        shutil.copyfile(finalVideoPath, finalSavePath)


parser = argparse.ArgumentParser(description='transform videos')

parser.add_argument('--video_dir_path', required=True, help="video directory path")
parser.add_argument('--save_dir_path', required=True, help="save directory path")
parser.add_argument('--json_file_path', required=True, help="json file path")

args = parser.parse_args()
video_dir_path = args.video_dir_path
save_dir_path = args.save_dir_path
json_file_path = args.json_file_path

for vid in os.listdir(video_dir_path):
    vid_path = os.path.join(video_dir_path, vid)
    transform_videos(vid_path, save_dir_path, json_file_path)
