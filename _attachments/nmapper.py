#!/usr/bin/env python
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import redis,json,time
import ipcalc
import xml.dom.minidom
import commands

#cq = adapter.couch_queue()
#webdb = redis.Redis(cq.local_config['redis'],db=1)

def host(host_dom):
	status = host_dom.getElementsByTagName("status")[0]
	updown = status.getAttribute('state')
	if updown == 'up':
		addr = host_dom.getElementsByTagName("address")[0].getAttribute('addr')
		name = ''
		names = host_dom.getElementsByTagName("hostname")
		if len(names) > 0:
			name = names[0].getAttribute('name')
		return {'host':[addr,name]}
		

def get_subnet(subnet):
	net = ipcalc.Network(subnet)
	doc = commands.getoutput('nmap -T insane -oX - -sP '+subnet)
	dom = xml.dom.minidom.parseString(doc)
	hosts = dom.getElementsByTagName("host")	
	host_list = []
	for i in hosts:
		val = host(i)
		if val:
			host_list.append(val)
	return host_list

def get_host(host):
	print host
	doc = commands.getoutput('nmap -T insane -oX - '+host[0])
	dom = xml.dom.minidom.parseString(doc)

def callback(ch, method, properties, body):
	try:
		ref = json.loads(body)
		key = method.routing_key
		print ref
		if 'subnet' in ref.keys():
			print ref['subnet'] 
			hosts = get_subnet(ref['subnet'])
			for i in hosts:
				ch.basic_publish('','mapping',json.dumps(i))
				print i
		if 'host' in ref.keys():
			get_host(ref['host'])
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
	except:
		print body
		ch.basic_ack(delivery_tag = method.delivery_tag)
	
if __name__ == "__main__":
	cq = adapter.couch_queue()
	cq.run_queue('mapping',callback)
