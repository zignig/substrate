import adapter

" thingiverse interchange "
class thingiverse(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		doc = self.cq.id(body['_id'])
		if 'thing_fetched' in doc:
			self.channel.basic_publish('incoming','process',adapter.encode(body))

export = thingiverse 
