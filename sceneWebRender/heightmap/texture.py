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

	hmContour.save("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_contour.png")
	hm = hmContour.filter(ImageFilter.GaussianBlur(radius=5))
	hm = ImageOps.invert(hm).convert("RGB")
	hm.save(outputTexturePath)