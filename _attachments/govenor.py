#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	ref = json.loads(body)
	print ref
	print cq.redis.hgetall('bobbin')
	for i in ref['services']:
		val = cq.redis.hget('bobbin',i)
		if val <> None:
			if int(val)  > 0:
				print 'start '+i+' on '+ref['queue']
				cq.redis.hincrby('bobbin',i,1)
				cq.channel.basic_publish('',ref['queue'],i)

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
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	build_exchanges(cq)
	cq.redis.hincrby('bobbin','download',2)
	#cq.redis.hincrby('bobbin','incoming',2)
	#cq.redis.hincrby('bobbin','thingiverse',2)
	#cq.redis.hincrby('bobbin','stl',2)
	
	cq.run_queue('notify',callback)
