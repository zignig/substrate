#!/usr/bin/python 

import requests,redis,json
from bs4 import BeautifulSoup

red = redis.Redis()
ttl = 8640000
def get_thing(thing_id):
	if red.exists('thing_doc:'+str(thing_id)):
		return json.loads(red.get('thing_doc:'+str(thing_id)))
	s = requests.session()
	url = 'http://thingiverse.com/thing:'+str(thing_id)
	path = 'thing:'+str(thing_id)
	if red.exists(path):
		data = red.get(path) 
	else:
		r = s.get(url)
		data = r.content
		red.set(path,data)
		#red.expire(path,ttl)
	soup = BeautifulSoup(data)
	#title 
	title = soup.find('div',attrs={'class':'thing-interaction-parent'}).get('title')
	#print title
	# author
	author = soup.find('span',attrs={'class':'creator-name'}).find('a').get_text()
	#print author
	# licence
	licence = soup.find('div',attrs={'class':'thing-license'}).get('title')
	#print licence
	# description
	description = soup.find('div',attrs={'class','thing-info-content'}).get_text()
	#print description
	#dowloads 	
	downloads = []
	n = soup.find_all('div',attrs={'class':"thing-file-container"})
	for i in n:
		download = i.find('a',attrs={'class':'track'}).get('href')
		file_name = i.find('div',attrs={'class':'filename'}).get_text()
		downloads.append([download,file_name])
	#print downloads
	#tags
	tags = soup.find('div',attrs={'class':'tags'}).find_all('a')
	tag_list = []
	for i in tags:
		t = i.get_text()
		tag_list.append(t)
	#print tag_list
	# instructions
	instruct= soup.find('div',attrs={'id':'instructions','class':'thing-info-content'})
	if instruct == None:
		instructions = ''
	else:
		instructions = instruct.get_text()
	#print instructions

	# generate doc
	doc = {
		'author': author,
		'name':title,
		'tags': tag_list,
		'thingi_download': downloads,
		'thing_id': thing_id,
		'description': description.strip(),
		'instructions': instructions.strip(),
		'licence': licence,
		'type': 'thingiverse',
		'path': ['thingiverse','new'],
		'url': url
	}		
	red.set('thing_doc:'+str(thing_id),json.dumps(doc))
	red.sadd('things',str(thing_id))
	red.rpush('thing_queue',str(thing_id))
	#red.expire('thing_doc:'+str(thing_id),ttl)
	return doc

def get_author_id(author):
	s = requests.session()
	url = 'http://www.thingiverse.com/'+author
	path = 'author_page:'+str(author)
	if red.exists(path):
		data = red.get(path) 
	else:
		r = s.get(url)
		data = r.content
		red.set(path,data)
		#red.expire(path,ttl)
	soup = BeautifulSoup(data)
	rss_feed = soup.find('head').find('link',attrs={"rel":"alternate"}).get("href")
	author_id = rss_feed.split(':')[-1]
	return author_id

def get_author(author_id):
	s = requests.session()
	thing_list = 'author_ids:'+author_id
	if red.exists(thing_list):
		return json.loads(red.get(thing_list))
	url = 'http://www.thingiverse.com/ajax/user/designs'
	path = 'author:'+str(author_id)
	payload = {'id':author_id,'page':1,'per_page':50}
	if red.exists(path):
		data = red.get(path) 
	else:
		r = s.post(url,data=payload)
		data = r.content
		red.set(path,data)
		red.expire(path,ttl)
	soup = BeautifulSoup(data)
	a = soup.find_all('div',attrs={'class':'row-fluid'})
	things = []
	for i in a:
		thing_slug = i.find('a').get('href')
		thing_id = int(thing_slug.split(':')[1])
		things.append(thing_id)	
	red.set(thing_list,json.dumps(things))
	return things

	
#doc = get_thing(35167)
#doc = get_thing(126371)
#doc = get_thing(50212)
#doc = get_thing(40212)
#doc = get_thing(39682)
#print json.dumps(doc,indent=True)

def grab_author(author):
	author_id =  get_author_id(author)
	print author_id
	things = get_author(author_id)
	for i in things:
		doc = get_thing(i)
		try:
			print str(doc['name']),doc['thing_id']
		except:
			print 'fail'

grab_author('zignig')

