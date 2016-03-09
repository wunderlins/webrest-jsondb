#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

REST example with json/xml/txt and html output. The output is controlled 
by the http Accept request header

Example:
curl -iH "Accept: application/json" localhost:8082/a/b/c
curl -iH "Accept: text/xml" localhost:8082/a/b/c
curl -iH "Accept: text/html" localhost:8082/a/b/c
curl -iH "Accept: text/plain" localhost:8082/a/b/c

Using a different method:
curl -XDELETE  -iH "Accept: text/xml" localhost:8082/a/b/c

if the Accept header is missing, json is the default.

"""

import sys, os

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'web.py-0.37'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'python-mimeparse-1.5.1'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'mimerender-master', 'src'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'dicttoxml-1.6.6'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'jsondatabase-0.1.1'))

try:
	import simplejson as json
except ImportError:
	import json
import pprint
import mimerender
import web
import dicttoxml
from xml.dom.minidom import parseString

mimerender = mimerender.WebPyMimeRender()

urls = (
	'/test',    'test',
	'/db/(.*)', 'db'
)

class wsgiapp(web.application):
	def run(self, port=8080, ip='127.0.0.1', *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, (ip, port))

class renderer(object):
	@staticmethod
	def dict2xml(d):
		return parseString(dicttoxml.dicttoxml(d, \
		                   custom_root="root")).toprettyxml()
	
	@staticmethod
	def dict2json(d):
		return json.dumps(d)
	
	@staticmethod
	def dict2txt(d):
		pp = pprint.PrettyPrinter(indent=4, width=1)
		return pp.pformat(d)
	
	@staticmethod
	def dict2html(d):
		buffer = '<table border="1" style="border-collapse: collapse;"><tbody>'
		for e in d:
			
			# handle lists
			if type(e) is list: # or type(d[e]) is list:
				for el in e:
					buffer += "<tr><td>" + str(el) + "</td><td>"
				buffer += '</tbody></table>'
				return buffer
					
			# handle dicts
			buffer += "<tr><td>" + str(e) + "</td><td>"
			if type(d[e]) is dict: # or type(d[e]) is list:
				buffer += renderer.dict2html(d[e])
			elif type(d[e]) is dict: # or type(d[e]) is list:
				buffer += renderer.dict2html(d[e])
			else:
				buffer += str(d[e])
			#buffer += "</td></tr>"
		buffer += '</tbody></table>'
	
		return buffer

class test:
	def GET (self):
		render = web.template.render('template')
		return render.test()

class NotFoundException(Exception):
	pass

class db:
	render_xml  = lambda **args: renderer.dict2xml(args)
	render_json = lambda **args: renderer.dict2json(args)
	render_html = lambda **args: '<!DOCTYPE html>\n<html>\n<body>\n' + \
	                             renderer.dict2html(args) + "\n</body>\n</html>"
	render_txt  = lambda **args: renderer.dict2txt(args)
	
	@staticmethod
	def _getdb():
		from jsondb.db import Database
		return Database("data.json")
	
	@staticmethod
	def _location(location):
		# sanitize path
		location = location.replace("../", "")
		# remove trailing slash
		if location[-1:] == "/":
			location = location[0:-1]
		# split path
		aloc = location.split("/")
		
		return (location, aloc)
	
	@staticmethod
	def _fetch(aloc, db):
		ret = db
		try:
			for e in aloc:
				if type(ret) == list:
					ret = ret[int(e)]
				else:
					ret = ret[e]
		except:
			raise NotFoundException("Crikey!")
		
		return ret
	
	@mimerender(
		default = 'json',
		json = render_json,
		xml  = render_xml,
		#html = render_html,
		txt  = render_txt
	)
	def GET(self, name):
		location, aloc = self._location(name)
		db = self._getdb()
		
		# handle root node
		if not location:
			ret = {}
			for e in db:
				ret[e] = db[e]
			return ret
		
		# handle sub nodes
		ret = None
		try:
			ret = self._fetch(aloc, db)
		except NotFoundException as e:
			details = e.args[0]
			raise web.notfound()
		
		return {"data": ret}

	@mimerender(
		default = 'json',
		json = render_json,
		xml  = render_xml,
		#html = render_html,
		txt  = render_txt
	)
	def POST(self, location):
		location, aloc = self._location(name)
		db = self._getdb()
		
		pass

if __name__ == "__main__":
	web.config.debug = True
	app = wsgiapp(urls, globals())
	app.run(port=8083)
	
