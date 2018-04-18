#!flask/bin/python
from flask import Flask, render_template, jsonify, request
import json
import handleSketch
from terrain import creator, texture
from water import flowmap

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
	return render_template('index.html'), 201

@app.route("/scene", methods=['GET'])
def scene():
	return render_template('scene.html'), 201

@app.route("/painting", methods=['GET'])
def painting():
	index = int(request.args['paintingIndex'].encode("utf-8"))
	return render_template('painting.html', paintingIndex=index), 201

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

@app.route("/achieveSketch", methods=['POST'])
def achieveSketch():
	data = json.loads(request.get_data())
	print data

	sceneDesc = handleSketch.parseBackground(data['pixel'], data['size'])
	
	HM = creator.heightMap(sceneDesc['size'])
	HM.createMountains(sceneDesc['mountain'])
	HM.adjustMountains(upperBound=200)
	HM.saveMountainMap("/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/tmp_mountain.png")
	HM.synthesizeMountains()

	HM.createPlanes(sceneDesc['plane'])
	HM.synthesizePlanes()
	HM.exportTerrainMap("/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/tmp_terrain.png")

	HM.smoothSynthesize(8)

	HM.createNoiseForMountains(150, 30) 
	HM.smoothNoise(3.5)#2,3.5,5
	HM.synthesizeNoise()

	#HM.createTree(7, 1000, 1)
	#HM.synthesizeTree()

	HM.saveSynthesizedMap("/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/heightMap.png")
	#texture.generateTextureForTerrain("/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/tmp_mountain.png",
										#"/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/tmp_terrain.png",
										#"/home/kakaiu/chinese-painting-3D/sceneWebRender/static/terrain/texture.png")
	return render_template('painting.html'), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)