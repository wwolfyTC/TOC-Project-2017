from bs4 import BeautifulSoup as bs 
from urllib.request import urlopen
from pymongo import MongoClient

root = 'http://www.cplusplus.com'

headers = [
	'assert',
	'ctype',
	'errno',
	'float',
	'iso646',
	'limits',
	'locale',
	'math',
	'setjmp',
	'signal',
	'stdarg',
	'stddef',
	'stdio',
	'stdlib',
	'string',
	'time'
]

def htmlStr(s):
	if s is None:
		return ''
	r = ''
	for c in s:
		if c == '<':
			r += '&lt;'
		elif c == '>':
			r += '&gt;'
		elif c == '&':
			r += '&amp;'
		else:
			r += c
	return r
	

def parse(lib, collect):
	target = 'http://www.cplusplus.com/reference/c' + lib + '/'
	header = lib + '.h'

	# parser
	mainPage = urlopen(target).read()
	mainSoup = bs(mainPage, 'html.parser')
	
	# put header file
	try:
		description = mainSoup.find('div', id='I_description').string
	except:
		print('failed open main page:', lib)
		exit()
	
	# remove old items
	collect.delete_many({'header':header})
	print('old items removed:', lib)
	
	
	obj = {
		'name':htmlStr(header),
		'link':htmlStr(target),
		'header':htmlStr(header),
		'itemType':'header',
		'prototype':'',
		'description':htmlStr(description),
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
				params.append({'name':htmlStr(pname), 'description':htmlStr(pdescription)})
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
			'name':htmlStr(name),
			'link':htmlStr(link),
			'header':htmlStr(header),
			'itemType':itemType,
			'prototype':htmlStr(prototype),
			'description':htmlStr(description),
			'params':params,
			'returnVal':htmlStr(returnVal)
		}
	
		collect.insert_one(obj)
		print('insert:', obj['name'])
	
	
	print('done!')


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
col = cli.CLibrary.library

for head in headers:
	parse(head, col)

