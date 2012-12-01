#!/usr/bin/python 
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter

import stl,finished,initialize,pending
import thing_fetch,incoming,downloads
import changes,logging

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
	'stl':stl.callback
}
	


cq = adapter.couch_queue()
comm = cq.channel.queue_declare(exclusive=True)
cq.channel.queue_bind(queue=comm.method.queue,exchange='commands',routing_key='spindle')
services = {
	'queue':comm.method.queue,
	'services':spool_list.keys()
}
cq.channel.basic_publish('commands','notify',json.dumps(services))

def comm_callback(ch, method, properties, body):
	print body
	if spool_list.has_key(body):
		print 'spin up'
		tmp_cq = adapter.couch_queue()
		tmp_cq.start_spool(body,spool_list[body])
	ch.basic_ack(delivery_tag = method.delivery_tag)
	if body == 'die':
		ch.stop_consuming()


cq.run_queue(comm.method.queue,comm_callback)
