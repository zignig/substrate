import adapter

" thing processor "
class thing(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		self.channel.basic_publish('incoming','process',adapter.encode(body))

export = thing
