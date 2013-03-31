#!/usr/bin/python 

import web
import couchdbkit
import adapter
import redis,json,time

cq = adapter.couch_queue()
webdb = redis.Redis(cq.local_config['redis'],db=1)
web.config.debug =True 
web_ttl = 2 
frag_spooler = 'web_fragments'
cq.channel.queue_declare(queue=frag_spooler)

tmp = 	'/id/(.+)','ident',
urls = (
	'/','index',
	'/(.+)','base'
)


render = web.template.render('templates')
app = web.application(urls,globals())
cq.message('/',key=frag_spooler)
queries = cq.config['redis_query'].keys()
cq.channel.queue_declare(queue='frag_'+'known')
for i in queries:
	#cq.channel.queue_declare(queue='frag_'+i)
	cq.channel.queue_bind(queue='frag_'+'known',exchange='fragments',routing_key=i)
cq.channel.queue_bind(queue='frag_'+'known',exchange='fragments',routing_key='id')

class index:
	def GET(self):
		return render.page(['/'],queries,False) 

class ident:
	def GET(self,name):
		print name
		return json.dumps(cq.id(name),indent=4)

class base:
 def GET(self,name):
	if webdb.exists('complete:'+name):
		print 'cached '+name
		#page = json.loads(webdb.get('complete:'+name))
		#return render.page(page[0],page[1],False)
		return webdb.get('complete:'+name)
	else:
		if webdb.exists('pending:'+name):
			page = json.loads(webdb.get('pending:'+name))
		else:
			webdb.set('pending:'+name,json.dumps([['pending'],['/'+name]]))
			webdb.expire('pending:'+name,4)
		tmp = name.split('/')
		print tmp
		if len(tmp) > 0:
			val = tmp[0]
			if val in queries:
				print 'match -> '+val 
				cq.message(json.dumps([name,tmp]),key=val,ex='fragments')
			else:
				cq.message(json.dumps(tmp),key='unknown',ex='fragments')
		time.sleep(0.5)
		page = json.loads(webdb.get('pending:'+name))
		breadcrumbs = page[0]
		the_list = page[1]
		pending = False
		print breadcrumbs
		if len(breadcrumbs) >= 1:
			for i in range(len(the_list)):
					if webdb.exists('id:'+the_list[i]):
						cur = str(the_list[i])
						the_list[i] = webdb.get('id:'+cur)
					else:
						pending = True
						webdb.set('id:'+the_list[i],json.dumps([['pending'],[the_list[i]]]))
						webdb.expire('id:'+the_list[i],web_ttl)
						cq.message(json.dumps(['id',the_list[i]]),key='id',ex='fragments')
		if pending:
			return render.page(breadcrumbs,the_list,True)
		else:
			webdb.set('complete:'+name,render.page(breadcrumbs,the_list,False))
			webdb.expire('complete:'+name,86400)
			return render.page(breadcrumbs,the_list,False)
			

if __name__ == "__main__":
	app.run()
