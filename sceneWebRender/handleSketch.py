def getBox(data):
	tmpH = -1
	tmpL = 99999999999999999
	tmpLA = 99999999999999999 #small
	tmpLB = -1 #large
	for pixel in data:
		if pixel[1]<tmpL:
			tmpL = pixel[1]
		if pixel[1]>tmpH:
			tmpH = pixel[1]
		if pixel[0]<tmpLA:
			tmpLA = pixel[0]
		if pixel[0]>tmpLB:
			tmpLB = pixel[0]
	print tmpLB, tmpLA;
	print tmpL, tmpH;
	return {'h_low':tmpL, 'h_high':tmpH, 'r_low':float((tmpLB-tmpLA)/2), 'r_high':1}

def parseBackground(data):
	result = dict()
	i = 0
	for key in data:
		result[i] = getBox(data[key])
		i = i + 1
	return result