import adapter

" mark documents "
class marker(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
        print body

export = marker 
