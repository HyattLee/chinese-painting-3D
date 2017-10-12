#!flask/bin/python
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/scene", methods=['GET'])
def scene():
	return render_template('scene.html'), 201

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5000)