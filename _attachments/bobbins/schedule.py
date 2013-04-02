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
		if 'seconds' in body:
			self.sched.add_interval_job(self.echo,seconds=body['seconds'],args=body)

	def echo(self,val):
		print val 
export = scheduler 
