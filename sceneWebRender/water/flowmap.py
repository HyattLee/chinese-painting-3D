from PIL import Image, ImageOps, ImageFilter
import random, copy
import numpy, math

class flowmap_core:
	__flowmap = []
	__sizeX = -1
	__sizeY = -1

	def __init__(self, sizeX, sizeY):
		self.__sizeX = sizeX
		self.__sizeY = sizeY
		for x in range(0, self.__sizeX):
			self.__flowmap.append([])
			for y in range(0, self.__sizeY):
				self.__flowmap[x].append([0, 0, 0])

	def __deNormalize(self, inputPix):
		return min(int(-inputPix*128+128), 255)


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


def generate(flowmapXZ):
	fm = flowmap_core(len(flowmapXZ), len(flowmapXZ[0]))
	for x in range(0, len(flowmapXZ)):
		for z in range(0, len(flowmapXZ[0])):
			fm.setPixel([x, z], flowmapXZ[x][z])

	fm.save('static/texture/Water_1_M_Flow.jpg', 5)
