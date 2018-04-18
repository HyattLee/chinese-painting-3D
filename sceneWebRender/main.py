#!flask/bin/python
from flask import Flask, render_template, jsonify, request
import json
import time
import handleSketch
from terrain import creator, texture, createHeightMap
from water import flowmap

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
	return render_template('index.html'), 201

@app.route("/painting", methods=['GET'])
def painting():
	index = int(request.args['paintingIndex'].encode("utf-8"))
	return render_template('painting.html', paintingIndex=index), 201

@app.route("/achieveSketch", methods=['POST'])
def achieveSketch():
	timeLogPrecision = 5 #0.001
	time_start0 = time.time()

	time_start = time.time()
	data = json.loads(request.get_data())
	time_loadData = time.time()-time_start

	time_start = time.time()
	sceneDesc = handleSketch.parseBackground(data['pixel'], data['size'])
	time_parseSketch = time.time()-time_start

	time_start = time.time()
	mountainMap = createHeightMap.createMountain(sceneDesc['size'], sceneDesc['mountain'], 200)
	time_createMountain = time.time()-time_start

	time_start = time.time()
	planeMap = createHeightMap.createPlane(sceneDesc['size'], sceneDesc['plane'], 1)
	time_createPlane = time.time()-time_start

	time_start = time.time()
	wholeMap = createHeightMap.mountainPlusPlaneWithSmooth(sceneDesc['size'], mountainMap, planeMap, 8)
	time_smooth = time.time()-time_start

	time_start = time.time()
	finalHeightmap = createHeightMap.addNoiseToMap(sceneDesc['size'], mountainMap, wholeMap, 150, 30, 3.5)
	time_createNoise = time.time()-time_start

	time_total = time.time()-time_start0
	"""
	HM.saveSynthesizedMap("/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/heightMap.png")
	"""

	#finalHeightmap = HM.getHeightMap()

	timeLog = {
		"total":round(time_total, timeLogPrecision),
		"loadData":round(time_loadData, timeLogPrecision),
		"parseSketch":round(time_parseSketch, timeLogPrecision),
		"createMountain":round(time_createMountain, timeLogPrecision),
		"createPlane":round(time_createPlane, timeLogPrecision),
		"smooth":round(time_smooth, timeLogPrecision),
		"createNoise":round(time_createNoise, timeLogPrecision)}

	inputInfoLog = {
		"width":data['size']['width'],
		"height":data['size']['height'],
		"total":data['size']['width']*data['size']['height']}

	return jsonify({'time':timeLog, 'inputInfoLog':inputInfoLog, 'heightmap':finalHeightmap})

@app.route("/scene", methods=['GET'])
def scene():
	return render_template('scene.html'), 201

@app.route("/waterflow", methods=['GET'])
def waterflow():
	return render_template('waterflow.html'), 201

@app.route("/waterDynamicSurface", methods=['GET'])
def waterDynamicSurface():
	return render_template('waterDynamicSurface.html'), 201

@app.route("/sph", methods=['GET'])
def sph():
	return render_template('sph.html'), 201

@app.route("/terrain", methods=['GET'])
def terrain():
	return render_template('terrain.html'), 201

@app.route("/parseFlowMap", methods=['POST'])
def parseFlowMap():
	flowmapXZ = request.get_data()
	flowmap.generate(json.loads(flowmapXZ))

	return jsonify({'success':True}), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)