"""
just access mongoDB for convinent, not used in app.py
"""

from pymongo import MongoClient
from pprint import pprint

try:
	with open('../pw', 'r', encoding='utf-8') as fin:
		pw = fin.readline().strip()
except Exception:
	print('can not find password file')
	exit()

DBuri = ('mongodb://wwolfyTC:{0}@'
	'clibrary-shard-00-00-syrdm.mongodb.net:27017,'
	'clibrary-shard-00-01-syrdm.mongodb.net:27017,'
	'clibrary-shard-00-02-syrdm.mongodb.net:27017/'
	'admin?ssl=true&replicaSet=CLIbrary-shard-0'
	'&authSource=admin').format(pw)

cli = MongoClient(DBuri)
collect = cli.CLibrary.library

obj = {
	'description': 'Null pointer',
	'header': 'multiple header',
	'itemType': 'macro',
	'link': 'http://www.cplusplus.com/reference/cstdio/NULL/',
	'name': 'NULL',
	'params': [],
	'prototype': '',
	'returnVal': ''
}

r = collect.find_one({'name':'difftime'})
print(r['returnVal'])
for p in r['params']:
	print(p['name'], '\n', p['description'])
"""

collect.delete_many({'header':'string.h'})
"""
"""
rr = collect.find({'name':'NULL'})
for r in rr:
	pprint(r)
"""