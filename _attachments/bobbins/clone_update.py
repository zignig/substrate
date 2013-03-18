#!/usr/bin/env python
import os,subprocess,datetime
import pika,couchdbkit,json
import yaml,adapter,traceback

def now():
    return  datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%Sz')

def callback(ch, method, properties, body):
	print body 
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('clone_update',callback)
