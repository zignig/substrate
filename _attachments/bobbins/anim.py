import adapter

" animation type "
class anim(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print body
		doc = self.cq.id(body['_id'])
		print doc
		a = self.cq.delete_doc(doc)
		print a


export = anim 
