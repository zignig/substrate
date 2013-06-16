import adapter

" process and spool attachments "
class process(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
		self.routes = self.routes
	
	def consume(self,body):
		if '_id' in body:
			doc = self.cq.id(body['_id'])
			if '_attachments' in doc:
				att = doc['_attachments']
				for i in att:
					#print i
					mime_type = att[i]['content_type']
					mess = {'att':i,'_id':body['_id']}
					if mime_type in self.routes:
						print 'route for '+mime_type
						mess['route'] = self.routes[mime_type]
						
				 	self.channel.basic_publish('mime_type',mime_type,adapter.encode(mess))
				

export = process 
