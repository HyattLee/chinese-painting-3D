from PIL import Image, ImageEnhance, ImageFilter, ImageOps

def generateTextureForTerrain(terrainHeightMapPath, terrainTypePath, outputTexturePath):
	hm = Image.open(terrainHeightMapPath)
	tim = Image.open(terrainTypePath)
	size = hm.size

	hmContour = hm.filter(ImageFilter.CONTOUR)
	hmContourData = hmContour.load()
	timData = tim.load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			if hmContourData[x, y]<255:
				hmContourData[x, y] = 0
			if timData[x, y]!=200:
				hmContourData[x, y] = 0

	colorT = tim.convert("RGB")
	colorTData = colorT.load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			if colorTData[x, y][0]==200:
				colorTData[x, y] = (194,216,213)
			if colorTData[x, y][0]==100:
				colorTData[x, y] = (194,216,213)

	colorT.save("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_color.png")

	hmContour.save("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_contour.png")
	hm = hmContour.filter(ImageFilter.GaussianBlur(radius=5))
	hm.save("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_filter.png")
	hm = ImageOps.invert(hm)
	hm.save("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_invert.png")
	hmData = hm.load()
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			hmData[x, y] = int(hmData[x, y])

	hm = hm.convert("RGB")
	hmData = hm.load()
	hmContour.save("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_black.png")

	colorRate = 0.9
	for x in range(0, size[0]):
		for y in range(0, size[1]):
			if hmData[x, y][0]>40:
				if colorTData[x, y][0]!=0:
					hmData[x, y] = (int((1-colorRate)*hmData[x, y][0]+colorRate*colorTData[x, y][0]), 
									int((1-colorRate)*hmData[x, y][1]+colorRate*colorTData[x, y][1]), 
									int((1-colorRate)*hmData[x, y][2]+colorRate*colorTData[x, y][2]))


	hm = hm.filter(ImageFilter.GaussianBlur(radius=5))		

	hm.save(outputTexturePath)