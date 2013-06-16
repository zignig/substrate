import adapter

" template spooler "
class slicer(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print 'slice =>'+str(body['att'])
		return True
		

export = slicer 
