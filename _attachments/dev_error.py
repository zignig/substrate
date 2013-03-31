#!/usr/bin/python
import adapter

class dev_error(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print body

w = dev_error('dev_error')
w.start()
