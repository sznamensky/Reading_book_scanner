#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  button_ctrl_takepic_undist_preproc_raspy5_v3_47_imx219.py    RELEASE   
# 29 05 2026
# Algorythm Talking Scanner 7.1
# The program takes control from the button
# The program takes the scan image from two cameras imx219
# The program controls the light for scans
# The program is using the camera calibration results obtained from calibrate_camera_v3_22.py script
# The program processes the scanned images to compensate for the cameras  distortion 
# The program rotates 90 degrees the scanned images (left and right pages)
# The program crops the image to upper, left, right page borders  and then writes to output file (OCR noise reduction purpose)
# The program outputs scan image files
# 
# Command line: python button_ctrl_takepic_undist_preproc_raspy5_v3_47_imx219.py 
# Output file names: <page_??>.png 
# Output directory: /tmp/TalkingScanner 
#  
#  Copyright 2026 Сергей Львович Знаменский <serzn@mail.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#   
from gpiozero import LED
from gpiozero import Button
import os
from picamera2 import Picamera2, Preview 
#from libcamera import controls			# added for camera mode controls
import time 
from time import sleep
import numpy as np
import cv2 as cv
import glob
import sys

# the talking scanner  global variable - when set to True the activity  of the talking scanner run 
Confirmed = False

strt_line = 0		#  variable from which processing begin line in the frame
thres_wht_pxs = 500		# variable defines threshod for the number of white pixels (255) in the line 

L_img_up_brd_line = 0		# variable defines the upper border of the book left page  in the scan image
R_img_up_brd_line = 0		# variable defines the upper border of the book right page  in the scan image
L_img_crop_right_line = 50	# set variable that defines the right side border of the book left page  in the scan image
R_img_crop_right_line = 0	# variable defines the right side border of the book right page  in the scan image
L_img_crop_left_line = 0	# variable defines the left side border of the book left page  in the scan image
R_img_crop_left_line = 50	# set variable that defines the left side border of the book right page  in the scan image


def cnt_wht_pxl_in_rw(bin_img, row_num):	# function returns the number of white pixels in image row
	wht_pxl_cntr = 0
	row = bin_img[row_num]
	for i in row:
		if i == 255:
			wht_pxl_cntr += 1
	return wht_pxl_cntr

def cnt_wht_pxl_in_clmn(bin_img, clmn_num):	# function returns the number of white pixels in image column
	wht_pxl_cntr = 0
	clmn = bin_img[:, clmn_num]
	for i in clmn:
		if i == 255:
			wht_pxl_cntr += 1
	return wht_pxl_cntr

def find_upr_pg_brd(bin_img, thrd):		# function returns the row number of the upper page border
	h, w = bin_img.shape[:2]
	for i in range(h):
		if cnt_wht_pxl_in_rw(bin_img, i) > thrd:
			return i
			break
		else:
			continue
	return 0

def find_left_page_left_brd(bin_img, thrd):		# function returns the column number of the left page left border
	h, w = bin_img.shape[:2]
	for i in range(w):
		if cnt_wht_pxl_in_clmn(bin_img, i) > thrd:
			return i
			break
		else:
			continue
	return 0

def find_right_page_right_brd(bin_img, thrd):		# function returns the column number of the right page right border
	h, w = bin_img.shape[:2]
	for i in range(w - 1, 0, -1):
		if cnt_wht_pxl_in_clmn(bin_img, i) > thrd:
			return i
			break
		else:
			continue
	return 0 


# Button setup 
# Create the object for button control using GPIO 26
button = Button(26, hold_time = 4, bounce_time = 0.2)	

# callback function for button pressed is reserved for future
def pressed():
	#print('button pressed')
	return None
	
# callback function for the button released - initiates the activity within the talking scanner main cycle 
def confirm():
	global Confirmed
	Confirmed = True
	#print('button released, main cycle initiated')
	
# callback function for the button held 4 sec reserved for pause in reading
def pause():
	print('button held 4 sec')

