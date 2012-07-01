#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import adapter,traceback, string
import readline , rlcompleter
readline.parse_and_bind('tab:complete')
print('bl3dr console')
cq = adapter.couch_queue()
ttl = cq.config['ttl']
base_tag = 'walker:'

m = cq.config['mime_routing']
# get extensions
ex = {}
for i in m.keys():
	ex[m[i]] = i 
	cq.redis.sadd('walker',base_tag+i)
cq.redis.expire('walker',ttl)
print ex
	
flist = []

def walker(directory):
	print(directory)
	for root,dirs,files in os.walk(directory):
		for i in files:
			ext = string.split(str(i),'.')[-1]
			if ex.has_key(ext):
				fname= root+os.sep+i
				print(fname)
				#print os.stat(fname)
				flist.append(fname) 
				cq.redis.sadd(base_tag+ex[ext],json.dumps([root,i]))
				cq.redis.sadd(base_tag+'folders',root)

def gen_and_spool(mime):
	if m.has_key(mime):
		cq.channel.queue_declare(queue=base_tag+mime)
		cq.channel.queue_purge(queue=base_tag+mime)
		for i in range(cq.redis.scard(base_tag+mime)):
			f_name = cq.redis.spop(base_tag+mime)
			print f_name
			cq.message(f_name,key=base_tag+mime)

def enspool():
	for i in ex.values():
		gen_and_spool(i)	
	
walker('/home/zignig/Downloads')
