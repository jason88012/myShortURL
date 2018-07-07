from flask import Flask, request, jsonify, redirect, abort

from .urlShortener import *

app = Flask(__name__)
app.debug = True
shortener = urlShortener()

@app.route("/shortURL", methods=['POST'])
def shorten_request():
	"""
	Get the shorten request from client.
	"""
	url = request.get_data()
	result = shortener.add_to_db(url)
	if result["State"] is "Failed":
		return jsonify(result), 400
	else:
		return jsonify(result), 200

@app.route("/specify/<specify_key>", methods=['POST'])
def specify_url_key(specify_key):
	"""
	Use user specify url_key to generate shorten url
	"""
	url = request.get_data()
	result = shortener.add_to_db(url, url_key=specify_key)
	if result["State"] is "Failed":
		return jsonify(result), 400
	else:
		return jsonify(result), 200

@app.route("/<url_key>")
def redirect_to_url(url_key):
	"""
	Check the url_key is in DB, redirect to original url.
	"""
	url = shortener.get_from_db(url_key)
	if url is None:
		return jsonify({"State": "Failed", 
						"Info": "url_key: '%s' is not in database" % (url_key)}), 404
	return redirect(url)


@app.route("/")
def main():
	return jsonify("Test")

if __name__ == '__main__':
	# Test with Flask development server
	app.run(host='127.0.0.1', port=8080)