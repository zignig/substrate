import adapter,requests

" spindle govenor "
class govenor(adapter.worker):
    def __init__(self,queue):
        adapter.worker.__init__(self,queue,runout=False)
        #self.qi = queue_info(self.cq)
        self.bobbins = []
    
    def consume(self,body):
        print 'govenor gets ',body
        if 'status' in body:
            print 'status'
            get_queue_stat(self.cq)
        if 'info' in body:
            print self.bobbins
        #if 'spindle' in body:
            #d = self.qi.get_queue_stat()
            #for j in d.keys():
             #  print 'start '+j
              #  self.cq.channel.basic_publish('',body['spindle']['queue'],adapter.encode({'start_bobbin':j}))
#        if 'action' in body:
#            length = self.qi.queue_length(body['name'])
#            print length
#            if length >= 0:
#                print 'start' + body['name']
#                self.cq.channel.basic_publish('command','notify',adapter.encode({'start_bobbin':body['name']}))
        if 'bobbin' in body:
            self.bobbins.append(body['bobbin'])
        if 'start_bobbin' in body:
            self.cq.channel.basic_publish('command','spindle',adapter.encode(body))
            self.cq.channel.basic_publish('logging','info',adapter.encode(body))

export = govenor 
class queue_info:
    def __init__(self,cq):
        self.cq = cq
        self.s = requests.Session()
        cred = cq.local_config['broker_cred']
        self.s.auth = (cred[0],cred[1])
        self.broker = cq.config['broker'][0]
        
    def req(self,path=None):
        r = self.s.get('http://'+self.broker+':15672/api/'+path)
        return r.json()
    
    def queue_length(self,queue_name):
        queue = self.req('queues/%2f/'+queue_name)
        return queue['messages_ready']
        
    def get_queue_stat(self):
        queues = self.req('queues')
        print queues
        bobbin_list = {} 
        for i in queues:
            message_count = i['messages_ready']
            if message_count > 0:
                name = i['name']
                " don't respool yourself "
                if name != 'govenor' and name[0:3] !='amq':
                    bobbin_list[name] = message_count
        return bobbin_list

