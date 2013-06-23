import adapter
import commands

" template spooler "
class maninfold(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print 'manifold test => '+str(body['att'])
		# use admesh to check manifoldiness
		return True
		

export = maninfold
