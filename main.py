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

import subprocess, socket
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

    def check_browser(self):
        """
        Check browsers used by system
        """
        if sys.platform == 'darwin':
            f_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Firefox/Profiles')
            c_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Google/Chrome/Default/History')
            chromium_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Chromium/Default/History')
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
                        osx_self.browser_path = os.path.join(osx_profile, 'places.sqlite')
                        self.browser_path = osx_self.browser_path
                    else:
                        for folder in os.listdir(f_osx):
                            if folder.endswith('.default'):
                                osx_default = os.path.join(f_osx, folder)
                                osx_self.browser_path = os.path.join(osx_default, 'places.sqlite')
                                print "Setting:", osx_self.browser_path, "as history file"
                                self.browser_path = osx_self.browser_path
                    self.browser = "F"
                elif os.path.exists(c_osx):
                    self.browser = "C"
                    self.browser_path = c_osx
                elif os.path.exists(chromium_osx):
                    self.browser = "CHROMIUM"
                    self.browser_path = chromium_osx
            except:
                print "Warning: No Firefox, Chrome or Chromium installed."

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

    def getURL(self):
        """
        Set urls to visit
        """
        print "Browser database:", self.browser_path, "\n"
        if self.browser == "F": #Firefox history database
            conn = sqlite3.connect(self.browser_path)
            c = conn.cursor()
            c.execute('select url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
        elif self.browser == "C" or self.browser == "CHROMIUM": #Chrome/Chromium history database
            import filecmp
            a = self.browser_path + 'Copy'
            if os.path.exists(a):
                if filecmp.cmp(self.browser_path, a) == False:
                    os.system('rm ' + a)
                    os.system('cp "' + self.browser_path + '" "' + a + '"')
                else:
                    os.system('cp "' + self.browser_path + '" "' + a + '"')
                conn = sqlite3.connect(a)
                c = conn.cursor()
                c.execute('select urls.url, urls.last_visit_time FROM urls ORDER BY urls.last_visit_time DESC')
                os.system('rm "' + a + '"')
        else: # Browser not allowed
            print "\nSorry, you haven't a compatible browser\n\n"
            exit(2)
        url = c.fetchone()
        self.url = url
        print "Fetching URL:", self.url[0], "\n"
        return url[0]

    def traces(self):
        while True:
            url = urlparse(self.url[0]).netloc
            url = url.replace('www.','') #--> doing a tracert to example.com and www.example.com yields different results.
            url_ip = socket.gethostbyname(url)
            if url != self.old_url:
                count = 0
                a = subprocess.Popen(['lft', '-S', '-n', '-E', url_ip], stdout=subprocess.PIPE) # -> using tcp
                #a = subprocess.Popen(['lft', '-S', '-n', '-u', url_ip], stdout=subprocess.PIPE) # -> using udp
                logfile = open('logfile', 'a')

                for line in a.stdout:
                    logfile.write(line)
                    parts = line.split()
                    for ip in parts:
                        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
                            record = geoip.record_by_addr(ip)
                            #print record
                            try:
                                if record.has_key('country_name') and record['city'] is not '':
                                    country = record['country_name']
                                    city = record['city']
                                    print count, "While surfing you got to "+ip+" which is in "+city+", "+country
                                elif record.has_key('country_name'):
                                    country = record['country_name']    
                                    print count, "While surfing you got to "+ip+" which is in "+country
                                    time.sleep(0.3)
                                    count+=1
                            except:
                                print "Not more records. Aborting...", "\n"
                                exit()

            self.old_url = url
            print "old url = ", self.old_url
            logfile.close()
            time.sleep(5)

    def getGEO(self):
        """
        Get Geolocation database (http://dev.maxmind.com/geoip/legacy/geolite/)
        """
        # Download and extract database
        import urllib
        geo_db_path = "geo/"
        if not os.path.exists(os.path.dirname(geo_db_path)):
            os.makedirs(os.path.dirname(geo_db_path))
        try:
            print "Downloading GeoIP database...\n"
            urllib.urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                                geo_db_path+'GeoLiteCity.gz')
        except:
            try:
                urllib.urlretrieve('http://xsser.sf.net/map/GeoLiteCity.dat.gz',
                                    geo_db_path+'GeoLiteCity.gz')
            except:
                print("[Error] - Something wrong fetching GeoIP maps from the Internet. Aborting..."), "\n"
                sys.exit(2)
        else:
            f_in = gzip.open(geo_db_path+'GeoLiteCity.gz', 'rb')
            f_out = open(geo_db_path, 'wb')
            f_out.write(f_in.read())
            f_in.close()
            os.remove(geo_db_path+'GeoIPdb.gz')

        # Set database (GeoLiteCity)
        geoip= pygeoip.GeoIP(geo_db_path + 'GeoLiteCity.dat')

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
        # extract browser type and path
        browser = self.try_running(self.check_browser, "\nInternal error checking browser files path.")
        # extract url
        url = self.try_running(self.getURL, "\nInternal error getting urls from browser's database.")
        # set geoip database
        geo = self.try_running(self.getGEO, "\nInternal error setting geoIP database.")
        # run traceroutes
        traces = self.try_running(self.traces, "\nInternal error tracerouting.")
        # start web mode
        BorderCheckWebserver(self) #child process or another thread

if __name__ == "__main__":
    app = bc()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
