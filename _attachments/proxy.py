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
		return render.page(['/'],queries) 

class ident:
	def GET(self,name):
		print name
		return json.dumps(cq.id(name),indent=4)

class base:
 def GET(self,name):
	if webdb.exists('complete:'+name):
		print 'cached '+name
		page = json.loads(webdb.get('complete:'+name))
		return render.page(page[0],page[1])
	else:
		#webdb.set(name,json.dumps([['pending'],['/'+name]]))
		#webdb.expire(name,web_ttl)
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
		page = json.loads(webdb.get(name))
		breadcrumbs = page[0]
		the_list = page[1]
		pending = False
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
			return render.page(breadcrumbs,the_list)
		else:
			data = json.dumps([breadcrumbs,the_list])
			print 'should be saving' 
			webdb.set('complete:'+name,"test")
			return render.page(breadcrumbs,the_list)
			

if __name__ == "__main__":
	app.run()
