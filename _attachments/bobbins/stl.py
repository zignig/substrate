import adapter

" template spooler "
class test(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)

	def consume(self,body):
		# stl handler 
		# uses routes to push the file about
		return True	

export = test
