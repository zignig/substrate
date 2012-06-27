#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
from couchdbkit.consumer import Consumer

cq = adapter.couch_queue()

def run_item(item):
	print item
	if item.has_key('changes') and not item.has_key('deleted'):
		item['_id'] = item['id']
		cq.message(json.dumps(item),'changes')


def spool():
	update_seq = cq.db.info()['update_seq']	
	c = Consumer(cq.db)
	c.wait(run_item,since=update_seq)

def spool_status(view,key,queue):
		#l = cq.server[cq.db].view(view,key=key,limit=10).all()
		l = cq.db.view(view,reduce=False,key=key).all()
		for doc in l:
				print key+': '+doc['id']
				doc['_id'] = doc['id']
				cq.message(json.dumps(doc),key=queue)

def queue_all(queue):
		l = cq.db.view('_all_docs').all()
		for doc in l:
				cq.message(json.dumps(doc),key=queue)

def initilize(queue):
        l = cq.db.view(cq.config['initialize']).all()
        for doc in l:
            print doc['id']
            doc['_id'] = doc['id']
            cq.message(json.dumps(doc),key=queue)

def enqueue_status():
		status = cq.config['status_queue']
		for i in status.keys():
			print status[i]
			for j in status[i].items():
				print j
				spool_status(i,j[0],j[1])


cq.build()
cq.flush()
initilize('initialize')
queue_all('out')
enqueue_status()
while 1:
	spool()
