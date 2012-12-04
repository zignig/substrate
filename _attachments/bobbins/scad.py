#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import adapter

render_dir = 'cache'
scad_dir = 'cahce'

def callback(ch, method, properties, body):
	ref = json.loads(body)
	print ref	
	cid = ref['id']
	D = ch.cq.db[cid]
	#print D
	#D['robot_status'] = 'new'
	#server['stl'].save_doc(D)
	att = ref['value'][1]
	name  = att.split('.')[0]
	print name
	print cid,att
	if att.split('.')[-1] == 'scad':
		f = ch.cq.db.fetch_attachment(cid,att,stream=True)
		data = f.read()
		f2 = open('cache/'+att,'wb')
		f2.write(data)
		f2.close()
		#command = 'blender -b  utils' + os.sep + 'render.blend -P utils' + os.sep + 'viz.py -- ' + stl_dir + os.sep + att + ' ' + render_dir + os.sep + name + '.png'
		command = 'openscad ' + scad_dir + os.sep + att + ' -s ' + render_dir + os.sep + name + '.stl'
		print(command)
		try:
			subprocess.check_output(command.split())
			attachment = open(render_dir+os.sep+name+'.stl').read()
			ch.cq.db.put_attachment(D,attachment,name+'.stl','application/sla',headers={'processed':"true"})
			ch.cq.db.save_doc(D)
		except:
			print "fail"
	ch.basic_ack(delivery_tag = method.delivery_tag)

cq = adapter.couch_queue()
cq.run_queue('scad',callback)
