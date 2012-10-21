#!/usr/bin/python -i 

import torrent

a = torrent.RTorrentXMLRPCClient('http://127.0.0.1:5000')
li = a.download_list()
for i in li:
	print a.d.name(i)

# functions 
# a.d.start(id)
# a.d.stop(id)
# a.d.erase(id)
