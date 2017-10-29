from PIL import Image, ImageOps, ImageFilter
import random, copy
import numba, numpy, math

@numba.jit
def accelerate_createMountains(matrix, sizeX, sizeY):
	baseMatrix = numpy.zeros((sizeX, sizeY))
	for mountain in mountainsDescription:
		print 'create a mountain'
		x0 = mountain['x0']*sizeX
		y0 = mountain['y0']*sizeY
		rl = mountain['rl']*sizeX
		rh = mountain['rh']*sizeX
		h = mountain['h']*sizeY

		for x in range(int(x0-rl), int(x0+rl)):
			for y in range(int(y0-rl), int(y0+rl)):
				x = float(x)
				y = float(y)
				if x>=0 and x<=baseMatrix.shape[1] and y>=0 and y<=baseMatrix.shape[0]:
					delta = math.sqrt((x-x0)*(x-x0)+(y-y0)*(y-y0))
					h_tmp = 0
					if delta>rh:
						h_tmp = h - (((delta-rh)*h)/(rl-rh))*h
					else:
						h_tmp = h
					if h_tmp>baseMatrix[int(x), int(y)]:
						baseMatrix[int(x), int(y)] = h_tmp

	for x in range(0, sizeX):
		for y in range(0, sizeY):
			matrix = matrix + baseMatrix[int(x), int(y)]
			
	return matrix

class heightMap:
	__noiseMap = []
	__heightMap = []
	__planeMap = []
	__treeMap = []
	__synthesizedMap = []
	__image = None
	__sizeX = None
	__sizeY = None
	__randomMax = 0
	__randomScale = 1

	def __init__(self, size, randomMax):
		self.__sizeX = int(size[0])
		self.__sizeY = int(size[1])
		self.__randomMax = randomMax
		for x in range(0, self.__sizeX):
			self.__heightMap.append([])
			self.__noiseMap.append([])
			self.__planeMap.append([])
			self.__treeMap.append([])
			self.__synthesizedMap.append([])
			for y in range(0, self.__sizeY):
				self.__heightMap[x].append(0)
				self.__noiseMap[x].append(0) #random.uniform(0, randomMax)
				self.__planeMap[x].append(0)
				self.__treeMap[x].append(0)
				self.__synthesizedMap[x].append(0)

		self.__image = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")

	#plane map:
	def setCircleElement(self, x0, y0, r, h):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if (x-x0)*(x-x0)+(y-y0)*(y-y0)<r*r:
					self.__planeMap[x][y] = int(h)
	#tree map
	def createTree(self, intensity, topLine, rare):
		count = 0
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__heightMap[x][y]>self.__randomMax*self.__randomScale*0.3 and count%(rare)==0:
					self.__treeMap[x][y] = (random.uniform(0, intensity))
				count = count + 1

	#height map advance
	def scaleMountains(self, scaleRate):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__heightMap[x][y] = self.__heightMap[x][y]*scaleRate

	def createMountains(self, mountainsDescription):
		baseMatrix = numpy.zeros((self.__sizeX, self.__sizeY))
		for mountain in mountainsDescription:
			print 'create a mountain'
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
			
	def createPlane(self, x0, y0, r):
		self.setCircleElement(x0*self.__sizeX, y0*self.__sizeY, r*self.__sizeX, 1)

	def synthesizeHeightMap(self):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==0:
					self.__synthesizedMap[x][y] = self.__synthesizedMap[x][y] + self.__noiseMap[x][y] + self.__heightMap[x][y]
				else:
					self.__synthesizedMap[x][y] = self.__planeMap[x][y]

	def synthesizeTree(self):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==0:
					self.__synthesizedMap[x][y] = self.__synthesizedMap[x][y] + self.__treeMap[x][y]
				else:
					self.__synthesizedMap[x][y] = self.__planeMap[x][y]

	def gaussianSmooth(self, gaussianBlurRadius):
		tmp = self.__image.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmp[x, y] = int(self.__synthesizedMap[x][y])
		self.__image = self.__image.filter(ImageFilter.GaussianBlur(radius=gaussianBlurRadius))
		tmp = self.__image.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__synthesizedMap[x][y] = tmp[x, y]

	def saveInImage(self):
		tmp = self.__image.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmp[x, y] = int(self.__synthesizedMap[x][y])

	def saveAsHeightMap(self, path):
		self.__image.save(path)

	def saveAsTexture(self, path):
		inverted_image = ImageOps.invert(self.__image).convert("RGB")
		green_image = Image.new("RGB", (self.__sizeX, self.__sizeY), "green")
		textureImage = Image.blend(inverted_image, green_image, 0.3)
		textureImage.save(path)

"""
HM = heightMap("input/ground2.png")
HM.scaleNoise(0.4)

HM.createMountain(100, 0, 5, 100, 14)
HM.createMountain(200, 0, 5, 200, 14)
HM.createMountain(200, 250, 5, 100, 7)
HM.createMountain(320, 250, 5, 100, 15)
HM.createMountain(460, 250, 5, 100, 24)
HM.scaleHeightMap(8)

HM.createPlane(0, 400, 100)
HM.createPlane(100, 400, 100)
HM.createPlane(200, 400, 100)
HM.createPlane(300, 400, 100)
HM.createPlane(400, 400, 100)
HM.createPlane(500, 400, 100)

HM.synthesize()
HM.saveInImage()
HM.saveAsHeightMap("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/heightmap/1.png")
HM.saveAsTexture("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/texture/ground2.png")
"""