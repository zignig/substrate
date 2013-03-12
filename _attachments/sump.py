#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback,time
base_ttl = 2
proc = yaml.load(open('process.yaml').read())
k = proc['sump'].keys()
current_set =  {}

def callback(ch, method, properties, body):
	ref = json.loads(body)
	print ref 
	if 'ttl' in ref:
		ref['ttl'] = ref['ttl'] - 1
		if ref['ttl'] == 0:
			ch.basic_ack(delivery_tag = method.delivery_tag)
			return
	else:
		ref['ttl'] = base_ttl
	
	if method.routing_key in k:
		key = method.routing_key	
		bl_ref = proc['sump'][key]
		print method.routing_key
		if key in current_set:
			cq.message(json.dumps(ref),bl_ref,'incoming')
		else:
			print 'building and binding '+bl_ref
			ch.queue_declare(queue=bl_ref)
			ch.queue_bind(queue=bl_ref,exchange='incoming',routing_key=key)
			cq.message(json.dumps(ref),key,'incoming')
			current_set[bl_ref] = True
	#if '_id' in ref:
	#	doc = cq.id(ref['_id'])
	#	if 'type' in doc:
	#		if 'name' in doc:
	#			#print doc['name'],doc['type']
				#print json.dumps(ref)
			#	cq.message(json.dumps(ref),doc['type'],'incoming')
	#print ref	
	#print method.exchange
	#print method.routing_key
	#a = ch.cq.redis.zincrby('mime_count',ref['key'])
	#if a == 1:
	##	print ref
		#bind_type(ref['key'])
	#print ch.cq.redis.zrange('mime_count',0,-1,withscores=True)
	ch.basic_ack(delivery_tag = method.delivery_tag)

def bind_type(mtype):
	print 'binding ' + mtype
	cq.channel.queue_declare(queue=mtype)
	cq.channel.queue_bind(queue=mtype,exchange='mime_types',routing_key=mtype)	

def gen_exchanges():
	cq.channel.exchange_declare(exchange='incoming',exchange_type='topic',arguments={'alternate-exchange':'sump'}) 
	cq.channel.exchange_declare(exchange='sump',exchange_type='topic',arguments={'alternate-exchange':'fail'}) 
	cq.channel.exchange_declare(exchange='fail',exchange_type='fanout',arguments={}) 
	cq.channel.exchange_declare(exchange='commands',exchange_type='topic',arguments={}) 
	cq.channel.queue_declare(queue='commands')
	cq.channel.queue_bind(queue='commands',exchange='commands',routing_key='*')
	cq.channel.queue_declare(queue='sump_spool')
	cq.channel.queue_bind(queue='sump_spool',exchange='sump',routing_key='*')
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	gen_exchanges()
	cq.run_queue('sump_spool',callback)
