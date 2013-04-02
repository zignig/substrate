import adapter
from couchdbkit.consumer import Consumer

" changes spooler "
class changes(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	#def consume(self,body):
#		print body

	def run(self):
		while 1:
			update_seq = self.cq.db.info()['update_seq']
			c = Consumer(self.cq.db)
			c.wait(self.run_item,since=update_seq)

	def run_item(self,item):
		print item
		if item.has_key('changes') and not item.has_key('deleted'):
			item['_id'] = item['id']
			self.channel.basic_publish('incoming','incoming',adapter.encode(item))
		
export = changes 
