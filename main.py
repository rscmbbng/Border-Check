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
            if options.url:
                print("[Error] - Something wrong fetching urls. Aborting..."), "\n"
                sys.exit(2)
            else:
                print(error, "error")
                if DEBUG:
                    traceback.print_exc()

    def check_browser(self):
        """
Check for browser used by system
"""
        if sys.platform == 'darwin':
            f_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Firefox/Profiles')
            c_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Google/Chrome/Default/History')
            chromium_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Chromium/Default/History')
            try:
                if os.path.exists(f_osx):
                    if len(os.listdir(f_osx)) > 2:
                        print 'you have multiple profiles, choosing the last one used'
                        #filtering the directory that was last modified
                        all_subdirs = [os.path.join(f_osx,d)for d in os.listdir(f_osx)]
                        try:
                            all_subdirs.remove(os.path.join(f_osx,'.DS_Store')) #throwing out .DS_store
                        except:
                            pass
                        latest_subdir = max(all_subdirs, key=os.path.getmtime)

                        osx_profile = os.path.join(f_osx, latest_subdir)
                        osx_history_path = os.path.join(osx_profile, 'places.sqlite')
                        self.browser_path = osx_history_path

                    else:
                        for folder in os.listdir(f_osx):
                            if folder.endswith('.default'):
                                osx_default = os.path.join(f_osx, folder)
                                osx_history_path = os.path.join(osx_default, 'places.sqlite')
                                print "setting:", osx_history_path, "as history file"
                                self.browser_path = osx_history_path

                    self.browser = "F"

                elif os.path.exists(c_osx):
                    self.browser = "C"
                    self.browser_path = c_osx

                elif os.path.exists(chromium_osx):
                    self.browser = "CHROMIUM"
                    self.browser_path = chromium_osx

            except:
                print "no firefox or chrome installed"

        elif sys.platform.startswith('linux'):
            f_lin = os.path.join(os.path.expanduser('~'), '.mozilla/firefox/') #add the next folder
            c_lin = os.path.join(os.path.expanduser('~'), '.config/google-chrome/History')
            chromium_lin = os.path.join(os.path.expanduser('~'), '.config/chromium/Default/History')

            if os.path.exists(f_lin):
                #missing multiple profile support
                for folder in os.listdir(f_lin):
                    if folder.endswith('.default'):
                        lin_default = os.path.join(f_lin, folder)
                        lin_history_path = os.path.join(lin_default, 'places.sqlite')
                        self.browser = "F"
                        self.browser_path = lin_history_path

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
        conn = sqlite3.connect(self.browser_path)
        c = conn.cursor()

        if self.browser == "F": #Firefox history database
            c.execute('select url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
        elif self.browser == "C": #Chrome history database
            # Linux: /home/$USER/.config/google-chrome/
            # Linux: /home/$USER/.config/chromium/
            # Windows Vista (and Win 7): C:\Users\[USERNAME]\AppData\Local\Google\Chrome\
            # Windows XP: C:\Documents and Settings\[USERNAME]\Local Settings\Application Data\Google\Chrome\
            c.execute('select urls.url, urls.title, urls.visit_count, urls.typed_count, urls.last_visit_time, urls.hidden, visits.visit_time, visits.from_visit, visits.transition from urls, visits where urls.id = visits.url')
        else: # Browser not allowed
            print "\nSorry, you haven't a compatible browser\n\n"
            exit(2)
        url = c.fetchone()
        self.url = url
        print "Fetching URL:", self.url[0], "\n"
        return url[0]

    def getGEO(self):
        """
Get Geolocation database (http://dev.maxmind.com/geoip/legacy/geolite/)
"""
        # Download and extract database
        try:
            urllib.urlretrieve('http://xsser.sf.net/map/GeoLiteCity.dat.gz',
                                      geo_db_path+'.gz', reportfunc)
        except:
            try:
                urllib.urlretrieve('http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
                                      geo_db_path+'.gz', reportfunc)
            except:
                print("[Error] - Something wrong fetching GeoIP maps from the Internet. Aborting..."), "\n"
                sys.exit(2)

        # Set database
        geoip= pygeoip.GeoIP('GeoLiteCity.dat')

    def run(self, opts=None):
        """
Run BorderCheck
"""
        #eprint = sys.stderr.write
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
        print "url:", self.url
        # start web mode
        print("Running webserver\n")
        BorderCheckWebserver(self)

        while True:
            url = urlparse(self.url[0]).netloc
            url = url.replace('www.','') #--> doing a tracert to for example.com and www.example.com yields different results most of the times.
            url_ip = socket.gethostbyname(url)
            print url_ip
            if url != self.old_url:
                count = 0
                print url

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
            print"old url =", self.old_url
            logfile.close()
            time.sleep(5)

if __name__ == "__main__":
    app = bc()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()