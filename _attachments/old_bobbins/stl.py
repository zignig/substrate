#!/usr/bin/env python
import os,subprocess,datetime
import pika,couchdbkit,json
import yaml,adapter,traceback

def now():
    return  datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%Sz')

def callback(ch, method, properties, body):
	print 'stl '+body
	ch.basic_ack(delivery_tag = method.delivery_tag)
	return 

	server = ch.couch
	database = ch.cq.db
	ref = json.loads(body)
	cid = ref['id']
	D = ch.cq.cur_id(cid)
	att = ref['value'][1]
	name  = att.split('.')[0]
	#print ref 
	if att.split('.')[-1] == 'stl':
		#print D
		f = database.fetch_attachment(cid,att,stream=True)
		data = f.read()
		f2 = open('cache/'+att,'wb')
		f2.write(data)
		f2.close()
		command = 'blender -b  utils' + os.sep + 'render.blend -P utils' + os.sep + 'viz.py -- ' + stl_dir + os.sep + att + ' ' + render_dir + os.sep + name + '_l.png'
		print(command)
		try:
			subprocess.check_output(command.split())
			attachment = open(render_dir+os.sep+name+'_l.png')
	 		database.put_attachment(D,attachment,name+'_l.png','image/png')
			# get doc again incas it has changed
			D['large'] = name+'.png'
			D['updated_at'] = now()
			database.save_doc(D)
		except:
			traceback.print_stack()
			print "FAIL on render"
	ch.basic_ack(delivery_tag = method.delivery_tag)

stl_dir = 'cache'
render_dir = 'cache'

if __name__ == '__main__':
	cq = adapter.couch_queue()
	cq.run_queue('stl',callback)
