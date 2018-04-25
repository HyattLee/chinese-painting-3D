import math
COUNT = 50

def parseBackground(objectList, size):
	result = {'mountain':[], 'size':[size['width'],size['height']], 'plane':[]}##
	for obj in objectList:
		horizontalReferenceTMP = []
		verticalRidgeTMP = []
		horizontalRidgeTMP = []
		for href in obj['horizontalReference']:
			horizontalReferenceTMP.append(obj['horizontalReference'][href])
		for vr in obj['verticalRidge']:
			verticalRidgeTMP.append(obj['verticalRidge'][vr])
		for hr in obj['horizontalRidge']:
			horizontalRidgeTMP.append(obj['horizontalRidge'][hr])

		if obj['type']=='mountain':
			meanYHorizontalReference = 0
			radiusHorizontalReference = 0
			tmpBig = -1
			tmpSmall = 9999999999999999999999999
			tmpCount = 0
			for tmp in horizontalReferenceTMP:
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
			for tmp in verticalRidgeTMP:
				tmp2 = sorted(tmp, key=lambda pixel: pixel[1], reverse=False)
				tmp2Step = int(len(tmp2)/COUNT)
				tmpCount = 0
				verticalRidge = []
				for tmp3 in tmp2:
					if tmpCount%tmp2Step==0:
						verticalRidge.append({	'h':float(meanYHorizontalReference-tmp3[1])/size['height'], 
												'x0':float(tmp3[0])/size['width'], 
												'y0':(float(tmp3[1])/size['height']), 
												'rl':float(radiusHorizontalReference)/(size['width']*1.2),
												'rh':float(20)/size['width']}) 
					tmpCount = tmpCount + 1
				verticalRidgeList.append(verticalRidge)

			for verticalRidge in verticalRidgeList:
				print 'verticalRidgeList:', len(verticalRidge)
				for tmp in verticalRidge:
					result['mountain'].append(tmp)

			horizontalRidgeList = []
			for tmp in horizontalRidgeTMP:
				tmp2 = sorted(tmp, key=lambda pixel: pixel[0], reverse=False)
				tmp2Step = int(len(tmp2)/COUNT)
				tmpCount = 0
				horizontalRidge = []
				for tmp3 in tmp2:
					if tmpCount%tmp2Step==0:
						horizontalRidge.append({'h':float(meanYHorizontalReference-tmp3[1])/size['height'], 
												'x0':float(tmp3[0])/size['width'], 
												'y0':(float(tmp3[1])/size['height']/1.2), 
												'rl':float(radiusHorizontalReference)/(size['width']*1.2),
												'rh':float(20)/size['width']})
					tmpCount = tmpCount + 1
				horizontalRidgeList.append(horizontalRidge)

			for horizontalRidge in horizontalRidgeList:
				print 'horizontalRidgeList:', len(horizontalRidge)
				for tmp in horizontalRidge:
					result['mountain'].append(tmp)
		
		elif obj['type']=='plane':
			meanYHorizontalReference = 0
			tmpBig = -1
			tmpSmall = 9999999999999999999999999
			tmpCount = 0
			for tmp in horizontalReferenceTMP:
				for tmp2 in tmp:
					meanYHorizontalReference = meanYHorizontalReference + tmp2[1]
					tmpCount = tmpCount + 1
					if tmp2[0]>tmpBig:
						tmpBig = tmp2[0]
					if tmp2[0]<tmpSmall:
						tmpSmall = tmp2[0]
			if tmpCount!=0:
				meanYHorizontalReference = float(meanYHorizontalReference)/tmpCount
			radiusHorizontalReference = (float(tmpBig) - tmpSmall)
			print 'meanYHorizontalReference:', meanYHorizontalReference
			print 'spanHorizontalReference:', tmpSmall, tmpBig

			planeList = []
			for tmp in horizontalRidgeTMP:
				tmp2 = sorted(tmp, key=lambda pixel: pixel[0], reverse=False)
				tmp2Step = int(len(tmp2)/COUNT)
				tmpCount = 0
				planes = []
				for tmp3 in tmp2:
					if tmpCount%tmp2Step==0:
						planes.append({	'Ax':float(tmp3[0])/size['width'], 
										'Ay':float(max(meanYHorizontalReference, tmp3[1]))/size['height'],  ##TODO
										'Bx':float(tmp3[0])/size['width'],
										'By':float(min(meanYHorizontalReference, tmp3[1]))/size['height']})
					tmpCount = tmpCount + 1
				planeList.append(planes)

			for plane in planeList:
				print 'planeList:', len(plane)
				for tmp in plane:
					result['plane'].append(tmp)

	return result