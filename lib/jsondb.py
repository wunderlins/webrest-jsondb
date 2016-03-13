#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simple json file access with exclusive locking during write.

Storing data will set an exclusive lock to the data file until data is 
commited to disk. Make sure to take this into account on multi threaded 
applications.

Writing data is always write all, this implementation is not intended for 
large database files.

Check the main function for usage examples.

Interface
db = new jsonndb("file.json")

data = db.get(None)  # fetch the root node
data = db.get("a/b") # fetch data["a"]["b"]
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
	
	def __init__(self, path=""):
		"""Open json file
		
		:param path: path to json file
		:returns: None
		"""
		self.__path = path
		f = open(path, 'rb')
		self.__data = json.load(f)
		f.close()
	
	def __cleanpath(self, path=""):
		"""Sanitize object path
		
		:param path: path to object
		:returns: str
		"""
		if len(path) > 0 and path[-1] == "/":
			path = path[0:-1]
		return path		
	
	def exists(self, path):
		"""Check if object exists
		
		:param path: path to object
		:returns: Bool
		"""
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
	
	def get(self, path=""):
		"""Fetch an object an all it's children
		
		:param path: path to object
		:returns: dict
		"""
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
		
		return {"data": node, "path": path}
	
	def is_dirty(self):
		"""Check if there uncommited changes
		
		:returns: Bool
		"""
		return self.__dirty
	
	def set(self, data={}, path=""):
		"""Set data, everything will be overwitten
		
		:param data: dict
		:param path: string element to set/replace
		:returns: None
		"""
		
		if type(data) != dict and path == "":
			raise TypeError("Expected dict")
		
		# set root
		if path == "":
			self.__dirty = True
			self.__data = data
			return
		
		# handle path
		path = self.__cleanpath(path)
		node = self.__data
		
		if not self.exists(path[0:-1]):
			raise ExceptionNotFound("Element "+path+" not found in " + self.__path)
		
		apath = path.split('/')
		
		# handle 
		if len(apath) == 1:
			self.__data[apath[0]] = data
			self.__dirty = True
			return
		
		parent = None
		lastkey = None
		for e in apath:
			lastkey = e
			try:
				node[e]
			except KeyError, ex:
				# FIXME: will fail on non existend intermediate nodes
				parent = node
				node[e] = data
			
			parent = node
			node = node[e]
		
		if type(node) != int or type(node) == float or type(node) == str or \
		   type(node) == unicode or type(node) == list:
			parent[lastkey] = data
		elif type(node) == dict:
			node = data
		else:
			raise TypeError("Unhandled Datatype " + type(node))
			
		self.__dirty = True
		
	def commit(self):
		"""Commit changes to disk
		
		:returns: None
		"""
		if self.__dirty == False:
			return
		
		# import only on write, we expect most operations to be read operations
		import portalocker
		file = open(self.__path, 'wb')
		portalocker.lock(file, portalocker.LOCK_EX)
		json.dump(self.__data, file)
		file.close()
		
		self.__dirty == False

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
	
	try:
		assert db.get("/") == {"a": {"b": 1, "c": 2, "d": [1,2,3]}}
		assert db.get("") == {"a": {"b": 1, "c": 2, "d": [1,2,3]}}
		assert db.get("a/b") == 1
		assert db.get("a") == {"b": 1, "c": 2, "d": [1,2,3]}
		assert db.get("a/") == {"b": 1, "c": 2, "d": [1,2,3]}
	except ExceptionNotFound, e:
		print e
		sys.exit(1)
	
	try:
		assert db.set({"a": 12}) == None
	except TypeError, e:
		print e
		sys.exit(1)
		
	try:
		assert db.get("") == {"a": 12}
	except ExceptionNotFound, e:
		print e
		sys.exit(1)
	
	try:
		assert db.set({"a": {"b": 1, "c": 2, "d": [1,2,3]}}) == None
		assert db.set({"e": "eeeee"}, "x") == None
		assert db.set({"x": "1", "xx": 2}, "a/e") == None
		assert db.set(50, "x") == None
		assert db.set(20, "a/d") == None
	except TypeError, e:
		print e
		sys.exit(1)
	
	try:
		assert db.commit() == None
	except LockException, e:
		print "failed to write to file, locked exclusively"
	
	print db.get("")

