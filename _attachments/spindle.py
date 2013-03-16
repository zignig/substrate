#!/usr/bin/python 
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter , uuid

#import stl,finished,initialize,pending
#import frag_spooler
#import thing_fetch,incoming,downloads
#import changes,logging
from bobbins import downloads
from bobbins import stl 
from bobbins import thing_fetch 
from bobbins import incoming 

readline.parse_and_bind('tab:complete')
print('bl3dr combined runner')

#	('initialize',initialize.callback),
#	('pending',pending.callback),
#	('finished',finished.callback),
#	('stl',stl.callback),

spool_list = {
	'download':downloads.callback,
	'thingiverse':thing_fetch.callback,
	'incoming':incoming.callback,
	'stl':stl.callback,
#	'frag_spooler':frag_spooler.callback
}
	
threads = []

cq = adapter.couch_queue()
comm = cq.channel.queue_declare(exclusive=True)
cq.channel.queue_bind(queue=comm.method.queue,exchange='command',routing_key='spindle')
services = {
	'queue':comm.method.queue,
	'services':spool_list.keys()
}
cq.channel.basic_publish('command','notify',json.dumps({'spindle':services}))

threads = {}
def comm_callback(ch, method, properties, body):
	print body
	try:
		ref = json.loads(body)
	except:
		print body + ' not json'
		ch.basic_ack(delivery_tag = method.delivery_tag)
		return
	if 'bobbin' in ref:
		if spool_list.has_key(ref['bobbin']):
			print 'spin up'
			tmp_cq = adapter.couch_queue()
			thread_id = uuid.uuid4()
			threads[thread_id] = tmp_cq
			tmp_cq.start_spool(ref['bobbin'],spool_list[ref['bobbin']])
			cq.channel.basic_publish('command','notify',json.dumps({'bobbin':{'id':str(thread_id),'name':body}}))
			ch.basic_ack(delivery_tag = method.delivery_tag)
		else:
			ch.basic_ack(delivery_tag = method.delivery_tag)
			cq.channel.basic_publish('error','error',json.dumps({'error':body}))

		if ref['bobbin'] == 'die':
			ch.stop_consuming()

cq.run_queue(comm.method.queue,comm_callback)
