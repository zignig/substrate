import adapter

" primary incoming spool , base routing and error checking"
class incoming(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		if '_id' in body:
			cid = body['_id']
			print cid
			doc = self.cq.id(cid)
			#doc['marked'] = True
			#self.cq.save(cid,doc)
			#self.cq.sync()
			if 'type' in doc:
				self.channel.basic_publish('type_router',doc['type'],adapter.encode(body))
				#self.channel.basic_publish('amq.topic','chat.general',cid)
				return True

export = incoming 
