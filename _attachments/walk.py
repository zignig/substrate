#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback

def callback(ch, method, properties, body):
	print body
	server = ch.couch
	database = server[ch.db]
	ref = json.loads(body)
	cid = ref['id']
	D = database[cid]
	print D
	D['robot_status'] = 'new'
	database.save_doc(D)
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('classify',callback)
