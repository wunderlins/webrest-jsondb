#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interface

db = new jsonndb("file.json")

data = db.get("a/b")
  -> throw ExceptionNotFound if element does not exist

db.set("a/b", value)
	-> create intermediate elements if they do not exist

db.delete("a/b")
  -> raise ExceptionNotFound if element does not exist

db.commit()
	- lock file 
	- store
	- unlock

TODO: might add a feature to traverse list elements

2016, Simon Wunderlin
"""

import sys, os, json
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'portalocker-0.5.7'))
from portalocker import *

class ExceptionNotFound(Exception):
	pass

class jsondb(object):
	__data  = None
	__dirty = False
	__path  = None
	
	def __cleanpath(self, path):
		if len(path) > 0 and path[-1] == "/":
			path = path[0:-1]
		return path		
	
	def __init__(self, path):
		self.__path = path
		f = open(path, 'rb')
		self.__data = json.load(f)
		f.close()
	
	def __exists(self, path):
		path = self.__cleanpath(path)
	
		# root node always exists
		if not path:
			return True
		
		# loop over all parts in path
		apath = path.split('/')
		node = self.__data
		for e in apath:
			if e not in node.keys():
				return False
			node = node[e]
		
		return True
	
	def get(self, path):
		path = self.__cleanpath(path)
		
		if not path:
			return self.__data
		
		if not self.__exists(path):
			raise ExceptionNotFound("Element "+path+" not found in " + self.__path)
		
		# FIXME: two loops for lookup is inefficient
		#        loop over all parts in path
		apath = path.split('/')
		node = self.__data
		for e in apath:
			node = node[e]
		
		return node
		
	def set(self, path, data):
		path = self.__cleanpath(path)
		
		if not path:
			self.__data = data
			return

		node = self.__data
		if self.__exists(path):
			apath = path.split('/')
			for e in apath[0:-1]:
				node = node[e]
			node[apath[-1]] = data
			return
		
		# TODO: ceate intermediate nodes
		
	def delete(self, path):
		raise Exception("Not implemented")

	def commit(self):
		if self.__dirty:
			return
		
		raise Exception("Not implemented")

if __name__ == "__main__":
	"""Testing """
	
	# create a test file
	f = 'testdb.json'
	data = '{"a": {"b": 1, "c": 2, "d": [1,2,3]}}'
	fd = open(f, 'w')
	fd.write(data)
	fd.close()
	
	# open db
	db = jsondb(f)
	
	# check if an element exists
	""" disable checks, existst renamed to __exists
	assert db.exists("") == True
	assert db.exists("a/b") == True
	assert db.exists("a/e") == False
	"""
	
	assert db.get("/") == {"a": {"b": 1, "c": 2, "d": [1,2,3]}}
	assert db.get("") == {"a": {"b": 1, "c": 2, "d": [1,2,3]}}
	assert db.get("a/b") == 1
	assert db.get("a") == {"b": 1, "c": 2, "d": [1,2,3]}
	assert db.get("a/") == {"b": 1, "c": 2, "d": [1,2,3]}
	
	assert db.set("a/b", 15) == None
	assert db.get("") == {"a": {"b": 15, "c": 2, "d": [1,2,3]}}
	assert db.set("", {"a": 12}) == None
	assert db.get("") == {"a": 12}
	

