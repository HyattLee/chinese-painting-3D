#!flask/bin/python
from flask import Flask, render_template, jsonify, request
import json
import handleSketch
from terrain import creator, texture

app = Flask(__name__)

@app.route("/scene", methods=['GET'])
def scene():
	return render_template('scene.html'), 201

@app.route("/painting", methods=['GET'])
def painting():
	return render_template('painting.html'), 201

@app.route("/achieveSketch", methods=['POST'])
def achieveSketch():
	data = None
	for key in request.form:
		data = json.loads(key)

	sceneDesc = handleSketch.parseBackground(data['pixel'], data['size'])
	
	HM = creator.heightMap(sceneDesc['size'])
	HM.createMountains(sceneDesc['mountain'])
	HM.adjustMountains(upperBound=200)
	HM.saveMountainMap("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_mountain.png")
	HM.synthesizeMountains()

	HM.createPlanes(sceneDesc['plane'])
	HM.synthesizePlanes()
	HM.exportTerrainMap("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_terrain.png")

	HM.smoothSynthesize(10)
	
	HM.createNoiseForMountains(100, 30)
	HM.smoothNoise(3.5)
	HM.synthesizeNoise()

	#HM.createTree(7, 1000, 1)
	#HM.synthesizeTree()

	HM.saveSynthesizedMap("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/heightMap.png")
	texture.generateTextureForTerrain("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_mountain.png",
										"/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/tmp_terrain.png",
										"/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/terrain/texture.png")
	return render_template('painting.html'), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)