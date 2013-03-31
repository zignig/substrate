import adapter

" primary incoming spool , base routing and error checking"
class incoming(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		cid = body['_id']
		doc = self.cq.id(cid)
		if 'type' in doc:
			self.channel.basic_publish('type_router',doc['type'],adapter.encode(body))

export = incoming 
