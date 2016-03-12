#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simple json file access with exclusive locking during write

Interface
db = new jsonndb("file.json")

data = db.get("a/b")
  -> throw ExceptionNotFound if element does not exist

db.set(jsondata)
	-> this method will alway overwire all data

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
	
	def __init__(self, path):
		self.__path = path
		f = open(path, 'rb')
		self.__data = json.load(f)
		f.close()
	
	def __cleanpath(self, path):
		if len(path) > 0 and path[-1] == "/":
			path = path[0:-1]
		return path		
	
	def exists(self, path):
		path = self.__cleanpath(path)
	
		# root node always exists
		if not path:
			return True
		
		# loop over all parts in path
		#print path
		apath = path.split('/')
		node = self.__data
		for e in apath:
			try:
				if e not in node.keys():
					return False
			except AttributeError, e:
				return False
				
			node = node[e]
		
		return True
	
	def get(self, path):
		path = self.__cleanpath(path)
		
		if not path:
			return self.__data
		
		if not self.exists(path):
			raise ExceptionNotFound("Element "+path+" not found in " + self.__path)
		
		# FIXME: two loops for lookup is inefficient
		#        loop over all parts in path
		apath = path.split('/')
		node = self.__data
		for e in apath:
			node = node[e]
		
		return node
	
	def is_dirty(self):
		return self.__dirty
	
	def set(self, data):
		self.__dirty = True
		self.__data = data
		
	def commit(self):
		if self.__dirty == False:
			return
		
		# import only on write, we expect most operations to be read operations
		import portalocker
		file = open(self.__path, 'wb')
		portalocker.lock(file, portalocker.LOCK_EX)
		json.dump(self.__data, file)
		file.close()

if __name__ == "__main__":
	"""Testing """
	
	# create a test file
	f = 'testdb.json'
	data = '{"a": {"b": 1, "c": 2, "d": [1,2,3]}}'
	fd = open(f, 'w')
	fd.write(data)
	fd.close()
	
	# open db
	try:
		db = jsondb(f)
	except IOError, e:
		print e
		sys.exit(1)
	
	# check if an element exists
	assert db.exists("") == True
	assert db.exists("a/b") == True
	assert db.exists("a/e") == False
	
	assert db.get("/") == {"a": {"b": 1, "c": 2, "d": [1,2,3]}}
	assert db.get("") == {"a": {"b": 1, "c": 2, "d": [1,2,3]}}
	assert db.get("a/b") == 1
	assert db.get("a") == {"b": 1, "c": 2, "d": [1,2,3]}
	assert db.get("a/") == {"b": 1, "c": 2, "d": [1,2,3]}
	
	assert db.set({"a": 12}) == None
	assert db.get("") == {"a": 12}
	try:
		assert db.commit() == None
	except LockException, e:
		print "failed to write to file, locked exclusively"
	
