import math
COUNT = 8

def parseBackground(mountainlList, size):
	result = []
	for mountain in mountainlList:
		horizontalReference = []
		verticalRidge = []
		horizontalRidge = []

		for href in mountain['horizontalReference']:
			horizontalReference.append(mountain['horizontalReference'][href])
		for vr in mountain['verticalRidge']:
			verticalRidge.append(mountain['verticalRidge'][vr])
		for hr in mountain['horizontalRidge']:
			horizontalRidge.append(mountain['horizontalRidge'][hr])

		meanYHorizontalReference = 0
		radiusHorizontalReference = 0
		tmpBig = -1
		tmpSmall = 9999999999999999999999999
		tmpCount = 0
		for tmp in horizontalReference:
			for tmp2 in tmp:
				meanYHorizontalReference = meanYHorizontalReference + tmp2[1]
				tmpCount = tmpCount + 1
				if tmp2[0]>tmpBig:
					tmpBig = tmp2[0]
				if tmp2[0]<tmpSmall:
					tmpSmall = tmp2[0]
		if tmpCount!=0:
			meanYHorizontalReference = float(meanYHorizontalReference)/tmpCount
		radiusHorizontalReference = (float(tmpBig) - tmpSmall)/2
		print 'meanYHorizontalReference:', meanYHorizontalReference
		print 'radiusHorizontalReference:', radiusHorizontalReference

		verticalRidgeList = []
		for tmp in verticalRidge:
			tmp2 = sorted(tmp, key=lambda pixel: pixel[1], reverse=False)
			tmp2Step = int(len(tmp2)/COUNT)
			tmpCount = 0
			verticalRidge = []
			for tmp3 in tmp2:
				if tmpCount%tmp2Step==0:
					verticalRidge.append({	'h':float(meanYHorizontalReference-tmp3[1])/size['height'], 
											'x0':float(tmp3[0])/size['width'], 
											'y0':float(tmp3[1])/size['height'], 
											'rl':float(radiusHorizontalReference)/(size['width']*2),
											'rh':float(10)/size['width']}) 
				tmpCount = tmpCount + 1
			verticalRidgeList.append(verticalRidge)

		for verticalRidge in verticalRidgeList:
			print 'verticalRidgeList:', len(verticalRidge)
			for tmp in verticalRidge:
				result.append(tmp)

		horizontalRidgeList = []
		for tmp in horizontalRidge:
			tmp2 = sorted(tmp, key=lambda pixel: pixel[0], reverse=False)
			tmp2Step = int(len(tmp2)/COUNT)
			tmpCount = 0
			horizontalRidge = []
			for tmp3 in tmp2:
				if tmpCount%tmp2Step==0:
					horizontalRidge.append({'h':float(meanYHorizontalReference-tmp3[1])/size['height'], 
											'x0':float(tmp3[0])/size['width'], 
											'y0':float(tmp2[0][1])/size['height'], 
											'rl':float(radiusHorizontalReference)/(size['width']*2),
											'rh':float(10)/size['width']})
				tmpCount = tmpCount + 1
			horizontalRidgeList.append(horizontalRidge)

		for horizontalRidge in horizontalRidgeList:
			print 'horizontalRidgeList:', len(horizontalRidge)
			for tmp in horizontalRidge:
				result.append(tmp)

	return result