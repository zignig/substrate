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
	
b = get_couch()
