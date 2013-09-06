import adapter

import os,subprocess
import pika,couchdbkit,json
import yaml,traceback
import redis,json,time,StringIO

from PIL import Image

#size = (320,240)
size = (200,150)
#size = (80,60)

def process_image(val,cq):
    doc = cq.db.get(val['_id'])
    r = cq.db.fetch_attachment(val['_id'],val['att'])
    image = Image.open(StringIO.StringIO(r))
    print image.size
    if image.size[0] > 200:
        image.thumbnail(size,Image.ANTIALIAS)
        doc['thumb'] = 'thumb.jpg'
        doc['robot_status'] = 'done'
        if 'file_info' in doc:
          doc['file_info']['image'] = {val['att']:'thumb.jpg'}
        else:
          doc['file_info'] = {}
          doc['file_info']['image'] = {val['att']:'thumb.jpg'}
        b = cq.db.save_doc(doc)
        data = StringIO.StringIO()
        image.save(data,"JPEG")
        cq.db.put_attachment(doc,data,'thumb.jpg')
        print doc
        return image
    else:
        print 'too small'


" thumbnail spooler "
class thumbnail(adapter.worker):
	def __init__(self,queue):
		adapter.worker.__init__(self,queue)
	
	def consume(self,body):
		print 'thumbnail => '+str(body)
		try:
			process_image(body,self.cq)
		except:
			print 'fail'

export = thumbnail 
