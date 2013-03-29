#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	print "changes" + body
	server = ch.couch
	conf = ch.cq.config
	cq = ch.cq
	states = conf['status_states']
	database = cq.db 
	ref = json.loads(body)
	cid = ref['_id']
	D = ch.cq.id(cid) 
	if D.has_key('robot_status'):
		stat = D['robot_status']
		print D['_id'] , stat
		if states.has_key(stat):
			cq.message(json.dumps(D),states[stat])
	else:
		cq.message(json.dumps(D),'initialize')
	ch.basic_ack(delivery_tag = method.delivery_tag)


def attachements(doc): #incomplete 

	rev = int(ref['changes'][0]['rev'].split('-')[0])
	print rev
	if D.has_key('_attachments'):
		for i in D['_attachments']:
			print i + ': ',
			print D['_attachments'][i] 
			revpos = D['_attachments'][i]['revpos'] 
			if revpos == rev:
				print 'spool me' + i
				ch.cq.message(i,'out')
	ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('changes',callback)
