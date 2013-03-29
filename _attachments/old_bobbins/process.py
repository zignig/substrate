#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback


def spool_attachment(cq,doc):
		#print doc
		mime_dict = cq.config['mime_routing']
		mime = doc['value'][0]
		if mime_dict.has_key(mime):
			cq.message(json.dumps(doc),mime_dict[mime])
		else:
			cq.message(json.dumps(doc),'classify')

def callback(ch, method, properties, body):
	ref = json.loads(body)
	cid = ref['_id']
	D = ch.cq.id(cid) 
	#if 'name' in D:
		#print 'process ' + D['name']
	if '_attachments' in D:
		att = D['_attachments']
		for i in att:
			#print '\t'+i+' = '+str(att[i]['content_type'])
			ch.basic_publish('mime_type',att[i]['content_type'],json.dumps({'name':i}))
	ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('process',callback)
