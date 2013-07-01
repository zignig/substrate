import adapter

" scad processor "
class scad_compile(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print body
		return True

export = scad_compile 
