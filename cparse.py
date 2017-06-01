from bs4 import BeautifulSoup as bs 
from urllib.request import urlopen
from pymongo import MongoClient

from pprint import pprint


lib = 'time'

root = 'http://www.cplusplus.com'
target = 'http://www.cplusplus.com/reference/c' + lib + '/'
header = lib + '.h'

# database connect
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

# remove old items
collect.delete_many({'header':header})
print('old items removed')

# parser
mainPage = urlopen(target).read()
mainSoup = bs(mainPage, 'html.parser')

description = mainSoup.find('div', id='I_description').string

obj = {
	'name':header,
	'link':target,
	'header':header,
	'itemType':'header',
	'prototype':'',
	'description':description,
	'params':[],
	'returnVal':''
}

collect.insert_one(obj)
print('insert:', obj['name'])

# parse items
items = mainSoup.find_all('dl', class_='links')

for item in items:
	c11 = item.find('b', class_='C_cpp11')
	if c11 is not None:
		continue

	link = root + item.dt.a['href']
	name = item.dt.a.b.string

	page = urlopen(link).read()
	soup = bs(page, 'html.parser')

	itemType = soup.find('div', id='I_type').string.strip()

	try:
		prototype = soup.find('div', class_='C_prototype').pre.string
	except AttributeError:
		prototype = ''

	description = soup.find('div', id='I_description').string

	try:
		params = []
		paraSection = soup.find('section', id='parameters').dl.find_all('dt')
		for p in paraSection:
			pname = p.string
			strs = p.find_next('dd').strings
			pdescription = ''.join(strs)
			params.append({'name':pname, 'description':pdescription})
	except AttributeError:
		params = []

	try:
		returnSection = soup.find('section', id='return')
		returnSection.h3.decompose()

		strs = returnSection.strings
		returnVal = ''.join(strs)
	except AttributeError:
		returnVal = ''

	obj = {
		'name':name,
		'link':link,
		'header':header,
		'itemType':itemType,
		'prototype':prototype,
		'description':description,
		'params':params,
		'returnVal':returnVal
	}

	collect.insert_one(obj)
	print('insert:', obj['name'])

	#pprint(obj)
	#print('\n')

print('done!')