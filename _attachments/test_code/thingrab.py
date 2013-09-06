#!/usr/bin/python 

import requests,redis,json
from bs4 import BeautifulSoup

red = redis.Redis()

def get_thing(thing_id):
	s = requests.session()
	url = 'http://thingiverse.com/thing:'+str(thing_id)
	path = 'thing:'+str(thing_id)
	if red.exists(path):
		data = red.get(path) 
	else:
		r = s.get(url)
		data = r.content
		red.set(path,data)
		red.expire(path,86400)
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
	instructions = soup.find('div',attrs={'id':'instructions','class':'thing-info-content'}).get_text()
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
	return doc
#doc = get_thing(35167)
#doc = get_thing(126371)
#doc = get_thing(50212)
doc = get_thing(40212)
print json.dumps(doc,indent=True)
