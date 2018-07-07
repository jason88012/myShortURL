import redis
import urllib.parse as parse
import hashlib
import base62

from .conf import *

def short(url):
	# MD5 hash and take first 40bit encdoe with base62
	return base62.encodebytes(hashlib.md5(url).digest()[-5:])

def check_url(url):
	# Check with too long string or missed protocol
	if (len(url) > MAX_URL_LEN):
		return {"State":"Failed", 
				"Error_msg":"Please don't use url longer than 2000 character."}
	parsed_url = parse.urlparse(url.decode())
	if parsed_url.scheme == '':
		return {"State":"Failed", 
				"Error_msg":"Please use correct protocol such as 'http', 'https' or 'ftp'."}
	return True

def check_url_loop(url_key, url):
	parsed_url = parse.urlparse(url.decode())
	url_path = parsed_url.path.replace("/", "")
	server_domain = SERVER_URL_PREFIX.replace(":", "").replace("/", "")
	if ( server_domain == parsed_url.scheme+parsed_url.netloc and url_path == url_key):
		return {"State":"Failed", 
				"Error_msg":"This url %s will redirect to same page" % (SERVER_URL_PREFIX+url_key)}
	return {"State":"Sucess"}

class urlShortener():
	def __init__(self):
		self.db = redis.Redis(host='localhost', db=0)

	def set_to_db(self, url_key, url):
		if not self.in_db(url_key):
			try:
				self.db.set(url_key, url)
				return {"State":"Sucess"}
			except:
				return {"State":"Failed", 
						"Error_msg": "Insert to database failed"}
		else:
			if self.check_collision(url_key, url):
				try:
					self.db.set(url_key, url)
					return {"State":"Sucess"}
				except:
					return {"State":"Failed", 
							"Error_msg": "Insert to database failed"}
		return {"State":"Sucess"}

	def in_db(self, url_key):
		if self.db.get(url_key) is None:
			return False
		return True

	def check_collision(self, url_key, url):
		assert self.db.get(url_key) is not None
		if self.db.get(url_key) != url:
			return True
		return False

	def add_to_db(self, url, url_key=None):
		check_url_result = check_url(url)
		if check_url_result is not True:
			return {"State":"Failed", 
					"Error_msg": check_url_result["Error_msg"]}

		# No specify url_key
		if url_key is None:
			url_key = short(url)
			res = self.set_to_db(url_key, url)
			if res["State"] is not "Sucess":
				return res
		# Specify key
		else:
			if self.in_db(url_key):				# If the given key has been used, generate another key
				new_key = short(url)
				res = self.set_to_db(new_key, url)
				if res["State"] is not "Sucess":
					return res
				return {"State":"Sucess", 
						"Info": "The url_key %s is not available, but we generate another key %s for you." % (url_key, new_key), 
						"short_url":"%s" % (SERVER_URL_PREFIX+new_key)}
			else:
				chk_url = check_url_loop(url_key, url)
				if chk_url["State"] is not "Sucess":
					return chk_url
				res = self.set_to_db(url_key, url)
				if res["State"] is not "Sucess":
					return res

		return {"State":"Sucess", 
				"short_url":"%s" % (SERVER_URL_PREFIX+url_key)}

	def get_from_db(self, url_key):
		"""
		Check the given url_key is in database or not
		"""
		return self.db.get(url_key)
 