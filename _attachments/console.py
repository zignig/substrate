#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter
readline.parse_and_bind('tab:complete')
print('bl3dr console')
cq = adapter.couch_queue()
print('base object = cq')

def go():
	cq.spool(cq.author('zignig'))

author = cq.author
tags = cq.tags

def split_author(name):
	ids = cq.author(name)
	if len(ids) > 10:
		cq.server.create_db(name)
		cq.server.replicate(cq.db.uri,name,doc_ids=ids)
	else:
		print('to few things')
		print ids
		
