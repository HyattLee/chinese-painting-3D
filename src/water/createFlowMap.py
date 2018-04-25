from PIL import Image, ImageOps, ImageFilter
import random, copy
import math

def initZeroMap(size):
	dataMap = []
	for x in range(0, size[0]):
		dataMap.append([])
		for y in range(0, size[1]):
			dataMap[x].append([0, 0, 0])
	return dataMap

def createFlowMap(flowmapXZ):
	fm = initZeroMap([len(flowmapXZ), len(flowmapXZ[0])])
	for x in range(0, len(flowmapXZ)):
		for z in range(0, len(flowmapXZ[0])):
			fm[x][z] = (flowmapXZ[x][z][0], flowmapXZ[x][z][1], 0)
	return fm

def smoothFlowMap(flowmap, blurR):
	image_tmp = Image.new("RGB", (len(flowmap), len(flowmap[0])), (0,0,0))
	tmp = image_tmp.load()
	for x in range(0, len(flowmap)):
		for z in range(0, len(flowmap[0])):
				tmp[x, z] = (min(int(-flowmap[x][z][0]*128+128), 255), 
							 min(int(-flowmap[x][z][1]*128+128), 255), 
							 min(int(-flowmap[x][z][2]*128+128), 255)) 

	result = initZeroMap([len(flowmap), len(flowmap[0])])
	tmp2 = image_tmp.filter(ImageFilter.GaussianBlur(radius=blurR)).load()
	for x in range(0, len(flowmap)):
		for z in range(0, len(flowmap[0])):
			result[x][z] = tmp2[x, z]
	return result
