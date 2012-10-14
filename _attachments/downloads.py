#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback,urllib2
import socket

timeout = 10
#socket.setdefaulttimeout(timeout)

def grab(ch,D,ref):
		req = urllib2.urlopen(ref['url'])
		print ref['url']
		#print req.info()
		data = req.read()
		#print len(data)
		ch.cq.redis.delete('id:'+ref['_id'])
		mime =  req.info()['Content-type']
		#print mime
		#print json.dumps(D,indent=4,sort_keys=True)	
		name = 'cache/'+ref['name']
		f = open(name,'w')
		f.write(data)
		f.close()
		f = open(name)
		ch.cq.db.put_attachment(D,f,ref['name'],req.info()['Content-type'])
		f.close()
	
def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		cid = ref['_id']
		D = ch.cq.id(cid) 
		if '_attachments' in D:
			att = D['_attachments']
			if att.has_key(ref['name']):
				print 'alread got '+ref['name']
				#grab(ch,D,ref)
			else:
				grab(ch,D,ref)
		else:
			grab(ch,D,ref)
	except:
		tb = traceback.format_exc()
		print tb
		#ch.basic_publish('','error',body+'\n\n'+str(tb))
	ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
		cq = adapter.couch_queue()
		cq.run_queue('download',callback)
