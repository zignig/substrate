substrate
=========

Open hardware spooler

I needed a place to store and process and ever increasing number of Open Hardware design files. This is the result.

#Sofware
substrate is written in python 2.7
##Servers
1. (couchdb)[http://couchdb.apache.org] for document storage and map/reduce views
2. (rabbitmq)[http://rabbitmq.com] for spooling
3. (redis)[http://redis.io] for FAST local storage/cache and data editing
##Clients
1. (blender)[http://blender.org] rendering and editing
