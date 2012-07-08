#!/usr/bin/python
import os,subprocess
import pika,couchdbkit,json
import yaml,pika,redis
import threading

TTL = 9600 
TTL2 = 86400 
class redis_query:
	" redis query abstraction"
	def __init__(self,database,redis,name,query):
		self.name = name
		self.redis = redis
		self.db = database
		self.query = query

	def list(self,length=200):
		if self.redis.exists(self.name):
			return self.redis.zrevrange(self.name,0,length)
		else:
			q = self.db.view(self.query,group=True).all()
			for i in q:
				self.redis.zadd(self.name,i['key'],i['value'])
			self.redis.expire(self.name,TTL)
			return self.redis.zrevrange(self.name,0,length)

	def __call__(self,query=''):
		if query == '':
			return self.list()
		if self.redis.exists(self.name+':'+str(query)):
			return list(self.redis.smembers(self.name+':'+str(query)))
		else:
			v = self.db.view(self.query,reduce=False,key=query).all()
			if len(v) > 0:
				for i in v:
					self.redis.sadd(self.name+':'+str(query),i['id'])
				self.redis.expire(self.name+':'+str(query),TTL)
				self.redis.zadd(self.name,i['key'],len(v))
				return list(self.redis.smembers(self.name+':'+str(query)))
			else:
				return [] 
			
class couch_queue:
	def __init__(self,config='config.json'):
		print("load config")
		try:
				os.stat(config)
				conf = json.loads(open('config.json').read())
				self.local_config = conf
		except:
				print("no config")

		print("connect to couch")
		try:
			self.server = couchdbkit.Server(conf['server'])
			current = self.server[conf['database']][conf['constructor']]
			self.db = self.server[current['databases'][0]]
			brokers = current['broker']
			print(json.dumps(current,sort_keys=True,indent=4)) 
			self.config = current
		except:
			print("couchdb fail")
		try:
			print("connect to broker")
			credentials = pika.PlainCredentials(conf['broker_cred'][0],conf['broker_cred'][1])
			print brokers
			connection = pika.BlockingConnection(pika.ConnectionParameters(credentials=credentials,host=str(brokers[0])))
			channel = connection.channel()
			channel.basic_qos(prefetch_count=1)
			self.channel = channel
			print("connected")
		except:
			print("broker failed")
		try:
			print("connect to redis")
			svr = self.local_config['redis']
			print(svr)
			r = redis.Redis(svr)
			self.redis = r
			print("connected")
			print("build queries")
			qs = self.config['redis_query']
			# dict access to queries 
			self.queries = {}
			for i in qs.keys():
				print('   '+i)
				qe = redis_query(self.db,self.redis,i,qs[i])
				self.queries[i] = qe
				self.__dict__[i] = qe 

		except:
			print("redis failed")


	def run_queue(self,default_queue,callback):
		print('running')
		# add the server to the queue for couch access
		self.channel.couch = self.server
		self.channel.cq = self
		self.channel.config = self.config
		self.channel.db = self.db
		self.channel.basic_consume(callback,queue=default_queue)
		self.channel.start_consuming()
	
	def build(self):
		print "[X] building queues" 
		for i in self.config['queues']:
			print('creating queue '+i)
			self.channel.queue_declare(queue=str(i))
		
	def flush(self):
		print "[X] flushing queues" 
		for i in self.config['queues']:
			print('flushing queue '+i)
			self.channel.queue_purge(queue=str(i))
		
	def message(self,mes,key='default'):
		self.channel.basic_publish(exchange='', routing_key=key, body=mes)
	
	def save(self,id,doc):
		ids = 'id:'+id
		self.redis.set(ids,json.dumps(doc))
		self.redis.expire(ids,TTL)
		self.redis.sadd('dirty',ids)
		self.message(json.dumps({'_id':id}),'changes')
        
	def write(self,id,doc):
		ids = 'id:'+id
		self.db.save_doc(doc)
		self.redis.delete(ids)

	def id(self,id):
		ids = 'id:'+id
		if self.redis.exists(ids):
		 	doc = json.loads(str(self.redis.get(ids)))
			#print(doc['_id']+' : '+doc['name']+' by '+doc['author'])
			return doc 
		else:
			doc = self.db[id]
			self.redis.set(ids,json.dumps(doc))
			self.redis.expire(ids,TTL2)
			#print(doc['_id']+' : '+doc['name']+' by '+doc['author'])
			self.redis.sadd('loaded',doc['_id'])
			return doc	
	
		
	def load(self,items):
		for i in items:
			self.id(i)
	
	def spool(self,items):
		for i in items:
			self.message(json.dumps({'_id':i}),'incoming')

	def sync(self):
		if self.redis.exists('dirty'):
			li = list(self.redis.smembers('dirty'))
			for i in li:
				try:
					self.write(i,self.id(i[3:]))
					print('saving ; '+i)
					self.redis.srem('dirty',i)
					#self.redis.delete(i)
				except:
					print 'fail on : '+i
			#self.redis.delete('dirty')

	def cur_id(self,id):
            ids = 'id:'+id
            doc = self.db[id]
            self.redis.set(ids,json.dumps(doc))
            self.redis.expire(ids,TTL2)
            return doc

	def start_spool(self,name,callback):
		qt = queue_thread(self,name,callback)
		qt.setDaemon(True)
		qt.start()
		return qt
	



def callback(ch, method, properties, body):
	print ch,method,properties,body
	ch.basic_ack(delivery_tag = method.delivery_tag)

def test(queue_name):
	cq = couch_queue()
	cq.run_queue(queue_name,callback)


class queue_thread(threading.Thread):
	def __init__(self,cq,queue_name,callback):
		threading.Thread.__init__(self)
		self.cq = cq
		self.queue_name = queue_name
		self.callback = callback
	
	def run(self):
		self.cq.run_queue(self.queue_name,self.callback)
