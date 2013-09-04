#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
import os
import sys
from SocketServer import ForkingMixIn, ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from runpy import run_module
from urlparse import urlparse
from cgi import parse_qs #, parse_header, parse_multipart
import cgi

port = 8080
wwwroot = "web/"
http = {} # global storage

class ForkingTCPServer(ForkingMixIn, HTTPServer): pass
class ThreadingTCPServer(ThreadingMixIn, HTTPServer): pass

def print_exception(type=None, value=None, tb=None, limit=None):
	if type is None:
		type, value, tb = sys.exc_info()
	import traceback
	ret = "<html><body><h2>Traceback (most recent call last):<h2 />"
	ret += "<pre>"
	list = traceback.format_tb(tb, limit) + \
		traceback.format_exception_only(type, value)
	ret += "exception error"
	ret += "%s: %s<br/>\n" % ( ("\n".join(list[:-1])), (list[-1]))
	ret +="</body></html>"
	del tb
	return ret

class HttpHandler(BaseHTTPRequestHandler):
                
	# TODO: whitelist out there
	def client_not_allowed(self, addr):
		return False
		if addr == "127.0.0.1":
			return False
		print ("Client not allowed ",addr)
		return True 

	def serve(self):
		output = ""
		uri = self.path
		tmp = uri.find ('?')
		args = parse_qs(urlparse(uri)[4])

		#from ipdb import set_trace;set_trace()
		if tmp != -1:
			uri = uri[0:tmp]
			for a in uri[tmp:-1].split("&"):
				sep = a.find ("=")
				if sep != -1:
					print "%s)(%s"%(a[0:sep],a[sep:-1])
					args[a[0:sep]]=a[sep:-1]
		
		file = wwwroot + "/" + uri
		if self.client_not_allowed (self.client_address[0]):
			self.wfile.write ("HTTP/1.0 503 Not allowed\r\n\r\nYou are not whitelisted")
			return
		content = ""
		try:
			ctype,pdict = cgi.parse_header(self.headers.getheader('content-type'))
			print "CTYPE IS ",ctype
			if ctype == 'multipart/form-data':
				query = cgi.parse_multipart(self.rfile, pdict)
				content = query.get('upfile')
		except:
			pass
		print "Request from %s:%d"%self.client_address+"  "+uri
		if uri[-1] == '/' or os.path.isdir(file):
			file = file + "/index.py"
		if os.path.isfile(file+".py"):
			file = file + ".py"
		if file.find("py") != -1:
			modname = file.replace(".py", "")
			cwd = modname[0:modname.rfind('/')]+"/"
			modname = modname.replace("/", ".")
			while modname.find("..") != -1:
				modname = modname.replace("..",".")
			globals = {
				"output": output,
				"http": http,
				"uri": uri,
				"args": args,
				"cwd": cwd,
				"headers": self.headers,
				"content": content
			}
			try:
				a = run_module(modname, init_globals=globals)
				output = a["output"]
			except:
				output = print_exception()
		else:
			try:
				f = open (file, "r")
				output = f.read ()
				f.close ()
			except:
				output = "404"
		if output == "404":
			self.wfile.write ("HTTP/1.0 404 Not found\r\n\r\n")
		else:
			self.wfile.write ("HTTP/1.0 200 OK\r\n\r\n")
			self.wfile.write (output)

	def do_POST (self):
		self.serve ()

	def do_GET (self):
		self.serve ()

class BorderCheckWebserver():
    def __init__(self, ref, *args):
	HttpHandler.ref = ref
        httpd = HTTPServer(('', port), HttpHandler)
        print "http://127.0.0.1:%d/ : Serving directory '%s/www'" % (port, os.getcwd())
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print 'Server killed on user request (keyboard interrupt).'

if __name__=="__main__":
    wwwroot = "www"
    httpd = HTTPServer(('', port), HttpHandler)
    print "http://127.0.0.1:%d/ : Serving directory '%s/www'" % (port, os.getcwd())
    
    try:
    	httpd.serve_forever()
    except KeyboardInterrupt:
    	print 'Server killed on user request (keyboard interrupt).'
