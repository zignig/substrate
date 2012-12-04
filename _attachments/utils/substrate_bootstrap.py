#!/usr/bin/python 

import couchdbkit,json,urlparse

print('Welcome to the substrate database intsaller')
print('Checking remote server')

remote = 'http://bl3dr.iriscouch.com/'
remote_db = 'incoming'

remote_server = couchdbkit.Server(remote)

global local_server

try:
	print(remote_server.info())
	print(remote_server[remote_db].info())
except:
	print('UMM....')
	print('no network ? , DNS broken')

def get_couch():
	exit = 1
	while exit:
		print('Enter couch url : http://user:pass@example.com:<port>/')
		r = raw_input('>')
		u = urlparse.urlparse(r)	
		print(u)
		if u.hostname != None:
			s = couchdbkit.Server(u.geturl())
			try:
				info = s.info()
				if info.has_key('couchdb'):
					exit = 0
			except:
				print('fail server '+r)
	return s
	
def add_replication(name,source):
	return
	

#b = get_couch()
local_c = couchdbkit.Server()
print(local_c.info())
print('set up replication')
print('servers db')
local_c.get_or_create_db('servers')
local_c.replicate(remote+'/'+'servers','servers')
print('incoming')
local_c.get_or_create_db('incoming')
rep_db = local_c['_replicator']
if rep_db.doc_exist('bl3dr_incoming') == False:
	incoming = {'_id':'bl3dr_incoming','source':'http://bl3dr.iriscouch.com//incoming','target':'incoming'}
	rep_db.save_doc(incoming)

