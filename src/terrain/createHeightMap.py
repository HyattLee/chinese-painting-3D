from PIL import Image, ImageOps, ImageFilter
import random, copy
import math


def initZeroMap(size):
	dataMap = []
	for x in range(0, size[0]):
		dataMap.append([])
		for y in range(0, size[1]):
			dataMap[x].append(0)
	return dataMap

def createMountain(size, mountainsDescription, upperBound):
	baseMatrix = initZeroMap((size[0], size[1]))
	tmpHeightest = 0
	print 'creating mountains...'
	for mountain in mountainsDescription:
		x0 = mountain['x0']*size[0]
		y0 = mountain['y0']*size[1]
		rl = mountain['rl']*size[0]
		rh = mountain['rh']*size[0]
		h = mountain['h']*size[1]

		for x in range(int(x0-rl), int(x0+rl)):
			for y in range(int(y0-rl), int(y0+rl)):
				x = float(x)
				y = float(y)
				if x>=0 and x<size[0] and y>=0 and y<size[1]:
					delta = math.sqrt((x-x0)*(x-x0)+(y-y0)*(y-y0))
					h_tmp = 0
					if delta>rh:
						h_tmp = h - (((delta-rh)*h)/(rl-rh))
					else:
						h_tmp = h
					if h_tmp>baseMatrix[int(x)][int(y)]:
						baseMatrix[int(x)][int(y)] = h_tmp

					if h_tmp>tmpHeightest:
						tmpHeightest = h_tmp

	tmpScale = float(255)/tmpHeightest
	print 'scaling', tmpScale
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			baseMatrix[x][y] = baseMatrix[x][y]*tmpScale
	return baseMatrix

def createPlane(size, planesDescription, upperBound):
	baseMatrix = initZeroMap((size[0], size[1]))
	print 'creating planes...'
	for plane in planesDescription:
		Ax = plane['Ax']*size[0]
		Ay = plane['Ay']*size[1]
		Bx = plane['Bx']*size[0]
		By = plane['By']*size[1]

		for x in range(int(Ax-20), int(Ax+20)):
			for y in range(2*int(By)-int(Ay), int(Ay)):
				x = float(x)
				y = float(y)
				if x>=0 and x<size[0] and y>=0 and y<size[1]:
					baseMatrix[int(x)][int(y)] = upperBound
	return baseMatrix

def mountainPlusPlaneWithSmooth(size, mountainMap, planeMap, gaussianBlurRadius):
	baseMatrix = initZeroMap((size[0], size[1]))
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			baseMatrix[x][y] = max(mountainMap[x][y], planeMap[x][y])

	tmp = Image.new("RGB", (size[0], size[1]), "white").convert("L")
	tmpData = tmp.load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			tmpData[x, y] = int(baseMatrix[x][y])
	tmpData = tmp.filter(ImageFilter.GaussianBlur(radius=gaussianBlurRadius)).load()
	#tmpData = tmp.filter(ImageFilter.MedianFilter(gaussianBlurRadius)).load()
	#tmpData = tmp.filter(ImageFilter.RankFilter(5,13)).load()
	#tmpData = tmp.filter(ImageFilter.BLUR).load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			baseMatrix[x][y] = tmpData[x, y]

	return baseMatrix

def addNoiseToMap(size, mountainMap, dataMap, intensity, upperBound, gaussianBlurRadius):
	tmp = Image.new("RGB", (size[0], size[1]), "white").convert("L")
	tmpData = tmp.load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			tmpData[x, y] = int(random.uniform(upperBound-intensity, upperBound))

	tmpData = tmp.filter(ImageFilter.GaussianBlur(radius=gaussianBlurRadius)).load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			if mountainMap[x][y]!=0:
				dataMap[x][y] = dataMap[x][y] + tmpData[x, y]
	return dataMap
