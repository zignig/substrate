#!/usr/bin/python 
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter,StringIO
readline.parse_and_bind('tab:complete')
cq = adapter.couch_queue()

path = cq.local_config['import_path']
li = os.listdir(path)
print li
for i in li:
	try:
		li2 = cq.attach(i)
		print li2
		if len(li2) == 0:
			print 'import '+i
			d = open(path+os.sep+i)
			doc = {'type':'image'}
			doc['image'] = i 
			doc['tags'] = ['new']
			print doc
			cq.db.save_doc(doc)
			cq.db.put_attachment(doc,d,i)
	except:
		print 'fail'
cq.redis.flushall()
