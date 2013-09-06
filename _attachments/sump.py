#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback,time

import bobbins.govenor as gov
base_ttl = 8 
proc = yaml.load(open('process.yaml').read())
current_set =  {}

def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		if type(ref) != type({}):
			ch.basic_ack(delivery_tag = method.delivery_tag)
			ch.basic_publish('error','error',json.dumps({'error':body}))
			print body+' not dict'	
			return
	except:
		print body+' not json'
		ch.basic_ack(delivery_tag = method.delivery_tag)
		ch.basic_publish('error','error',json.dumps({'error':body}))
		return
	#print method.exchange,method.routing_key,ref
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
		#print '==> '+exchange
		if routing_key in proc[exchange]:
			#print '===> '+routing_key
			target_spool = proc[exchange][routing_key]
			if cq.redis.exists('recent:'+routing_key):
				#print 'resending '+str(ref)+' to '+exchange+'=>'+routing_key
				cq.message(json.dumps(ref),routing_key,exchange)
			else:
				print 'binding '+exchange+' -> '+routing_key+' -> '+target_spool
				ch.queue_declare(queue=target_spool,arguments={'x-expires':2*1000})
				#ch.queue_declare(queue=target_spool,arguments={'auto_delete':True})
				ch.queue_bind(queue=target_spool,exchange=exchange,routing_key=routing_key)
				print 'resending '+str(ref)+' to '+exchange+'=>'+routing_key
				cq.message(json.dumps(ref),routing_key,exchange)
				ch.basic_publish('command','notify',json.dumps({'start_bobbin':target_spool}))
				ch.cq.redis.sadd('running_bobbins',target_spool)
				#ch.basic_publish('error','error',json.dumps({'info':ref,'target_spool':target_spool}))
				cq.redis.set('recent:'+routing_key,'')
				cq.redis.expire('recent:'+routing_key,30)
		else:
			print 'unknown key '+routing_key
			print 'binding '+exchange+' -> '+routing_key+' to unknown' 
			ch.queue_bind(queue='unknown',exchange=exchange,routing_key=routing_key)
			ch.basic_publish('error','unknown',json.dumps({'error':ref,'exchange':exchange,'routing_key':routing_key}))
	ch.basic_ack(delivery_tag = method.delivery_tag)

def gen_exchanges():
	print 'building sump'
	cq.channel.exchange_declare(exchange='sump',exchange_type='topic',arguments={'alternate-exchange':'fail'}) 
	cq.channel.exchange_declare(exchange='command',exchange_type='topic',arguments={'alternate-exchange':'fail'}) 
	cq.channel.exchange_declare(exchange='error',exchange_type='topic',arguments={'alternate-exchange':'fail'}) 
	cq.channel.exchange_declare(exchange='logging',exchange_type='topic',arguments={'alternate-exchange':'fail'}) 
	cq.channel.queue_declare(queue='sump_spool')
	cq.channel.queue_declare(queue='govenor')
	cq.channel.queue_declare(queue='dev_error')
	cq.channel.queue_declare(queue='unknown')
	cq.channel.queue_bind(queue='sump_spool',exchange='sump',routing_key='*')
	cq.channel.queue_bind(queue='dev_error',exchange='error',routing_key='*')
	cq.channel.queue_bind(queue='govenor',exchange='command',routing_key='notify')
	print 'building error'
	print '-----'
	print 'building top level exchanges'
	for i in proc.keys():
		print 'primary exchange '+i
		cq.channel.exchange_declare(exchange=i,exchange_type='topic',arguments={'alternate-exchange':'sump'}) 
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	gen_exchanges()
	cq.channel.basic_publish('command','start',json.dumps({'base':'start'}))
	cq.channel.basic_publish('command','notify',json.dumps({'base':'start'}))
	cq.channel.basic_publish('logging','error',json.dumps({'base':'start'}))
	cq.channel.basic_publish('logging','error',json.dumps({'base':'start'}))
	# start up the govenor
	g = gov.govenor('govenor')
	g.setDaemon(True)
	g.start()
	cq.run_queue('sump_spool',callback)
