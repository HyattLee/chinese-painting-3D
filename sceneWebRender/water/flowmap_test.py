from PIL import Image

sizeX = 8
sizeY = 8
img = Image.new("RGB", (sizeX, sizeY), "white")
imgData = img.load()
for x in range(0, sizeX):
	for y in range(0, sizeY):
		imgData[x, y] = (30*x, 30*y, 0)
img.save("test.png")