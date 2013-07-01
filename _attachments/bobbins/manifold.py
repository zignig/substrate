import adapter
import commands,os

" template spooler "
class maninfold(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print 'manifold test => '+str(body['att'])
		att = self.cq.db.fetch_attachment(body['_id'],body['att'])
		file_path = 'cache'+os.sep+body['att']
		f = open(file_path,'w')
		f.write(att)
		f.close()
		# use admesh to check manifoldiness
		status,value = commands.getstatusoutput('admesh '+file_path)
		os.remove(file_path)
		if status == 0:
			return True
		else:
			return False

export = maninfold
