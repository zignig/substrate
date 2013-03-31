#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter

import bobbins.stl
import bobbins.finished
import bobbins.initialize
import bobbins.pending

import bobbins.changes

readline.parse_and_bind('tab:complete')
print('bl3dr combined runner')

spool_list = [
	('initialize',bobbins.initialize.callback),
	('pending',bobbins.pending.callback),
	('finished',bobbins.finished.callback),
	('changes',bobbins.changes.callback)
	
]
	
for i in spool_list:
	# lots of sockets
	tmp_cq = adapter.couch_queue()
	tmp_cq.start_spool(i[0],i[1])


