#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback,time
base_ttl = 2
proc = yaml.load(open('process.yaml').read())
current_set =  {}

def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		if type(ref) != type({}):
			ch.basic_ack(delivery_tag = method.delivery_tag)
			print body+' not dict'	
			return
	except:
		print body+' not json'
		ch.basic_ack(delivery_tag = method.delivery_tag)
		return
	print method.exchange,method.routing_key,ref
	exchange = method.exchange
	routing_key = method.routing_key
	if 'ttl' in ref:
		ref['ttl'] = ref['ttl'] - 1
		if ref['ttl'] == 0:
			ch.basic_ack(delivery_tag = method.delivery_tag)
			return
	else:
		ref['ttl'] = base_ttl
	
	if exchange in proc:
		print '==> '+exchange
		if routing_key in proc[exchange]:
			print '===> '+routing_key
			if cq.redis.exists('recent:'+routing_key):
				cq.message(json.dumps(ref),routing_key,exchange)
			else:
				print 'binding '+exchange+'->'+routing_key
				ch.queue_declare(queue=routing_key,arguments={'x-expires':30000})
				ch.queue_bind(queue=routing_key,exchange=exchange,routing_key=routing_key)
				print 'resending '+str(ref)+' to '+exchange+'=>'+routing_key
				cq.message(json.dumps(ref),routing_key,exchange)
				print 'sending start to '+routing_key
				ch.basic_publish('command','spindle',json.dumps({'bobbin':routing_key}))
				cq.redis.set('recent:'+routing_key,'')
				cq.redis.expire('recent:'+routing_key,30)
				print current_set
		else:
			print 'unknown key '+routing_key
	
	#if method.routing_key in k:
	##	key = method.routing_key	
	#	bl_ref = proc['sump'][key]
	#	print method.routing_key
	#	if key in current_set:
	#		cq.message(json.dumps(ref),key,'incoming')
	#	else:
	#		print 'building and binding '+bl_ref
	#		ch.queue_declare(queue=bl_ref)
	#		ch.queue_bind(queue=bl_ref,exchange='incoming',routing_key=key)
	#		cq.message(json.dumps(ref),key,'incoming')
	#		ch.basic_publish('command','spindle',key)
	#		current_set[bl_ref] = True
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
	print 'building sump'
	cq.channel.exchange_declare(exchange='sump',exchange_type='topic',arguments={'alternate-exchange':'fail'}) 
	cq.channel.exchange_declare(exchange='fail',exchange_type='fanout',arguments={}) 
	cq.channel.queue_declare(queue='sump_spool')
	cq.channel.queue_bind(queue='sump_spool',exchange='sump',routing_key='*')
	print 'building top level exchanges'
	for i in proc.keys():
		print 'primary exchange '+i
		cq.channel.exchange_declare(exchange=i,exchange_type='topic',arguments={'alternate-exchange':'sump'}) 
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	gen_exchanges()
	cq.run_queue('sump_spool',callback)
