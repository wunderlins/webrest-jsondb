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
	
	"""
	data = {
		"user": [
			{
				"user_id": 234565,
				"user_name": "AwesomeUserName",
				"is_moderator": True,
			},{
				"user_id": 234561,
				"user_name": "AwesomeUserName2",
				"is_moderator": False,
			}
		]
	}
	db.data(dictionary=data)
	"""
	
	print db["user"][1]
