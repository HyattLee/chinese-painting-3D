from PIL import Image

sizeX = 8
sizeY = 8
img = Image.new("RGB", (sizeX, sizeY), 
"white").convert("L")
imgData = img.load()
for x in range(0, sizeX):
	for y in range(0, sizeY):
		imgData[x, y] = 16*(x+y)
img.save("test.png")