# -*- coding: utf-8 -*-

import adapter

" template spooler "
class svg_thumb(adapter.worker):
    def __init__(self,queue):
        adapter.worker.__init__(self,queue)
    
    def consume(self,body):
        print body
        return True

export = svg_thumb