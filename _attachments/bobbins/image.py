import adapter

" template spooler "
class test(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		doc = self.cq.id(body['_id'])
		print doc['_id']
		if 'thumb' not in doc:
			if '_attachments' in doc:
				att = doc['_attachments']
				for i in att:
					print i
					self.channel.basic_publish('render','thumbnail',adapter.encode({'_id':body['_id'],'att':i}))
		

export = test
