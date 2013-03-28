#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter
readline.parse_and_bind('tab:complete')
print('bl3dr console')
cq = adapter.couch_queue()
print('base object = cq')
proc = yaml.load(open('process.yaml').read())

def go():
	cq.spool(cq.author(cq.local_config['author']))

author = cq.author
tags = cq.tags
# generate process magic
base = adapter.empty()
for i in proc.keys():
	ex = adapter.empty()
	base.__dict__[i] = ex
	for j in proc[i]:
		ex.__dict__[j] = adapter.item(cq,i,j)

def spool_all():
	docs = cq.db.all_docs().all()
	ids = []
	for i in docs:
		ids.append(i['id'])
	cq.spool(ids)

def split_author(name):
	ids = cq.author(name)
	if len(ids) > 10:
		cq.server.create_db(name)
		cq.server.replicate(cq.db.uri,name,doc_ids=ids)
	else:
		print('to few things')
		print ids
		
