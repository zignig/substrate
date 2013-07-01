#!/usr/bin/python 
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter , uuid
import importlib,sys

cq = adapter.couch_queue()
comm = cq.channel.queue_declare(exclusive=True)

# recieve global spindle commands
cq.channel.queue_bind(queue=comm.method.queue,exchange='command',routing_key='spindle')
services = {'queue':comm.method.queue }
cq.channel.basic_publish('command','notify',json.dumps({'spindle':services}))

threads = {}

def try_load(name,namespace='bobbins'):
	" attempt load a bobbin "
	try:
		print 'trying to load '+name
		mod = importlib.import_module(namespace+'.'+name)
		print mod.export
		return (True,mod.export)
	except Exception,e:
		exc_type, exc_value, exc_tb = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_tb)
		return (False,False)
		
def comm_callback(ch, method, properties, body):
	print body
	try:
		ref = json.loads(body)
	except:
		print body + ' not json'
		ch.basic_ack(delivery_tag = method.delivery_tag)
		return
	ch.basic_ack(delivery_tag = method.delivery_tag)
	if 'start_bobbin' in ref:
		bobbin = ref['start_bobbin']
		print 'try load'
		status , caller = try_load(bobbin)
		print 'finish load with '+str(status)
		if status:
			print 'spin up'
			#tmp_cq = adapter.couch_queue()
			#thread_id = uuid.uuid4()
			#threads[thread_id] = tmp_cq
			new_worker = caller(bobbin)
			new_worker.spindle = comm.method.queue
			new_worker.setDaemon(True)
			threads[new_worker.id] = new_worker
			print 'start worker'
			new_worker.start()
			print 'worker running'
			#tmp_cq.start_spool(ref['bobbin'],new_worker.callback)
			cq.channel.basic_publish('command','notify',json.dumps({'bobbin':{'id':str(new_worker.id),'name':bobbin}}))
		else:
			cq.channel.basic_publish('error','error',json.dumps({'error':body}))

		if bobbin  == 'status':
			print threads
			for i in threads:
				worker = threads[i]
				info = {'status':'check'
						,'spindle':worker.spindle,
						'queue':worker.queue,
						'uuid':str(i)}
				print worker.spindle,worker.queue,i
				cq.channel.basic_publish('command','notify',json.dumps(info))

		if bobbin == 'die':
			ch.stop_consuming()

"start the spindle"
cq.run_queue(comm.method.queue,comm_callback)
