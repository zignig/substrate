import adapter

" thumbnail spooler "
class thumbnail(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print 'do blender stuff => '+body['att'] 

export = thumbnail 
