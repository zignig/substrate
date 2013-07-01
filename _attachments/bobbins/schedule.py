import adapter
from apscheduler.scheduler import Scheduler

" scheduler "
class scheduler(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
		self.sched = Scheduler()
		self.sched.start()
	
	def consume(self,body):
		print body
		if 'jobs' in body:
			jobs = self.sched.get_jobs()
			for i in jobs:
				print i
		if 'seconds' in body:
			job = self.sched.add_interval_job(self.echo,seconds=body['seconds'],kwargs=body)
			print job
			self.channel.basic_publish('command','notify',adapter.encode({'name':'schedule'}))

	def echo(self,**kwargs):
		if 'exchange' in kwargs:
			if 'key' in kwargs:
				self.channel.basic_publish(kwargs['exchange'],kwargs['key'],adapter.encode(kwargs['mess']))


export = scheduler 
