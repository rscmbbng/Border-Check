#!/usr/local/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
import os, sys, time, re, traceback
from urlparse import urlparse
try:
    import pygeoip
except:
    print "\nError importing: pygeoip lib. \n\nOn Debian based systems, please try like root:\n\n $ apt-get install python-geoip\n"
    sys.exit(2)
try:
    import sqlite3
except:
    print "\nError importing: sqlite3 lib. \n\nOn Debian based systems, please try like root:\n\n $ apt-get install sqlite3\n"
    sys.exit(2)

import subprocess, socket, thread
from options import BCOptions
from webserver import BorderCheckWebserver

# set to emit debug messages about errors (0 = off).
DEBUG = 1

class bc(object):
    """
    BC main Class
    """
    def __init__(self):
        """
        Init defaults
        """
        self.browser = "" # "F" Firefox / "C" Chrome
        self.browser_path = ""
        self.url = ""
        self.old_url = ""

    def set_options(self, options):
        """
        Set program options
        """
        self.options = options

    def create_options(self, args=None):
        """
        Create options for OptionParser
        """
        self.optionParser = BCOptions()
        self.options = self.optionParser.get_options(args)
        if not self.options:
            return False
        return self.options

    def try_running(self, func, error, args=None):
        """
        Try running a function and print some error if it fails and exists with a fatal error.
        """
        options = self.options
        args = args or []
        try:
            return func(*args)
        except Exception as e:
            print("[Error] - Something wrong fetching urls. Aborting..."), "\n"
            if DEBUG:
                traceback.print_exc()
                sys.exit(2)

    def check_root(self):
        """     
        Check root permissions
        """
        if not os.geteuid()==0:
            sys.exit("\nOnly root can run this script...\n")

    def check_browser(self):
        """
        Check browsers used by system
        """
        if sys.platform == 'darwin':
            f_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Firefox/Profiles')
            c_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Google/Chrome/Default/History')
            chromium_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Chromium/Default/History')
            s_osx = os.path.join(os.path.expanduser('~'), 'Library/Safari/History.plist')
            try:
                if os.path.exists(f_osx):
                    if len(os.listdir(f_osx)) > 2:
                        print 'You have multiple profiles, choosing the last one used'
                        #filtering the directory that was last modified
                        all_subdirs = [os.path.join(f_osx,d)for d in os.listdir(f_osx)]
                        try:
                            all_subdirs.remove(os.path.join(f_osx,'.DS_Store')) #throwing out .DS_store
                        except:
                            pass
                        latest_subdir = max(all_subdirs, key=os.path.getmtime)
                        osx_profile = os.path.join(f_osx, latest_subdir)
                        self.browser_path = os.path.join(osx_profile, 'places.sqlite')
                    else:
                        for folder in os.listdir(f_osx):
                            if folder.endswith('.default'):
                                osx_default = os.path.join(f_osx, folder)
                                self.browser_path = os.path.join(osx_default, 'places.sqlite')
                                #print "Setting:", self.browser_path, "as history file"
                    self.browser = "F"
                elif os.path.exists(c_osx):
                    self.browser = "C"
                    self.browser_path = c_osx
                elif os.path.exists(chromium_osx):
                    self.browser = "CHROMIUM"
                    self.browser_path = chromium_osx
                elif os.path.exists(s_osx):
                    self.browser = "S"
                    self.browser_path = s_osx
            except:
                print "Warning: None of the currently supported browsers (Firefox, Chrome, Chromium, Safari) are installed."

        elif sys.platform.startswith('linux'):
            f_lin = os.path.join(os.path.expanduser('~'), '.mozilla/firefox/') #add the next folder
            c_lin = os.path.join(os.path.expanduser('~'), '.config/google-chrome/History')
            chromium_lin = os.path.join(os.path.expanduser('~'), '.config/chromium/Default/History')
            if os.path.exists(f_lin):
                #missing multiple profile support
                for folder in os.listdir(f_lin):
                    if folder.endswith('.default'):
                        lin_default = os.path.join(f_lin, folder)
                        self.browser_path = os.path.join(lin_default, 'places.sqlite')
                        self.browser = "F"
            elif os.path.exists(c_lin):
                self.browser = "C"
                self.browser_path = c_lin
            elif os.path.exists(chromium_lin):
                self.browser = "CHROMIUM"
                self.browser_path = chromium_lin
        print "Browser Options:\n" + '='*45 + "\n"
        print "On use:", self.browser, "\n"
        print "Version:", "\n"
        print "History path:", self.browser_path, "\n"

    def getURL(self):
        """
        Set urls to visit
        """
        if self.browser == "F": #Firefox history database
            conn = sqlite3.connect(self.browser_path)
            c = conn.cursor()
            c.execute('select url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
            url = c.fetchone()

        elif self.browser == "C" or self.browser == "CHROMIUM": #Chrome/Chromium history database
            #Hack that makes a copy of the locked database to access it while Chrome is running.
            #Removes the copied database afterwards
            import filecmp
            a = self.browser_path + 'Copy'
            if os.path.exists(a):
                if filecmp.cmp(self.browser_path, a) == False:
                    os.system('rm "' + a+'"')
                    os.system('cp "' + self.browser_path + '" "' + a + '"')
            else:
                os.system('cp "' + self.browser_path + '" "' + a + '"')
    
            conn = sqlite3.connect(a)
            c = conn.cursor()
            c.execute('select urls.url, urls.last_visit_time FROM urls ORDER BY urls.last_visit_time DESC')
            url = c.fetchone()
            os.system('rm "' + a + '"')

        elif self.browser == "S": #Safari history database
            try:
                from biplist import readPlist
            except:
                print "\nError importing: biplist lib. \n\nTo run BC with Safari you need the biplist Python Library:\n\n $ pip install biplist\n"

            plist = readPlist(self.browser_path)
            url = [plist['WebHistoryDates'][0][''], '']

        else: # Browser not allowed
            print "\nSorry, you haven't a compatible browser\n\n"
            exit(2)
        
        self.url = url
        return url[0]

    def traces(self):
        # Set database (GeoLiteCity)
        self.geoip= pygeoip.GeoIP('GeoLiteCity.dat')

        print '='*45 + "\n", "Current target:\n" + '='*45 + "\n"
        print "URL:", self.url[0], "\n"
        #url = urlparse(self.url[0]).netloc 
        url = urlparse(self.getURL()).netloc #changed this for prototyping
        url = url.replace('www.','') #--> doing a tracert to example.com and www.example.com yields different results.
        url_ip = socket.gethostbyname(url)
        print "Host:", url, "\n"
        if url != self.old_url:
            count = 1
            if sys.platform.startswith('linux'):
                # using udp
                try:
                    print "Method: udp\n"
                    a = subprocess.Popen(['lft', '-S', '-n', url_ip], stdout=subprocess.PIPE)
                # using tcp
                except:
                    try:
                        print "Method: tcp\n"
                        a = subprocess.Popen(['lft', '-S', '-n', '-E', url_ip], stdout=subprocess.PIPE)
                    except:
                        print "Error: network is not responding correctly. Aborting...\n"
                        sys.exit(2)
            else:
                # using udp     
                try:            
                    print "Method: udp\n"
                    a = subprocess.Popen(['lft', '-S', '-n', '-u', url_ip], stdout=subprocess.PIPE)
                # using tcp
                except:     
                    try:    
                        print "Method: tcp\n"
                        a = subprocess.Popen(['lft', '-S', '-n', '-E', url_ip], stdout=subprocess.PIPE)
                    except: 
                        print "Error: network is not responding correctly. Aborting...\n"
                        sys.exit(2)
            logfile = open('logfile', 'a')
            print '='*45 + "\n" + "Packages Route:\n" + '='*45
            for line in a.stdout:
                logfile.write(line)
                parts = line.split()
                for ip in parts:
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
                        record = self.geoip.record_by_addr(ip)
                        #print record
                        try:
                            if record.has_key('country_name') and record['city'] is not '':
                                country = record['country_name']
                                city = record['city']
                                print "Trace:", count, "->", ip, "->", city, "->", country
                                count+=1
                            elif record.has_key('country_name'):
                                country = record['country_name']
                                print "Trace:", count, "->", ip, "->", country
                                count+=1
                        except:
                            print "Trace:", count, "->", "Not allowed"
                            count+=1
            logfile.close()
            print '='*45 + "\n"
            print "Status: Waiting for new urls ...\n"

    def getGEO(self):
        """
        Get Geolocation database (http://dev.maxmind.com/geoip/legacy/geolite/)
        """
        print "="*45 + "\n", "GeoIP Options:\n" + '='*45 + "\n"
        # Download, extract and set geoipdatabase
        if not os.path.exists('GeoLiteCity.dat'):
            import urllib, gzip
            geo_db_path = '/'
            try:
                print "Downloading GeoIP database...\n"
                urllib.urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                                   'GeoLiteCity.gz')
            except:
                try:
                    urllib.urlretrieve('http://xsser.sf.net/map/GeoLiteCity.dat.gz',
                                        'GeoLiteCity.gz')
                except:
                    print("[Error] - Something wrong fetching GeoIP maps from the Internet. Aborting..."), "\n"
                    sys.exit(2)
            f_in = gzip.open('GeoLiteCity.gz', 'rb')
            f_out = open('GeoLiteCity.dat', 'wb')
            f_out.write(f_in.read())
            f_in.close()

            os.remove('GeoLiteCity.gz')
        print "Database: GeoLiteCity\n"

    def run(self, opts=None):
        """
        Run BorderCheck
        """
        # set options
        if opts:
            options = self.create_options(opts)
            self.set_options(options)
        options = self.options
        p = self.optionParser
        # banner
        print('='*75)
        print(str(p.version))
        print('='*75)
        # root checker
        root = self.try_running(self.check_root, "\nInternal error checking root permissions.")
        # extract browser type and path
        browser = self.try_running(self.check_browser, "\nInternal error checking browser files path.")
        # extract url
        url = self.try_running(self.getURL, "\nInternal error getting urls from browser's database.")
        # set geoip database
        geo = self.try_running(self.getGEO, "\nInternal error setting geoIP database.")
        # start web mode (on a different thread)
        try: 
            thread.start_new_thread(BorderCheckWebserver(self))
        except:
            print "Error: unable to start thread"
            pass
        # run traceroutes
        traces = self.try_running(self.traces, "\nInternal error tracerouting.")

if __name__ == "__main__":
    app = bc()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
