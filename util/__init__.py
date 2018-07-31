from flask import Flask, request, jsonify, redirect, abort

from .urlShortener import urlShortener, check_url_avail

app = Flask(__name__)
app.debug = True
shortener = urlShortener()

@app.route("/shortURL", methods=['POST'])
def shorten_request():
	"""
	Get the shorten request from client.
	"""
	url = request.get_data()
	chk_url_res = check_url_avail(url)
	if chk_url_res["State"] != "Success":
		return jsonify(chk_url_res)

	result = shortener.use_rand_key(url)
	if result["State"] != "Success":
		return jsonify(result), 400
	return jsonify(result), 200

@app.route("/specify/<specify_key>", methods=['POST'])
def specify_url_key(specify_key):
	"""
	Use user specify url_key to generate shorten url
	"""
	url = request.get_data()
	chk_url_res = check_url_avail(url)
	if chk_url_res["State"] != "Success":
		return jsonify(chk_url_res)

	result = shortener.use_spec_key(url, specify_key)
	if result["State"] != "Success":
		return jsonify(result), 400
	return jsonify(result), 200

@app.route("delete/<key>", methods=['POST'])
def remove_key(key):
	"""
	remove existed key
	"""
	if shortener.get_from_db(key) is None:
		return jsonify({"State":"Failed", 
						"Error_msg":"No such key in database"})
	else:
		result = shortener.rm_from_db(key)
		return jsonify(result)

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
	"""
	Guide page
	"""
	return "A short url api service."
"""
if __name__ == '__main__':
	# Test with Flask development server
	app.run(host='127.0.0.1', port=8080)
"""