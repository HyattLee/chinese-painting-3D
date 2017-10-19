#!flask/bin/python
from flask import Flask, render_template, jsonify, request
import json
import handleSketch

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

	background = handleSketch.parseBackground(data)
	return render_template('painting.html'), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)