import adapter

" process and spool attachments "
class process(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		if '_id' in body:
			doc = self.cq.id(body['_id'])
			if '_attachments' in doc:
				att = doc['_attachments']
				for i in att:
				 	self.channel.basic_publish('mime_type',att[i]['content_type'],adapter.encode({'att':i}))
				

export = process 
