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
    'VGA': ('640', '480'), # SD, 480p와 동일
    }


def resolution(inputpath, outputpath, width, height, fps):

    re_width, re_height = res['VGA']

    command = [
        'ffmpeg',
        '-i', inputpath,
        '-vf', 'scale='+str(re_width)+':'+str(re_height),
        outputpath
    ]
    subprocess.run(command)


def video_info(videopath):
    width, height, fps = None, None, None
    vcap = cv2.VideoCapture(videopath)
    if vcap.isOpened():
        width = vcap.get(3)
        height = vcap.get(4)
        # fps = vcap.get(5)
    video = VideoFileClip(videopath)

    return [width, height, round(video.fps)]


def main():
    if not os.path.isdir(os.path.join('videos2', 'origianl_resize')):
        os.makedirs(os.path.join('videos2', 'origianl_resize'))

    video_list = glob.glob(os.path.join('videos2', 'original', '*'))

    for videopath in video_list:
        base = os.path.basename(videopath)
        video, ext = base.split('.')
        meta_data = video_info(videopath)

        output_name = os.path.join('videos2', 'origianl_resize', base)
        resolution(videopath, output_name, *meta_data)

main()


