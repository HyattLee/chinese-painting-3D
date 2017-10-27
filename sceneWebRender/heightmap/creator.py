from PIL import Image, ImageOps, ImageFilter
import random, copy

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

	def __init__(self, baseImagePath, randomMax):
		tmp = Image.open(baseImagePath).convert("L")
		tmpPixel = tmp.load()
		self.__sizeX = tmp.size[0]
		self.__sizeY = tmp.size[1]
		self.__randomMax = randomMax
		for x in range(0, self.__sizeX):
			self.__heightMap.append([])
			self.__noiseMap.append([])
			self.__planeMap.append([])
			self.__treeMap.append([])
			self.__synthesizedMap.append([])
			for y in range(0, self.__sizeY):
				self.__heightMap[x].append(0)
				self.__noiseMap[x].append(random.uniform(0, randomMax))
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

	#noise map
	def scaleNoise(self, scaleRate):
		self.__randomScale = scaleRate
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__noiseMap[x][y] = self.__noiseMap[x][y]*scaleRate

	#height map
	def scaleHeightMap(self, scaleRate):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__heightMap[x][y] = self.__heightMap[x][y]*scaleRate

	def addCircleElement(self, x0, y0, r, hc, heightmap0):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if (x-x0)*(x-x0)+(y-y0)*(y-y0)<r*r and hc>heightmap0[x][y]:
					self.__heightMap[x][y] = self.__heightMap[x][y] + 1

	#tree map
	def createTree(self, intensity, topLine, rare):
		count = 0
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if self.__heightMap[x][y]>self.__randomMax*self.__randomScale*0.3 and count%(rare)==0:
					self.__treeMap[x][y] = (random.uniform(0, intensity))
				count = count + 1

	#height map advance
	def createMountain(self, x0, y0, rh, rl, h):
		heightmap0 = copy.deepcopy(self.__heightMap)
		for tmpH in range(0, int(h*255)):
			tmpR = (float(h-(float(tmpH)/255))/h)*(rl-rh)+rh
			print tmpR*self.__sizeX
			self.addCircleElement(x0*self.__sizeX, y0*self.__sizeY, tmpR*self.__sizeX, tmpH, heightmap0)

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