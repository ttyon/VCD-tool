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
    'VGA': ('640', '480'), # SD, 480p와 동일
       }


def resolution(inputpath, outputpath, width, height, fps, level='Light'):
	if level == 'Light':
		re_width, re_height = res['CIF']
	elif level == 'Medium':
		re_width, re_height = res['qCIF']

	command = [
		'ffmpeg', '-y',
		'-i', inputpath,
		'-vf', 'scale='+str(re_width)+':'+str(re_height),
		outputpath
	]
	subprocess.run(command)


def framerate(inputpath, outputpath, width, height, fps, level='Light'):
	if level == 'Light':
		re_fps = 20
	elif level == 'Medium':
		re_fps = 10
	elif level == 'Heavy':
		re_fps = 5

	command = 'ffmpeg -y -i ' + inputpath + ' -vf "setpts=1.25*PTS" -r ' + str(re_fps) + ' ' + outputpath
	subprocess.call(command, shell=True)


def format(inputpath, outputpath, level='Light'):
	new_ext = random.choice(['.mp4', '.avi'])
	outputpath = outputpath + new_ext
	command = ''
	if new_ext=='.avi':
		command = 'ffmpeg -y -i ' + inputpath + ' -ar 22050 -b 2048k ' + outputpath
	elif new_ext == '.mp4':
		command = 'ffmpeg -y -i ' + inputpath + ' ' + outputpath
		# command = 'ffmpeg -y -i ' + inputpath + ' -codec copy ' + outputpath
	subprocess.call(command, shell=True)


def crop(inputpath, outputpath, width, height, fps, level='Light'):
	# crop_rate = random.choice(np.arange(0.5, 0.8, 0.1))
	# crop_locate = random.choice(np.arange(0.1, 0.25, 0.05))

	crop_locate = None
	if level == 'Light':
		crop_locate = 0.025
	elif level == 'Medium':
		crop_locate = 0.06
	elif level == 'Heavy':
		crop_locate = 0.1

	crop_rate = 1-crop_locate

	crop_width = width * crop_rate
	crop_height = height *crop_rate
	crop_x = width * crop_locate
	crop_y = height * crop_locate

	command = 'ffmpeg -y -i ' + inputpath + ' -filter:v "crop= ' + str(crop_width) + ':' + str(crop_height) + ':' + str(crop_x) + ':' + str(crop_y) + '" ' + outputpath
	subprocess.call(command, shell=True)


