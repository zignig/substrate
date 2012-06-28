#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import adapter,traceback, string
import readline , rlcompleter
readline.parse_and_bind('tab:complete')
print('bl3dr console')
cq = adapter.couch_queue()

m = cq.config['mime_routing']
print m
# get extensions
ex = {}
for i in m.keys():
	ex[m[i]] = i
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
				print os.stat(fname)
				flist.append(fname) 
