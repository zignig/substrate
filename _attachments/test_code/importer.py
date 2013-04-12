#!/usr/bin/python -i
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
		li = cq.attach(i)
		if len(li) == 0:
			print 'import '+i
			d = open(path+os.sep+i)
			doc = {'type':'image'}
			cq.db.save_doc(doc)
			cq.db.put_attachment(doc,d,i)
	except:
		print 'fail'
