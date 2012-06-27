#!/usr/bin/python -i
import os,subprocess
import pika,couchdbkit,json
import yaml,adapter,traceback
import readline , rlcompleter
readline.parse_and_bind('tab:complete')
print('bl3dr console')
cq = adapter.couch_queue()
print('base object = cq')
