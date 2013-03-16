#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time

def callback(ch, method, properties, body):
	print body
	ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('dev_error',callback)