def rotate(inputpath, outputpath, width, height, fps, level='Light'):
	rotate_list = ['"transpose=1"', '"transpose=2"', '"transpose=2,transpose=2"']
	transpose = random.choice(rotate_list)
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

	re_width, re_height = res['CIF']
	width, height = res['VGA']

	command = [
		'ffmpeg', '-y',
		'-i', videopath,
		'-vf', 'scale='+str(re_width)+':'+str(re_height),
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


def add_logo(videopath, outputpath, width, height, fps, level='Light'):
	if level == 'Light':
		logopath = random.choice(glob.glob(os.path.join('logo', 'logo_Light', '*')))
	elif level == 'Medium':
		logopath = random.choice(glob.glob(os.path.join('logo', 'logo_Medium', '*')))
	elif level == 'Heavy':
		logopath = random.choice(glob.glob(os.path.join('logo', 'logo_Heavy', '*')))

	logo_x = width * 0.05
	logo_y = height * 0.05

	command = 'ffmpeg -y -i ' + videopath + ' -i ' + logopath+ ' -filter_complex "overlay=' + str(logo_x) + ":" + str(logo_y) + '" ' + outputpath
	subprocess.call(command, shell=True)


def brightness(videopath, outputpath, width, height, fps, level='Light'):
	if level == 'Light':
		rate = random.choice([0.09, -0.09])
	elif level == 'Medium':
		rate = random.choice([0.18, -0.36])
	elif level == 'Heavy':
		rate = random.choice([0.36, -0.18])

	command = 'ffmpeg -y -i ' + videopath +' -vf eq=brightness=' + str(rate) + ' -c:a copy ' + outputpath
	subprocess.call(command, shell=True)


def flip(videopath, outputpath, width, height, fps, level='Light'):
	command1 = 'ffmpeg -y -i ' + videopath + ' -filter:v "hflip" -c:a copy ' + outputpath
	command2 = 'ffmpeg -y -i ' + videopath + ' -filter:v "vflip" -c:a copy ' + outputpath
	command = random.choice([command1, command2])
	subprocess.call(command, shell=True)


def grayscale(videopath, outputpath, width, height, fps, level='Light'):
	command = 'ffmpeg -y -i ' + videopath + ' -vf format=gray ' + outputpath
	subprocess.call(command, shell=True)


def main(level, dataset_path):
	video_list = glob.glob(os.path.join(dataset_path, 'original_SD', '*')) # 원형 비디오셋 저장 경로

	print("len :", len(video_list))
	for videopath in video_list:
		base = os.path.basename(videopath)
		print("base :",base)
		video, ext = base.split('.')
		meta_data = video_info(videopath)


		output_name = os.path.join(dataset_path, 'framerate', level, base)
		framerate(videopath, output_name, *meta_data, level=level)

		output_name = os.path.join(dataset_path, 'crop', level, base)
		crop(videopath, output_name, *meta_data, level=level)

		output_name = os.path.join(dataset_path, 'logo', level, base)
		add_logo(videopath, output_name, *meta_data, level=level)

		output_name = os.path.join(dataset_path, 'brightness', level, base)
		brightness(videopath, output_name, *meta_data, level=level)

		# output_name = os.path.join(dataset_path, 'resolution', level, base)
		# resolution(videopath, output_name, *meta_data, level=level)

		# output_name = os.path.join(dataset_path, 'format', level, video)
		# format(videopath, output_name, level=level)

		# output_name = os.path.join(dataset_path, 'border', level, base)
		# add_border(videopath, output_name, *meta_data, level=level)

		# output_name = os.path.join(dataset_path, 'rotate', level, base)
		# rotate(videopath, output_name, *meta_data, level=level)

		# output_name = os.path.join(dataset_path, 'flip', level, base)
		# flip(videopath, output_name, *meta_data, level=level)

		# output_name = os.path.join(dataset_path, 'grayscale', level, base)
		# grayscale(videopath, output_name, *meta_data, level=level)


if __name__ == '__main__':
	dataset_path = '/transformed_video'
	# level = 'Light'
	# level = 'Medium'
	level = 'Heavy'

	# level = ['Light', 'Medium', 'Heavy']
	# for l in level:
	# if not os.path.isdir(os.path.join(dataset_path, 'resolution', level)):
	# 	os.makedirs(os.path.join(dataset_path, 'resolution', level))
	if not os.path.isdir(os.path.join(dataset_path, 'framerate', level)):
		os.makedirs(os.path.join(dataset_path, 'framerate', level))
	# if not os.path.isdir(os.path.join(dataset_path, 'format', level)):
	# 	os.makedirs(os.path.join(dataset_path, 'format', level))
	if not os.path.isdir(os.path.join(dataset_path, 'crop', level)):
		os.makedirs(os.path.join(dataset_path, 'crop', level))
	# if not os.path.isdir(os.path.join(dataset_path, 'border', level)):
	# 	os.makedirs(os.path.join(dataset_path, 'border', level))
	if not os.path.isdir(os.path.join(dataset_path, 'logo', level)):
		os.makedirs(os.path.join(dataset_path, 'logo', level))
	# if not os.path.isdir(os.path.join(dataset_path, 'rotate', level)):
	# 	os.makedirs(os.path.join(dataset_path, 'rotate', level))
	if not os.path.isdir(os.path.join(dataset_path, 'brightness', level)):
		os.makedirs(os.path.join(dataset_path, 'brightness', level))
	# if not os.path.isdir(os.path.join(dataset_path, 'flip', level)):
	# 	os.makedirs(os.path.join(dataset_path, 'flip', level))
	# if not os.path.isdir(os.path.join(dataset_path, 'grayscale', level)):
	# 	os.makedirs(os.path.join(dataset_path, 'grayscale', level))

	main(level, dataset_path)


