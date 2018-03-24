from PIL import Image, ImageEnhance, ImageFilter, ImageOps

hm = Image.open("/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/heightMap.png")
#hm = ImageOps.invert(hm)
colorTData = hm.load()
for x in range(0, hm.size[0]):
	for y in range(0, hm.size[1]):
		colorTData[x, y] = 255

hm.save("test_texture.png")