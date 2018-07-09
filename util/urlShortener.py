import redis
import urllib.parse as parse
import hashlib
import base62

from .conf import *

def short(url):
	# MD5 hash and take first 40bit encdoe with base62
	return base62.encodebytes(hashlib.md5(url).digest()[-5:])

def check_url_avail(url):
	# Check with too long string or missed protocol
	if (len(url) > MAX_URL_LEN):
		return {"State":"Failed", 
				"Error_msg":"Please don't use url longer than 2000 character."}
	parsed_url = parse.urlparse(url.decode())
	if parsed_url.scheme == '':
		return {"State":"Failed", 
				"Error_msg":"Please use correct protocol such as 'http', 'https' or 'ftp'."}
	return {"State":"Success"}

def check_url_loop(url_key, url):
	parsed_url = parse.urlparse(url.decode())
	url_path = parsed_url.path.replace("/", "")
	server_domain = SERVER_URL_PREFIX.replace(":", "").replace("/", "")
	if ( server_domain == parsed_url.scheme+parsed_url.netloc and url_path == url_key):
		return {"State":"Failed", 
				"Error_msg":"This url %s will redirect to same page" % (SERVER_URL_PREFIX+url_key)}
	return {"State":"Success"}

class urlShortener():
	def __init__(self):
		self.db = redis.Redis(host='localhost', db=0)

	def get_from_db(self, url_key):
		"""
		Check the given url_key is in database or not
		"""
		return self.db.get(url_key)

	def set_to_db(self, url_key, url):
		"""
		Set the given key-val to db, if failed return error message.
		"""
		try:
			self.db.set(url_key, url)
			return {"State":"Success"}
		except:
			return {"State":"Failed", 
					"Error_msg": "Insert to database failed"}

	def is_collision(self, url_key, url):
		"""
		Check if the given url_key has collision
		"""
		assert self.db.get(url_key) is not None
		if self.db.get(url_key) != url:
			return True
		return False

	def use_rand_key(self, url):
		"""
		The work flow of general usage.
		"""

		# In general mode, generate the relative key first.
		url_key = short(url)

		# Check if the generated key has been used
		if self.get_from_db(url_key) is not None:
			# key is in db, check collision
			if self.is_collision(url_key, url):
				# collision, insert it and replace the old one.
				set_res = self.set_to_db(url_key, url)
				if set_res["State"] != "Success":
					return set_res
		else:
			# key is not in db, insert it.
			set_res = self.set_to_db(url_key, url)
			if set_res["State"] != "Success":
				return set_res

		return {"State":"Sucess", 
				"short_url":"%s" % (SERVER_URL_PREFIX+url_key)} 

	def use_spec_key(self, url, spec_key):
		"""
		The work flow of specify key usage.
		"""

		# In specify mode, check loop condition first.
		chk_loop_res = check_url_loop(spec_key, url)
		if chk_loop_res["State"] != "Success":
			return chk_loop_res

		# Check if the given key has been used
		get_res = self.get_from_db(spec_key)
		if get_res is not None:
			# Given key has been used, check if the key has same url
			if get_res != url:
				# Not same, generate another key for it.
				res = self.use_rand_key(url)
				res["Info"] = "The given key %s is not avaiable, but we generate another usable key for you." % (spec_key)
				return res
		else:
			# Given key hasn't been used, insert it.
			set_res = self.set_to_db(spec_key, url)
			if set_res["State"] != "Success":
				return set_res

		return {"State":"Success", 
				"short_url":"%s" % (SERVER_URL_PREFIX+spec_key)} 

