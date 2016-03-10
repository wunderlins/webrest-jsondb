#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib', 'jsondatabase-0.1.1'))

try:
	import simplejson as json
except ImportError:
	import json

if __name__ == "__main__":
	from jsondb.db import Database
	db = Database("data.json")
	
	# add one item to a list
	path = [u"user", 2]
	data = {"element": 1}
	
	# find primary key in db, store prikey in variable
	
	# traverse dow the tree to check if the item exists
		# if not, generate intermediate elments and target
		# if exists, replace original item with post data
	
	# replace db[prikey] with the current in mem copy of the tree
	

