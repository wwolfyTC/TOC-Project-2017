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

r = collect.find_one_and_delete({'name':'<climits> (limits.h)'})
pprint(r)