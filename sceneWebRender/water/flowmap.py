from PIL import Image, ImageOps, ImageFilter
import random, copy
import numpy, math

class flowmap:
	__flowmap = []
	__sizeX = -1
	__sizeY = -1

	def __init__(self, path):
		im = Image.open(path)
		self.__sizeX, self.__sizeY = im.size
		print self.__sizeX, self.__sizeY
		print im.load()[0,0]

		for x in range(0, self.__sizeX):
			self.__flowmap.append([])
			for y in range(0, self.__sizeY):
				self.__flowmap[x].append([0, 0, 0])

	def __deNormalize(self, inputPix):
		return min(int(-inputPix*128+128), 255)

	def __setPixel(self, pos, RG):
		self.__flowmap[pos[0]][pos[1]] = (RG[0], RG[1], 0)

	def setPixel(self, pos, RG):
		self.__flowmap[pos[0]][pos[1]] = (RG[0], RG[1], 0)

	def save(self, path, blurR):
		image_tmp = Image.new("RGB", (self.__sizeX, self.__sizeY), (128,128,0))
		tmp = image_tmp.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmp[x, y] = (self.__deNormalize(self.__flowmap[x][y][0]), 
							self.__deNormalize(self.__flowmap[x][y][1]),
							self.__deNormalize(self.__flowmap[x][y][2]))
		image_tmp = image_tmp.filter(ImageFilter.GaussianBlur(radius=blurR))
		image_tmp.save(path)

mapSize = 700
fm = flowmap('heightMap.png')

for i in range(0, mapSize):
	for j in range(0, mapSize):
		if i>mapSize*0.8:
			fm.setPixel([i, j], [0,1])
		elif i<mapSize*0.2:
			fm.setPixel([i, j], [0,-1])
		else:
			fm.setPixel([i, j], [0,0])

		if j<mapSize*0.2:
			fm.setPixel([i, j], [1,0])
		elif j>mapSize*0.8:
			fm.setPixel([i, j], [-1,0])


fm.save('../static/texture/Water_1_M_Flow.jpg', 0.1*mapSize)