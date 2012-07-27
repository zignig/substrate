Substrate
=========

Open hardware spooler

I needed a place to store and process and ever increasing number of Open Hardware design files. This is the result.

#Sofware
substrate is written in python 2.7

##Servers

1. [couchdb](http://couchdb.apache.org) for document storage and map/reduce views
2. [rabbitmq](http://rabbitmq.com) for spooling
3. [redis](http://redis.io) for FAST local storage/cache and data editing

##Clients

1. [blender](http://blender.org) rendering and editing
2. [openscad](http://openscad.org) build and assemble

##Basic Use##

I have tried to build a spooler and processor based on some networked servers for distribution so small clients can do a single job 
and not have to worry about local access to any services.

So once you have installed the above servers you need to set up some stuff to get it running. 

first install the following python modules.


pip install pika redis couchdbkit couchapp

Now you have all the python tools you need.

1. find the couch database that you want to process
2. couchapp push http://user:pass@couch.server/database
3. check that the design/robot file design file has been created 

In this directory there is a file called current , this is the document that builds the substrate ( ie mod it for your stuff )

It looks kind of like this:

{
    "robot_version": 0.1, 
    "redis_query": {
        "status": "robot/status", 
        "name": "robot/name", 
        "author": "robot/author", 
        "process": "robot/process", 
        "tags": "robot/tag", 
        "thingi_id": "robot/thingi_id", 
        "derivative": "robot/derivative"
    }, 
    "status_states": {
        "new": "pending", 
        "running": "finished", 
        "pending": "running"
    }, 
    "ttl": 3600, 
    "_rev": "82-7cccca067b884c747cb870c67b62d18e", 
    "mime_routing": {
        "text/scad": "scad", 
        "application/sla": "stl"
    }, 
    "broker": [
        "gateway.terra"
    ], 
    "couch": [
        "http://gateway.terra:5984/"
    ], 
    "mime_queues": {
        "text/scad": [
            "render_to_stl", 
            "extract"
        ], 
        "application/sla": [
            "thumbnail", 
            "large", 
            "rotational", 
            "slice"
        ]
    }, 
    "status_queue": {
        "robot/status": {
            "new": "initialize", 
            "finished": "finished", 
            "pending": "pending"
        }, 
        "robot/process": {
            "download": "download", 
            "author": "author"
        }
    }, 
    "databases": [
        "incoming"
    ], 
    "initialize": "robot/robot_status", 
    "_id": "current", 
    "queues": [
        "stl", 
        "scad", 
        "incoming", 
        "new", 
        "assemble", 
        "recycle", 
        "finished", 
        "pending", 
        "classify", 
        "initialize", 
        "changes", 
        "out", 
        "error", 
        "fetch", 
        "slice"
    ], 
    "ttl_long": 86400
}

Looks kind of long and complicated doesn't it , HMM. yes it does. 

couch , database and broker are the important varibles here.

If these are pointing to your local servers they you should be nearly ready to cook.

cd into the \_attachement folder and run:

./substrate\_bootstrap.py  ( CURRENTLY BROKEN )

If you want to attach to the bl3dr multiverse , this will create a replica of the \_entire\_ incoming database (for now).

PLEASE :)

otherwise upload the "current" document into a couchdb and point config.json at it giving you a local substrate

#Usage

## Browsing

run ./console.py in the \_attachments directory

This should show you a bunch of stuff and give you a python console.

couchdb queries ( ie the robot design ) are mapped into redis with the following stanza:

    "redis_query": {
        "status": "robot/status",
        "name": "robot/name",
        "author": "robot/author",
        "process": "robot/process",
        "tags": "robot/tag",
        "thingi_id": "robot/thingi_id",
        "derivative": "robot/derivative"
    },

-- The console is tab completed --

cq.author() will give you a list of the most prolific authors.

>>cq.author('zignig')

will list the uuids of the documents that I have.

>>cq.load(cq.author('zignig'))

will load all of the couchdb docs ( not including attachments ) into RAM so access is fast.
these keys have a TTL and will disappear in good time (TTL in current).

>>cq.id('1637b134-d1f2-4181-8e21-3863e3325400') 

will yield 

{
    "_id": "1637b134-d1f2-4181-8e21-3863e3325400", 
    "_rev": "5-b2c142c6d573de5b91376e069a5f52fd", 
    "author": "zignig", 
    "name": "YAESU FT-857 head mount", 
    "processed": true, 
    "robot_status": "done", 
    "tags": [
        "3D", 
        "makerbot", 
        "useful"
    ], 
    "thingi_derivative": [], 
    "thingi_download": [
        [
            "/download:3202", 
            "bot-left.stl"
        ], 
        [
            "/download:3203", 
            "bot-right.stl"
        ], 
        [
            "/download:3204", 
            "joiner.stl"
        ], 
        [
            "/download:3205", 
            "top-left.stl"
        ], 
        [
            "/download:3206", 
            "top-right.stl"
        ], 
        [
            "/download:3207", 
            "FT857-mount.blend"
        ]
    ], 
    "thingi_id": 1251, 
    "thumb_url": "http://thingiverse-production.s3.amazonaws.com/renders/a4/26/c3/f5/c6/FT857mount_thumb_large.jpg", 
    "type": "thingiverse", 
    "url": "http://www.thingiverse.com/thing:1251"
}

as a json object

If you want to save a edited json file you can do it a couple of ways

>>cq.save(<doc>,<id>) 

will write the changes back to redis and add it to a dirty set

>>cq.sync() 

will  try so save back to the couchdb or fail and keep it dirty.

OR 

cq.write(<doc>,<id>)

will write to the couchdb and delete the key even on a failed write.

#Spooling 

For this bit you will need three consoles open

1. ./console.py so you can manipulate the queues and data.
2. ./spooler.py so changes in redis and couchdb are constantly spooled in
3. ./combined.py that starts a bunch of threads with individual spool munchers

each of the scripts can be run multiple times with exception of the spooler. 

so running ./stl.py locally or remotely ( with the python libs installed ) will grab process and run files out of the substrate.

This should take all the docs in the database and put them through a state machine defined by the 

    "status_queue": {
        "robot/status": {
            "new": "initialize",
            "finished": "finished",
            "pending": "pending"
        },
        "robot/process": {
            "download": "download",
            "author": "author"
        }

The changes.py script will grab items out of the rabbitmq changes queue and check the robot\_status of each document and send to the next spool based on the current value.

Each of these states has their own spool and script that is bound to it. That script contains a callback that is used to take a rabbitmq message and modify a couchdb-\>redis document and do somthing to it.

have a read of the code :) 

no really.

#Attachments

The initialize script will also take attachments on the documents and route the mime types based on the mime\_routing stanza

    "mime_routing": {
        "text/scad": "scad",
        "application/sla": "stl"
    },

These are spooled into scad and stl queus on rabbitmq. The are in turn consumed by the ./stl.py and ./scad.py scripts.

If the attachments do not have a mapping they are spooled to the classify spool , this script needs to be written ( hint , hint ) :)

#Thoughts 

Using some of the nifty network servers ( redis , rabbitmq and couchdb ) I have managed to process heaps of documents. 

I have set up http://bl3dr.iriscouch.com/incoming as a test bed database if you want to add more files to it please email me 

tigger at interthingy dot com

And I will add you as an editor and with bidirectional replicas we can build somthing really big.

zignig.

P.S. way past bed time.

out PSSSSSSSHT.



