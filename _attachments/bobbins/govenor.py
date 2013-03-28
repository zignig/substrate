#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback,requests

def get_queue_stat(cq):
	s = requests.Session()
	cred = cq.local_config['broker_cred']
	s.auth = (cred[0],cred[1])
	broker = cq.config['broker'][0]
	r = s.get('http://'+broker+':15672/api/queues')
	queues = r.json
	bobbin_list = []
	for i in queues:
		message_count = i['messages_ready']
		if message_count > 0:
			print i['name'],i['messages_ready']
			name = i['name']
			" don't respool yourself "
			if name != 'govenor' and name[0:3] !='amq':
				bobbin_list.append(name)
	return bobbin_list

def callback(ch,method,properties,body):
	ref = json.loads(body)
	print ref
	t = get_queue_stat(ch.cq)
	if 'spindle' in ref:
		print 'spindle starter'
		bobbin_list = get_queue_stat(ch.cq)
		queue = ref['spindle']
		name = queue['queue']
		ch.cq.redis.sadd('spindles',name)
		for i in t:
			ch.basic_publish('',name,json.dumps({'bobbin': i }))
	if 'start_bobbin' in ref:
		bobbin = ref['start_bobbin']
		ch.basic_publish('command','spindle',json.dumps({'bobbin': bobbin }))

	ch.basic_publish('error','error',json.dumps({'ref':ref}))
	ch.basic_ack(delivery_tag = method.delivery_tag)
	
def callback_rebuild(ch, method, properties, body):
	ref = json.loads(body)
	# hanlde spindle commands
	print ref	
	if ref.keys()[0] == 'spindle':
		comm = ref['spindle']
		if 'queue' in comm.keys():
			queue = comm['queue']
		if 'services' in comm.keys():
			for i in comm['services']:
				print i
				# just start one of each
				cq.channel.basic_publish('',queue,i)
	# handle bobbin
	if ref.keys()[0] == 'bobbin':
		print ref
		comm = ref['bobbin']
		ch.cq.redis.hincrby('bobbin',comm['name'])
	ch.basic_ack(delivery_tag = method.delivery_tag)

def build_exchanges(cq,sumpex='sump'):
	sump = cq.config['sump']
	for i in sump.keys():
		print i
		cq.channel.exchange_declare(exchange=i,exchange_type='fanout')
		for j in sump[i]:
			print '\t'+j
			cq.channel.queue_declare(queue=j)
			cq.channel.queue_bind(queue=j,exchange=i)
	exch = cq.config['exchanges']
	for i in exch.keys():
		print i
		cq.channel.exchange_declare(exchange=i,exchange_type='topic',arguments={'alternate-exchange':sumpex})
		for j in exch[i]:
			print '\t'+j
			cq.channel.queue_declare(queue=j)
			cq.channel.queue_bind(queue=j,exchange=i,routing_key=j)
	
def mime_types(cq):
	mt = cq.db.view('robot/mime_types',group=True).all()
	for i in mt:
		print i
		mtype = 'mime_type:'+i['key']
		cq.channel.queue_declare(queue=mtype)
		cq.channel.queue_bind(queue=mtype,exchange='mime_types',routing_key=mtype)	

if __name__ == "__main__":
	cq = adapter.couch_queue()
	#build_exchanges(cq)
	#mime_types(cq)
	cq.channel.basic_publish('command','notify',json.dumps({'spindle':'gov','keys':[]}))
	cq.redis.hincrby('bobbin','download',2)
	cq.redis.hincrby('bobbin','incoming',3)
	cq.redis.hincrby('bobbin','thingiverse',2)
	cq.run_queue('govenor',callback)
