from PIL import Image, ImageOps, ImageFilter

class heightMap:
	__noiseMap = []
	__heightMap = []
	__planeMap = []
	__synthesizedMap = []
	__image = None
	__sizeX = None
	__sizeY = None

	def __init__(self, noiseImagePath):
		tmp = Image.open(noiseImagePath).convert("L")
		tmpPixel = tmp.load()
		self.__sizeX = tmp.size[0]
		self.__sizeY = tmp.size[1]
		for x in range(0, self.__sizeX):
			self.__heightMap.append([])
			self.__noiseMap.append([])
			self.__planeMap.append([])
			for y in range(0, self.__sizeY):
				self.__heightMap[x].append(0)
				self.__noiseMap[x].append(tmpPixel[x, y])
				self.__planeMap[x].append(0)

		self.__image = Image.new("RGB", (self.__sizeX, self.__sizeY), "white").convert("L")


	#plane map:
	def setCircleElement(self, x0, y0, r, h):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if (x-x0)*(x-x0)+(y-y0)*(y-y0)<r*r:
					self.__planeMap[x][y] = int(h)

	#noise map
	def scaleNoise(self, scaleRate):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__noiseMap[x][y] = int(self.__noiseMap[x][y]*scaleRate)



	#height map
	def scaleHeightMap(self, scaleRate):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				self.__heightMap[x][y] = int(self.__heightMap[x][y]*scaleRate)

	def addCircleElement(self, x0, y0, r, h=1):
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				if (x-x0)*(x-x0)+(y-y0)*(y-y0)<r*r:
					self.__heightMap[x][y] = int(self.__heightMap[x][y] + h)


	#height map advance
	def createMountain(self, x0, y0, rh, rl, h):
		for tmpH in range(0, h):
			tmpR = (float(h-tmpH)/h)*(rl-rh)+rh
			self.addCircleElement(x0, y0, tmpR, 1)

	def createPlane(self, x0, y0, r):
		self.setCircleElement(x0, y0, r, 1)

	def synthesize(self):
		for x in range(0, self.__sizeX):
			self.__synthesizedMap.append([])
			for y in range(0, self.__sizeY):
				if self.__planeMap[x][y]==0:
					self.__synthesizedMap[x].append(self.__noiseMap[x][y] + self.__heightMap[x][y])
				else:
					self.__synthesizedMap[x].append(self.__planeMap[x][y])

	def saveInImage(self):
		tmp = self.__image.load()
		for x in range(0, self.__sizeX):
			for y in range(0, self.__sizeY):
				tmp[x, y] = self.__synthesizedMap[x][y]

	def saveAsHeightMap(self, path):
		self.__image.filter(ImageFilter.GaussianBlur(radius=4)).save(path)

	def saveAsTexture(self, path):
		inverted_image = ImageOps.invert(self.__image)
		inverted_image.filter(ImageFilter.GaussianBlur(radius=4)).save(path)


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