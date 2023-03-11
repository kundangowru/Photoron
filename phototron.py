import RPi.GPIO as gpio
import time
import imutils
import cv2

min1=12
min2=16
min3=18
min4=22

us_trig=13
us_echo=15

def motor_init():
	gpio.setmode(gpio.BOARD)
	gpio.setup(min1,OUT)
	gpio.setup(min2,OUT)
	gpio.setup(min3,OUT)
	gpio.setup(min4,OUT)

def us_init():
	gpio.setmode(gpio.BOARD)
	gpio.setup(us_trig,gpio.OUT)
	gpio.setup(us_echo,gpio.IN)

def distance():
	us_init()
	gpio.output(us_trig,True)
	time.sleep(0.00001)
	gpio.output(us_trig,False)
	nosig=time.time()
	sig=time.time()
	while gpio.input(us_echo)==0:
		nosig=time.time()
	while gpio.input(us_echo)==1:
		sig=time.time()
	t1=sig-nosig
	distance=(t1*34000)/2
	gpio.cleanup()
	return distance

def forward(tx):
	motor_init()
	gpio.output(min1,True)
	gpio.output(min2,False)
	gpio.output(min3,True)
	gpio.output(min4,False)
	time.sleep(tx)
	gpio.cleanup()

def turn(tx):
	motor_init()
	gpio.output(min1,True)
	gpio.output(min2,False)
	gpio.output(min3,False)
	gpio.output(min4,True)
	time.sleep(tx)
	gpio.cleanup()

def goforward():
	dist=distance()
	while dist>20:
		forward(1)
	turn(2)
	dist=distance()
	while dist>150:
		forward(1)

def detect_shape():
	cam=cv2.VideoCapture(0)
	if cam.isOpened()==False:
		cam.open()
	(ret,image)=cam.read()
	resized=imutils.resize(image,width=300)
	resized=resized[35:210,0:275]
	gray=cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
	blurred=cv2.GaussianBlur(gray,(5,5),0)
	_,thresh=cv2.threshold(blurred,90,255,cv2.THRESH_BINARY_INV)
	(img,cnts,hierarchy)=cv2.findContours(thresh.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	peri=cv2.arcLength(cnts[0],True)
	approx=cv2.approxPolyDP(cnts[0],0.04*peri,True)
	if len(approx)==3:
		shape="triangle"
	elif len(approx)==4:
		shape="square"
	elif len(approx)==10:
		shape="star"
	else:
		shape="circle"
	cam.release()
	return shape

img1=detect_shape()
time.sleep(5)
while True:
	img2=detect_shape()
	if img1==img2:
		goforward()
		exit()
	else:
		turn(1)
