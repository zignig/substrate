#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback,time,string,StringIO

def callback(ch, method, properties, body):
	print 'classify '+body
	ch.basic_ack(delivery_tag = method.delivery_tag)
	return

	server = ch.couch
	ref = json.loads(body)
	cid = ref['id']
	# record in redis
	ch.cq.redis.zincrby('mime_types',ref['value'][0],1)
	ch.cq.redis.hset('classify',cid,ref)
	ext = string.split(ref['value'],'.')
	if ext[-1] == 'scad':
		try:
			print cid
			data = ch.cq.db.fetch_attachment(cid,ref['value'])
			doc = ch.cq.db.get(cid)	
			ch.cq.db.put_attachment(doc,StringIO.StringIO(data),ref['value'],'text/scad')
		except:
			print "FAIL" 
	ch.basic_ack(delivery_tag = method.delivery_tag)
	#time.sleep(1)
	

if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('mime_type:application/octet-stream',callback)
