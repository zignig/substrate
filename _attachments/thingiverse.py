#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import httplib,adapter,traceback
import readline , rlcompleter,string,uuid

readline.parse_and_bind('tab:complete')
import BeautifulSoup
print('bl3dr console')
cq = adapter.couch_queue()
print('base object = cq')
tdir = 'thingiverse_cache'

def load(path='thingiverse_cache'):
	li = os.listdir(path)
	cq.redis.delete('pages')	
	cq.thingi_id.list()
	for i in li:
		print i
		cq.redis.set(i,open(path+os.sep+i).read())
		if i[0:4] == 'page':
			cq.redis.sadd('pages',i)
		

def grab(page):
	doc = cq.redis.get(page)
	bs = BeautifulSoup.BeautifulSoup(doc)
	items = bs.findAll(attrs={'class':'thing-float'})
	docs = []
	for i in items:
		thing_info = i.find(attrs={'class':'thing-info'})
		d = {}
		d['name']= thing_info.find(name='a').text
		d['url']= thing_info.find(name='a').attrs[0][1]
		d['thingi_id'] = int(string.split(d['url'],':')[-1])
		d['author'] = thing_info.find(attrs={'class':'thing-byline'}).find(name='a').text
		d['type'] = 'thingiverse'
		thing_thumb = i.find(name='img')
		d['thumb_url'] = thing_thumb.attrs[0][1]
		docs.append(d)
	return docs 
	
def proc_next():
	t = cq.redis.spop('pages')
	print t
	a = grab(t)
	for i in a:
		print str(i['thingi_id']),i['name']
		print len(cq.thingi_id(i['thingi_id']))
		if len(cq.thingi_id(i['thingi_id'])) ==  0:
			uid = uuid.uuid4()
			print uid
			i['_id'] = str(uid)
			cq.save(str(uid),i)
		else:
			print i['name']+' exists !'

def fetch_thing(thing_id):
		tid = 'thing:'+str(thing_id)
		if cq.redis.exists(tid):
			return cq.redis.get(tid)
		else:
			conn = httplib.HTTPConnection("thingiverse.com",port=80)
			conn.request("GET", "/thing:"+str(thing_id))
			r1 = conn.getresponse()
			print r1.status, r1.reason
			data1 = r1.read()
			conn.close()
			if r1.status == 302:
				cq.redis.set(tid,data1)
				return cq.redis.get(tid)
			else:
				return None

def process_thing(thing_id):
	cid = cq.thingi_id(thing_id)[0]
	print 'bound :'+str(cid)
	doc  = cq.id(cid)
	print doc
	bs = BeautifulSoup.BeautifulSoup(fetch_thing(thing_id))
	print("Tags:")
	htags = bs.find(attrs={'id':'thing-tag-list'})
	tags = []
	try:
		for i in htags.findAll(name='a'):
			tag = str(string.split(i.attrs[0][1],':')[-1])
			tags.append(tag)
		print tags	
		doc['tags'] = tags
	except:
		print("No Tags")
	print("Downloads:")
	downloads = []
	try:
		thing_files = bs.find(attrs={'id':'thing-files'})
		for i in thing_files.findAll(name='a'):
			dl_id = i.attrs[0][1]
			dl_name = i.attrs[1][1]
			downloads.append([dl_id,dl_name])
	 	print downloads	
	except:
		print("No downloads")
	try:
		print("Derivatives:")
		derivatives = []
		hderiv = bs.findAll(attrs={'id':'thing-made'})[1]
		der = hderiv.find(attrs={'class':'small-thumbs'})
		for i in der.findAll(name='a'):
			deriv = str(string.split(i.attrs[0][1],':')[-1])
			derivatives.append(deriv)
		print(derivatives)
	except:
		print("No Deriv")		
	doc['tags'] = tags
	doc['thingi_derivative'] = derivatives
	doc['thingi_download'] = downloads
	doc['processed'] = True
	cq.save(doc['_id'],doc)
		
def thing_stamp(id,force=False):
	doc = cq.id(id)
	if doc.has_key('thingi_id'):
		if (doc.has_key('processed') == False) or force:
			process_thing(doc['thingi_id'])

def dump_cache():
	try:
		os.stat(tdir)
	except:
		os.mkdir(tdir)
	k = cq.redis.keys('thing:*')
	for i in k:
		print(i)
		data = cq.redis.get(i)
		f = open(tdir+os.sep+i,'w')
		f.write(data)
		f.close()
		
def spool_things():
	cq.channel.queue_declare(queue='thing_stamp')
	li = cq.process('unprocessed')
	for i in li:
		print i
		cq.message(json.dumps({'_id':i}),key='thing_stamp')

def thing_chomp():
	while True:
		a = cq.channel.basic_get(queue='thing_stamp',no_ack=True)[2]
		thing_stamp(json.loads(a)['_id'])
