import adapter

" thing router ( generic thing handler )"

class thing(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print 'thing '+body
		if '_id' in body:
			print 'thing ',self.queue,body['_id']
			self.channel.basic_publish('incoming','process',adapter.encode(body))

export = thing
