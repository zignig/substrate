import adapter

" changes spooler "
class web_inter(adapter.worker):
	def __init__(self,queue=''):
		adapter.worker.__init__(self,queue)
	
	#def consume(self,body):
#		print body

	def run(self):
		while 1:
                  d = self.cq.redis.brpop('spool:fork')
                  print d
                  item = adapter.decode(d[1])
                  self.channel.basic_publish('incoming','mark',adapter.encode({'id':item['id'],'action':'mark'}))
                  
		
export = web_inter
