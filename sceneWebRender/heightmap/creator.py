from PIL import Image, ImageOps, ImageFilter
import random, copy
import numpy, math

class heightMap:
	__noiseMap = []
	__heightMap = []
	__planeMap = []
	__treeMap = []
	__synthesizedMap = []
	__sizeX = None
	__sizeY = None
	__randomScale = 1
	__terrainMap = []

	def __init__(self, size):
		self.__sizeX = int(size[0])
		self.__sizeY = int(size[1])
		for x in range(0, self.__sizeX):
			self.__heightMap.append([])
			self.__noiseMap.append([])
			self.__planeMap.append([])
			self.__treeMap.append([])
			self.__terrainMap.append([])
			self.__synthesizedMap.append([])
			for y in range(0, self.__sizeY):
				self.__heightMap[x].append(0)
				self.__noiseMap[x].append(0)
				self.__planeMap[x].append(0)
				self.__treeMap[x].append(0)
				self.__terrainMap[x].append(0)
				self.__synthesizedMap[x].append(0)

	#noise map
	def smoothNoise(self, gaussianBlurRadius):
		tmp = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")
		tmpData = tmp.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmpData[x, y] = int(self.__noiseMap[x][y])
		tmpData = tmp.filter(ImageFilter.GaussianBlur(radius=gaussianBlurRadius)).load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__noiseMap[x][y] = tmpData[x, y]

	def createNoiseForMountains(self, intensity, upperBound):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__heightMap[x][y]>0:
					self.__noiseMap[x][y] = random.uniform(upperBound-intensity, upperBound)

	#tree map
	def createTree(self, intensity, topLine, rare):
		count = 0
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__heightMap[x][y]>30*self.__randomScale and count%(rare)==0:
					self.__treeMap[x][y] = (random.uniform(0, intensity))
				count = count + 1

	#mountain map
	def adjustMountains(self, upperBound):
		tmpHeightest = 0
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__heightMap[x][y]>tmpHeightest:
					tmpHeightest = self.__heightMap[x][y]

		tmpScale = float(255)/tmpHeightest
		print 'scaling', tmpScale
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__heightMap[x][y] = self.__heightMap[x][y]*tmpScale

	def createMountains(self, mountainsDescription):
		baseMatrix = numpy.zeros((self.__sizeX, self.__sizeY))
		print 'creating mountains...'
		for mountain in mountainsDescription:
			x0 = mountain['x0']*self.__sizeX
			y0 = mountain['y0']*self.__sizeY
			rl = mountain['rl']*self.__sizeX
			rh = mountain['rh']*self.__sizeX
			h = mountain['h']*self.__sizeY

			for x in range(int(x0-rl), int(x0+rl)):
				for y in range(int(y0-rl), int(y0+rl)):
					x = float(x)
					y = float(y)
					if x>=0 and x<baseMatrix.shape[0] and y>=0 and y<baseMatrix.shape[1]:
						delta = math.sqrt((x-x0)*(x-x0)+(y-y0)*(y-y0))
						h_tmp = 0
						if delta>rh:
							h_tmp = h - (((delta-rh)*h)/(rl-rh))
						else:
							h_tmp = h
						if h_tmp>baseMatrix[int(x), int(y)]:
							baseMatrix[int(x), int(y)] = h_tmp

		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__heightMap[x][y] = self.__heightMap[x][y] + baseMatrix[int(x), int(y)]

	def createPlanes(self, planesDescription):
		baseMatrix = numpy.zeros((self.__sizeX, self.__sizeY))
		print 'creating planes...'
		for plane in planesDescription:
			Ax = plane['Ax']*self.__sizeX
			Ay = plane['Ay']*self.__sizeY
			Bx = plane['Bx']*self.__sizeX
			By = plane['By']*self.__sizeY

			for x in range(int(Ax-20), int(Ax+20)):
				for y in range(2*int(By)-int(Ay), int(Ay)):
					x = float(x)
					y = float(y)
					if x>=0 and x<baseMatrix.shape[0] and y>=0 and y<baseMatrix.shape[1]:
						self.__planeMap[int(x)][int(y)] = 1

	#terrain map
	def exportTerrainMap(self, path):
		tmp = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")
		tmpData = tmp.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==1:
					tmpData[x, y] = 100
				elif self.__heightMap[x][y]!=0:
					tmpData[x, y] = 200
				else:
					tmpData[x, y] = 0
		tmp.save(path)

	#synthesize
	def smoothSynthesize(self, gaussianBlurRadius):
		tmp = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")
		tmpData = tmp.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmpData[x, y] = int(self.__synthesizedMap[x][y])
		tmpData = tmp.filter(ImageFilter.GaussianBlur(radius=gaussianBlurRadius)).load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__synthesizedMap[x][y] = tmpData[x, y]

	def synthesizeNoise(self):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==0:
					self.__synthesizedMap[x][y] = self.__synthesizedMap[x][y] + self.__noiseMap[x][y]
				else:
					self.__synthesizedMap[x][y] = self.__planeMap[x][y]

	def synthesizeMountains(self):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==0:
					self.__synthesizedMap[x][y] = self.__synthesizedMap[x][y] + self.__heightMap[x][y]
				else:
					self.__synthesizedMap[x][y] = self.__planeMap[x][y]

	def synthesizePlanes(self):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==1:
					self.__synthesizedMap[x][y] = 25

	def synthesizeTree(self):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==0:
					self.__synthesizedMap[x][y] = self.__synthesizedMap[x][y] + self.__treeMap[x][y]
				else:
					self.__synthesizedMap[x][y] = self.__planeMap[x][y]
	#save
	def saveSynthesizedMap(self, path):
		image_tmp = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")
		tmp = image_tmp.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmp[x, y] = int(self.__synthesizedMap[x][y])
		image_tmp.save(path)

	def saveMountainMap(self, path):
		image_tmp = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")
		tmp = image_tmp.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmp[x, y] = int(self.__heightMap[x][y])
		image_tmp.save(path)