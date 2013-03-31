#!/usr/bin/python

import requests 
import BeautifulSoup
import string

s = requests.session()

def grab_index(page=1,per_page=16):
	p = {'type':'newest','per_page':per_page,'page':page}
	print p
	r = s.post('http://www.thingiverse.com/ajax/things/paginate_things',params=p)
	bs = BeautifulSoup.BeautifulSoup(r.text)
	items = bs.findAll(attrs={'class':'thing'})
	docs = []
	for i in items:
		print i
		d = {}
		d['name']= i.find(attrs={'class':'thing-name'}).text
		d['url']= i.find(name='a').attrs[0][1]
		d['thingi_id'] = int(string.split(d['url'],':')[-1])
		d['author'] = i.find(attrs={'class':'thing-byline'}).find(name='a').text
		d['type'] = 'thingiverse'
		thing_thumb = i.find(name='img')
		d['thumb_url'] = thing_thumb.attrs[1][1]
		docs.append(d)
	return docs 

t = grab_index()
print t

