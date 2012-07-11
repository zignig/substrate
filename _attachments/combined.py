#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter

import stl,finished,initialize,pending
import changes

readline.parse_and_bind('tab:complete')
print('bl3dr combined runner')

spool_list = [
	('initialize',initialize.callback),
	('pending',pending.callback),
	('finished',finished.callback),
	('stl',stl.callback),
	('changes',changes.callback)
	
]
	
for i in spool_list:
	# lots of sockets
	tmp_cq = adapter.couch_queue()
	tmp_cq.start_spool(i[0],i[1])

cq = adapter.couch_queue()

