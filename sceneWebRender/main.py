#!flask/bin/python
from flask import Flask, render_template, jsonify, request
import json
import handleSketch
from heightmap import creator

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

	background = handleSketch.parseBackground(data['pixel'], data['size'])
	
	HM = creator.heightMap("heightmap/input/ground2.png", 100)
	HM.scaleNoise(0.7)
	for mountain in background:
		HM.createMountain(mountain['x0'], mountain['y0'], mountain['rh'], mountain['rl'], mountain['h'])

	HM.scaleHeightMap(1)
	HM.synthesizeHeightMap()
	HM.gaussianSmooth(10)

	#HM.createTree(7, 1000, 1)
	#HM.synthesizeTree()

	HM.saveInImage()
	HM.saveAsHeightMap("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/heightmap/1.png")
	HM.saveAsTexture("/home/kakaiu/ThreeChinesePainting/sceneWebRender/static/texture/ground2.png")
	return render_template('painting.html'), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)