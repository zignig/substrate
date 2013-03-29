#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time,StringIO

from PIL import Image

#size = (320,240)
size = (200,150)
#size = (80,60)

def process_image(val):
	doc = cq.db.get(val['id'])
	r = cq.db.fetch_attachment(val['id'],val['value'])
	image = Image.open(StringIO.StringIO(r))
	print image.size
	if image.size[0] > 200:
		image.thumbnail(size,Image.ANTIALIAS)
		doc['thumb'] = 'thumb.jpg'
		doc['robot_status'] = 'done'
		b = cq.db.save_doc(doc)
		data = StringIO.StringIO()
		image.save(data,"JPEG")
		cq.db.put_attachment(doc,data,'thumb.jpg')
		print doc
		return image
	else:
		print 'too small'
		

def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		key = method.routing_key
		print key,ref
		process_image(ref)
		ch.basic_ack(delivery_tag = method.delivery_tag)
	except:
		print body
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
def get_all(mime_type='image/png'):
	a = cq.db.view('robot/mime_types',reduce=False,key=mime_type).all()
	for i in a:
		cq.channel.basic_publish('mime_types','mime_type:'+mime_type,json.dumps(i))	

def grab():
	mes = cq.channel.basic_get(queue='mime_type:image/jpeg')
	cq.channel.basic_ack(delivery_tag = mes[0].delivery_tag)
	return json.loads(mes[2])
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('mime_type:image/jpeg',callback)
