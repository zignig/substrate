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
	#print body
	ref = json.loads(body)
	cid = ref['_id']
	print("init : "+str(cid))
	D = ch.cq.id(cid) 
	#print D
	D['robot_status'] = 'new'
	if D.has_key('_attachments'):
		for i in D['_attachments']:
			att = D['_attachments'][i]
			att_doc = {'id':cid,'value':[att['content_type'],i]}
			spool_attachment(ch.cq,att_doc)
	ch.cq.save(cid,D)
	ch.basic_ack(delivery_tag = method.delivery_tag)
	

cq = adapter.couch_queue()
cq.run_queue('initialize',callback)
