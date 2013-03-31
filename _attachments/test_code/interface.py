#!/usr/bin/python -i

import httplib
import urllib,urlparse
import json
import yaml
import os
import readline,rlcompleter
import requests

readline.parse_and_bind('tab:complete')

class empty:
	def __init__(self):
		pass

class design(yaml.YAMLObject):
	yaml_tag = '!design'
	def __init__(self,database,design_doc,dbname):
		self.__database = database
		if design_doc.has_key('views'):
			views = design_doc['views'].keys()
			for i in views:
				self.__dict__[str(i)] = view(i,database,design_doc['_id'].split('/')[1],dbname)
		pass

class view(yaml.YAMLObject):
	yaml_tag = '!view'
	view_limit = 10
	def __init__(self,v,db,des,dbname):
		self.db = db 
		self.view = str(v)
		self.des = str(des)
		self.dbname = str(dbname)
	
	def get(self,q='',**params):
		path = self.dbname+'/_design/'+self.des+'/_view/'+self.view+'?'
		if params.has_key('limit') == 0:
			params['limit'] = view.view_limit
		return self.db.get(path+q,**params)
	
	def __call__(self,q='',**params):
		return self.get(q,**params)

class database(yaml.YAMLObject):
	yaml_tag = '!database'
	def __init__(self,pcouch,dbname):
		self.pcouch = pcouch
		self.dbname = str(dbname)
		self.get_des()
		
	def get_des(self):
		d = self.pcouch.get(self.dbname+'/_all_docs?startkey="_design"&endkey="_design0"')
		if 'error' not in d:
			for i in d['rows']:
				des_name = i['id'].split('/')[1]
				print '\t'+des_name
				des = self.get(i['id'])
				self.__dict__[str(des_name)] = design(self.pcouch,des,self.dbname)

	def get(self,q='',**params):
		return self.pcouch.get(self.dbname+'/'+q,**params)

class couch(yaml.YAMLObject):
	yaml_tag = '!couch'
	def __init__(self,url='http://127.0.0.1:5984/'):
		u = urlparse.urlsplit(url)
		self.url = url
		self.host = u.hostname
		self.port = u.port
		self.username = u.username
		self.password = u.password
		self.auth_cookie = ''
		self.__r = requests.session()
		self.scan()

	def auth(self,username,password):
		print username,password

	def scan(self):
		databases = self.get('_all_dbs')
		for i in databases:
			print(i)
			self.__dict__[str(i)] = database(self,i)
		return databases

	def get(self,q='',**params):
		#print self.url+q
		req = self.__r.get(self.url+q,params=params)
		if req.status_code == 200:
			#print yaml.dump(req)
			return req.json
				
		else:
			return req.json
	
	def post(self,q,**params):
	 	conn = httplib.HTTPConnection(self.host,self.port)
		headers = {"Content-Length":str(len(q)),"Content-Type":"application/json"}
		par = urllib.urlencode(params)
		print headers,par,q
		conn.request('POST',q,par,headers)
		req = conn.getresponse()
		print yaml.dump(req)
		if req.status == 200:
			return json.loads(str(req.read()))
		else:
			return {'status':req.status,'reason':req.reason}
	
class source(yaml.YAMLObject):
	yaml_tag = '!source'
	def __init__(self):
		self.dbs = {} 
		self.attach('substrate','http://substrate.terra:5984/')
		self.save()
			
	def __repr__(self):
		return str(self.dbs)

	def attach(self,name,url):
		c = couch(url)
		self.__dict__[name] = c
		self.dbs[name] = url
		
			
	def save(self):
		f = open('config.yaml','w')
		f.write(yaml.dump(self))
		f.close()

def bootstrap(config='config.yaml'):
	try:
		os.stat(config)
		return yaml.load(open(config).read())
	except:
		s = source()
		s.save()
		return s

s = bootstrap()
