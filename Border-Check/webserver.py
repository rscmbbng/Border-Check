#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013-2014-2015 by psy (epsylon@riseup.net)
"""
import os
import sys
import urllib2
from SocketServer import ForkingMixIn, ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from runpy import run_module
from urlparse import urlparse
from cgi import parse_qs #, parse_header, parse_multipart
import cgi
from options import BCOptions

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

def set_options(self, options):
    self.options = options

def create_options(self, args=None):
    self.optionParser = BCOptions()
    self.options = self.optionParser.get_options(args)
    if not self.options:
        return False
    return self.options

class HttpHandler(BaseHTTPRequestHandler):
    def client_not_allowed(self, addr):
        return False
        if addr == "127.0.0.1":
            return False
        print ("Client not allowed ",addr)
        return True 

    def is_valid_url(self,url):
        import re
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url is not None and regex.search(url)

    def is_online_url(self,url):
       status_reply = urllib2.urlopen("http://downforeveryoneorjustme.com/"+str(url)).read()
       if not 'is up' in status_reply:
           self.online_url = False
       else:
           self.online_url = True

    def serve(self):
        output = ""
        uri = self.path
        tmp = uri.find ('?')
        args = parse_qs(urlparse(uri)[4])
        if 'hostname' in args:
            if (self.is_valid_url(args['hostname'][0])):
                online = self.is_online_url(args['hostname'][0])
                if self.online_url == True:
                    options = create_options(BCOptions)
                    if options.debug == True:
                        print "saving hostname : "+str(args['hostname'])
                    with open('hostname.submit', 'w') as file:
                        file.write(str(args['hostname'][0]))
                else:
                    args['error']='invalid url !'
            else:
                args['error']='invalid url !'
        if tmp != -1 :
            uri = uri[0:tmp]
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
        #print "Request from %s:%d"%self.client_address + "  " + uri
        # print interactions w server
        options = create_options(BCOptions)
        if options.debug == True:
             print "Request from %s:%d"%self.client_address + "  " + uri
        if uri[-1] == '/' or os.path.isdir(file):
            file = file + "/index.py"
        if os.path.isfile(file + ".py"):
            file = file + ".py"
        if file.find("py") != -1:
            modname = file.replace(".py", "")
            cwd = modname[0:modname.rfind('/')] + "/"
            modname = modname.replace("/", ".")
            while modname.find("..") != -1:
                modname = modname.replace("..",".")
            globals = {
                "output": output,
                "http": http,
                "uri": uri,
                "args": args,
                "cwd": cwd,
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
        print '='*45 + "\n", "Data Visualization:\n" + '='*45 + "\n"
        print "Mode: Webserver\n"
        print "Host: http://127.0.0.1:%d/\n\nPath: '%s/web'" % (port, os.getcwd()), "\n"
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print 'Server killed on user request (keyboard interrupt).'

if __name__=="__main__":
    wwwroot = "web"
    httpd = HTTPServer(('', port), HttpHandler)
    print "http://127.0.0.1:%d/ : Serving directory '%s/web'" % (port, os.getcwd())
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'Server killed on user request (keyboard interrupt).'
