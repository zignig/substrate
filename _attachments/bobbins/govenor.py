import adapter,requests

" spindle govenor "
class govenor(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
		self.bobbins = []
	
	def consume(self,body):
		print 'govenor gets ',body
		if 'status' in body:
			print 'status'
			get_queue_stat(self.cq)
		if 'info' in body:
			print self.bobbins
		if 'spindle' in body:
			d = get_queue_stat(self.cq)
			for j in d.keys():
				print 'start '+j
				self.cq.channel.basic_publish('',body['spindle']['queue'],adapter.encode({'start_bobbin':j}))
		if 'bobbin' in body:
			self.bobbins.append(body['bobbin'])
		if 'start_bobbin' in body:
			self.cq.channel.basic_publish('command','spindle',adapter.encode(body))
			self.cq.channel.basic_publish('logging','info',adapter.encode(body))

export = govenor 

def get_queue_stat(cq):
    s = requests.Session()
    cred = cq.local_config['broker_cred']
    s.auth = (cred[0],cred[1])
    broker = cq.config['broker'][0]
    r = s.get('http://'+broker+':55672/api/queues')
    queues = r.json()
    bobbin_list = {} 
    for i in queues:
        message_count = i['messages_ready']
        if message_count > 0:
            name = i['name']
            " don't respool yourself "
            if name != 'govenor' and name[0:3] !='amq':
                bobbin_list[name] = message_count
    return bobbin_list

