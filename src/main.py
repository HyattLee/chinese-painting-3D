#!flask/bin/python
from flask import Flask, render_template, jsonify, request
import json
import time
import handleSketch
from terrain import createHeightMap
from water import createFlowMap

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

	return jsonify({'time':timeLog, 'inputInfoLog':inputInfoLog, 'heightmap':finalHeightmap}), 201

@app.route("/parseFlowMap", methods=['POST'])
def parseFlowMap():
	timeLogPrecision = 5 #0.001
	time_start0 = time.time()

	time_start = time.time()
	data = json.loads(request.get_data())
	time_loadData = time.time() - time_start

	time_start = time.time()
	flowMap = createFlowMap.createFlowMap(data)
	time_createFlowMap = time.time() - time_start

	time_start = time.time()
	finalFlowMap = createFlowMap.smoothFlowMap(flowMap, 3)
	time_smooth = time.time() - time_start

	time_total = time.time()-time_start0

	timeLog = {
		"total":round(time_total, timeLogPrecision),
		"loadData":round(time_loadData, timeLogPrecision),
		"createFlowMap":round(time_createFlowMap, timeLogPrecision),
		"smooth":round(time_smooth, timeLogPrecision)}

	inputInfoLog = {
		"width":len(data),
		"height":len(data[0]),
		"total":len(data)*len(data[0])}

	return jsonify({'time':timeLog, 'inputInfoLog':inputInfoLog, 'flowmap':finalFlowMap}), 201


@app.route("/waterFlowCreator", methods=['GET'])
def waterFlowCreator():
	return render_template('waterFlowCreator.html'), 201


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

@app.route("/drawLineIn3D", methods=['GET'])
def drawLineIn3D():
	return render_template('interactiveDraw3DLine.html'), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)