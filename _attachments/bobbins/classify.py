import adapter

" mime type classifier "

class test(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print body

export = test