# Define the right camera imx219 calibration matrix (to be imported from the calibration script results)
camera_matrix_R = np.array([[1.26005723e+04,   0.00000000e+00,  1.68573220e+03],
     [  0.00000000e+00,  1.27186930e+04,  1.18055038e+03],
     [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])
# Define the right camera distortion coefficients (to be imported from the calibration script results)
dist_coefs_R = np. array([-4.05956748e+00, 1.96364621e+01, -1.20845679e-02,  -7.50521553e-03, 2.05858337e+02])


# Define the left camera imx219 calibration matrix (to be imported from the calibration script results)
camera_matrix_L = np.array([[3.89228520e+03,   0.00000000e+00, 1.59530385e+03],
       [  0.00000000e+00, 3.90012102e+03, 1.28080704e+03],
       [  0.00000000e+00,   0.00000000e+00,   1.00000000e+00]])
# Define the left camera distortion coefficients (to be imported from the calibration script results)
dist_coefs_L = np. array([ -0.35572087, -0.10794404, 0.00191215, -0.00399379, 1.00119409])

# create pi camera objects
camera_R = Picamera2(0)
camera_L = Picamera2(1)

# create light objects for right (R) and left (L) scanning surfaces (pages)
led_R = LED(22)
led_L = LED(23)


# function initialize camera
def initialize_camera(camera):
	camera.start_preview()
	#time.sleep(2)
	config = camera.create_still_configuration()
	camera.configure(config)
	#camera.controls.ExposureTime = 10000	# set exposure time
	#camera.controls.AnalogueGain = 1.0			# set analogue gain
	#camera.controls.Sharpness = 1.0				# set sharpness from 0.0 to 16.0
	#camera.controls.Contrast = 1.0					# set contrast from 0.0 to 32.0
	#camera.controls.Brightness = 0.0				# set brightness from -1.0 to 1.0
	#camera.controls.Saturation = 1.0				# set saturation from 0.0 to 32.0
	#camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 0.0})		# set manual focus mode and lens position
	#camera.controls.AfMode = Manual				# set manual focus mode 
	#camera.controls.LensPosition = 0.0				# set lest position for manual focus
	
# function makes scan with camera
def make_scan(camera):
	camera.start()
	image = camera.capture_array()
	camera.stop()
	return image	



def main():
	
	global Confirmed
	global thres_wht_pxs
	global up_brd_line
	
	initialize_camera(camera_L)
	initialize_camera(camera_R)
	
	
	
	# the talking scanner  global variable - when set to True the activity  of the talking scanner run 
	Confirmed = False
		
	# wait cycle for the button pressed to scan the book
	counter = 30
	while Confirmed == False:
		if counter == 30:
			print('Положите книгу. Нажмите кнопку. И я прочитаю. \n')
			counter = 0
		# run callback function when button pressed (reserved for future)
		#button.when_pressed = pressed
		# run callback function confirm when button released - initiates activity in the main cycle
		button.when_released = confirm
		# run callback function when button held 4" - (reserved for future) to be used for pause in reading
		#button.when_held = pause
		time.sleep(1)
		counter += 1
		continue
	
	# Scan with right camera

	# turn on the light R
	led_R.on()

	# load scan image from camera R
	image = make_scan(camera_R)

	# turn off the light R
	led_R.off()

	# preprocess image R	ADDED CONVERSION TO GRAY THEN FILTERS CLAHE AND BIN THRESHOLD
	#img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
	gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)		# CHANGED TO GRAY CONVERSION
	clahe = cv.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))	# CHANGED CLIPLIMIT FROM 2.0 TO 1.5
	cl_equalized_gray = clahe.apply(gray_img)
	thres_val, img = cv.threshold(cl_equalized_gray, 130, 255, cv.THRESH_BINARY)	# THRESHOLD 150 AND BINARY CONVERSION
		
	h,  w = img.shape[:2]
	print('h w :', h, w)
	newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix_R, dist_coefs_R, (w,h), 1, (w,h))
				
	# undistort image R
	dst = cv.undistort(img, camera_matrix_R, dist_coefs_R, None, newcameramtx)
	
	# crop the image R 
	x, y, w, h = roi
	dst = dst[y:y+h, x:x+w]
	
	# rotate the image R 90 counterclockwise	
	dstRotate90 = cv.rotate(dst, cv.ROTATE_90_COUNTERCLOCKWISE)

	# Define crop image R borders
	#h, w = dstRotate90.shape[:2]
	R_img_up_brd_line = find_upr_pg_brd(dstRotate90, thres_wht_pxs)	+ 30
	R_img_crop_right_line = find_right_page_right_brd(dstRotate90, thres_wht_pxs) - 80
	#print('R_img_crop_right_line :', R_img_crop_right_line)
	


	# Define names to save scanned image R file and related OCR results file
	NextImgFileName = "/tmp/TalkingScanner/page_2.png"
	
	
	# Save scanned image R to file
	cv.imwrite(NextImgFileName, dstRotate90[R_img_up_brd_line:, R_img_crop_left_line:R_img_crop_right_line])
	#cv.imwrite(NextImgFileName, dstRotate90)
	print('Scanned image R saved to file name : ', NextImgFileName)
		
		
	# Scan with left camera

	# turn on the light L
	led_L.on()

	# load scan image from camera L
	image = make_scan(camera_L)

	# turn off the light L
	led_L.off()

	# preprocess image L	ADDED CONVERSION TO GRAY THEN FILTERS CLAHE AND BIN THRESHOLD
	#img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
	gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)		# CHANGED TO GRAY CONVERSION
	clahe = cv.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))	# CHANGED CLIPLIMIT FROM 2.0 TO 1.5
	cl_equalized_gray = clahe.apply(gray_img)
	thres_val, img = cv.threshold(cl_equalized_gray, 125, 255, cv.THRESH_BINARY)	# THRESHOLD 150 AND BINARY CONVERSION
	
	
	h,  w = img.shape[:2]
	print('h w :', h, w)
	newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix_L, dist_coefs_L, (w,h), 1, (w,h))
				
	# undistort image L
	dst = cv.undistort(img, camera_matrix_L, dist_coefs_L, None, newcameramtx)
	
	# crop the image L 
	x, y, w, h = roi
	dst = dst[y:y+h, x:x+w]
	
	# rotate the image L 90 counterclockwise
	dstRotate90 = cv.rotate(dst, cv.ROTATE_90_CLOCKWISE)

	# Define crop image L borders
	h, w = dstRotate90.shape[:2]
	L_img_up_brd_line = find_upr_pg_brd(dstRotate90, thres_wht_pxs) + 30
	L_img_crop_left_line = find_left_page_left_brd(dstRotate90, thres_wht_pxs) + 60
	
	
	# Define names to save scanned image L file and related OCR results file
	NextImgFileName = "/tmp/TalkingScanner/page_1.png"
	
	# Save scanned image L to file ПРОВЕРКА ОБРЕЗАНИЯ КАДРА ЛЕВОЙ КАМЕРЫ СПРАВА
	
	
	cv.imwrite(NextImgFileName, dstRotate90[L_img_up_brd_line:, L_img_crop_left_line:w - L_img_crop_right_line])
	print('Scanned image L saved to file name : ', NextImgFileName)

	
	return 0

if __name__ == '__main__':
	main()
