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

import subprocess, socket, threading
from options import BCOptions
from webserver import BorderCheckWebserver
from xml_exporter import xml_reporting
import webbrowser

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
        self.browser_history_path = ""
        self.browser_version = ""
        self.url = ""
        self.old_url = ""
        self.ip = ""
        self.longitude = ""
        self.latitude = ""
        self.hop_host_name = ""
        self.city = ""
        self.country = ""
        self.server_name = "" 
        self.hop_count = 1 # number of hops

        if os.path.exists('data.xml'): # removing xml data to has a new map each time that bc is launched
            os.remove('data.xml')  
        open('data.xml', 'w') # starting a new xml data container in write mode

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
            # paths to the browsing history db's 
            f_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Firefox/Profiles')
            c_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Google/Chrome/Default/History')
            chromium_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Chromium/Default/History')
            s_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Safari/History.plist')
            # path to the browser executables
            f_osx = '/Applications/Firefox.app/Contents/MacOS/firefox' 
            c_osx = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            chromium_osx = '/Applications/Chromium.app/Contents/MacOS/Chromium'
            s_osx = '/Applications/Safari.app/Contents/MacOS/Safari'
            try:
                if os.path.exists(f_his_osx):
                    if len(os.listdir(f_his_osx)) > 2:
                        print 'You have multiple profiles, choosing the last one used'
                        #filtering the directory that was last modified
                        all_subdirs = [os.path.join(f_his_osx,d)for d in os.listdir(f_his_osx)]
                        try:
                            all_subdirs.remove(os.path.join(f_his_osx,'.DS_Store')) #throwing out .DS_store
                        except:
                            pass
                        latest_subdir = max(all_subdirs, key=os.path.getmtime)
                        osx_profile = os.path.join(f_his_osx, latest_subdir)
                        self.browser_history_path = os.path.join(osx_profile, 'places.sqlite')
                    else:
                        for folder in os.listdir(f_his_osx):
                            if folder.endswith('.default'):
                                osx_default = os.path.join(f_his_osx, folder)
                                self.browser_history_path = os.path.join(osx_default, 'places.sqlite')
                                #print "Setting:", self.browser_history_path, "as history file"
                    self.browser = "F"
                    self.browser_path = f_osx
                elif os.path.exists(c_his_osx):
                    self.browser = "C"
                    self.browser_history_path = c_his_osx
                    self.browser_path = c_osx
                elif os.path.exists(chromium_his_osx):
                    self.browser = "CHROMIUM"
                    self.browser_history_path = chromium_his_osx
                    self.browser_path = chromium_osx
                elif os.path.exists(s_his_osx):
                    self.browser = "S"
                    self.browser_history_path = s_his_osx
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
                        self.browser_history_path = os.path.join(lin_default, 'places.sqlite')
                        self.browser = "F"
            elif os.path.exists(c_lin):
                self.browser = "C"
                self.browser_history_path = c_lin
            elif os.path.exists(chromium_lin):
                self.browser = "CHROMIUM"
                self.browser_history_path = chromium_lin

        print "Browser Options:\n" + '='*45 + "\n"
        if sys.platform.startswith('linux'):
            if self.browser == "F":
                print "Currently used: Firefox\n"
            if self.browser == "C":
                print "Currently used: Chrome\n"
            if self.browser == "CHROMIUM":
                print "Currently used: Chromium\n"
        else:
            print "Currently used:", self.browser_path.split('/')[-1], "\n"

        if self.options.debug == True:
            if sys.platform == 'darwin':
                if self.browser == "F" or self.browser == "C" or self.browser == "CHROMIUM":
                    self.browser_version = subprocess.check_output([self.browser_path, '--version']).strip('\n')
            elif sys.platform.startswith('linux') and self.browser == "F":
                self.browser_version = subprocess.check_output(['firefox', '--version']).strip('\n')

            if self.browser == "S":
                print "Can't get Safari version information, you'll have to look it up manually \n"
            else:
                print "Version:", self.browser_version, "\n"
            print "History:", self.browser_history_path, "\n"

        #move the subprocesses to debug mode

    def getURL(self):
        """
        Set urls to visit
        """
        if self.browser == "F": #Firefox history database
            conn = sqlite3.connect(self.browser_history_path)
            c = conn.cursor()
            c.execute('select url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
            url = c.fetchone()

        elif self.browser == "C" or self.browser == "CHROMIUM": #Chrome/Chromium history database
            #Hack that makes a copy of the locked database to access it while Chrome is running.
            #Removes the copied database afterwards
            import filecmp
            a = self.browser_history_path + 'Copy'
            if os.path.exists(a):
                if filecmp.cmp(self.browser_history_path, a) == False:
                    os.system('rm "' + a+'"')
                    os.system('cp "' + self.browser_history_path + '" "' + a + '"')
            else:
                os.system('cp "' + self.browser_history_path + '" "' + a + '"')
    
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

            plist = readPlist(self.browser_history_path)
            url = [plist['WebHistoryDates'][0][''], '']

        else: # Browser not allowed
            print "\nSorry, don't have a compatible browser\n\n"
            exit(2)
        
        self.url = url
        return url[0]

    def traces(self):
        '''
        Use LFT to traceroute objetives and pass data to webserver
        '''
        # Set database (GeoLiteCity)
        self.geoip = pygeoip.GeoIP('GeoLiteCity.dat')
        self.geoasn = pygeoip.GeoIP('GeoIPASNum.dat')
        self.hop_count = 1

        print '='*45 + "\n", "Current target:\n" + '='*45 + "\n"
        print "URL:", self.url[0], "\n"

        url = urlparse(self.getURL()).netloc #changed this for prototyping
        url = url.replace('www.','') #--> doing a tracert to example.com and www.example.com yields different results.
        url_ip = socket.gethostbyname(url)
        self.ip = url_ip
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
                    a = subprocess.Popen(['lft', '-S', '-n', '-e', url_ip], stdout=subprocess.PIPE)
                # using tcp
                except:     
                    try:    
                        print "Method: tcp\n"
                        a = subprocess.Popen(['lft', '-S', '-n', '-e', url_ip], stdout=subprocess.PIPE)
                    except: 
                        print "Error: network is not responding correctly. Aborting...\n"
                        sys.exit(2)
            #Make a tracelog file.
            if self.options.debug == True:
                logfile = open('tracelogfile', 'a')
                thingstolog = ['='*45 + "\n", "Browser: ", self.browser_path.split('/')[-1], "\n", "Version: ", self.browser_version, "\n", "Path to browser: ", self.browser_path, "\n", "History db: ", self.browser_history_path, "\n","URL: ", self.url[0], "\n", "Host: ",url, "\n", "Host ip: ", url_ip, "\n", '='*45, "\n"]
                for item in thingstolog:
                    logfile.write(item)
            print '='*45 + "\n" + "Packages Route:\n" + '='*45
            for line in a.stdout:
                self.hop_count = self.hop_count + 1

                if self.options.debug == True:
                    logfile.write(line)
                parts = line.split()
                for ip in parts:
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
                        record = self.geoip.record_by_addr(ip)
                        try:
                            asn = self.geoasn.org_by_addr(ip)
                        except:
                            asn = 'nothing'
                        #print record
                        try:
                            self.hop_host_name = socket.gethostbyaddr(ip)[0]
                        except:
                            self.hop_host_name = 'No hostname'
                        try:
                            longitude = str(record['longitude'])
                            self.longitude = longitude
                            latitude = str(record['latitude'])
                            self.latitude = latitude
                        except:
                            self.longitude = '-'
                            self.latitude = '-'
                        try:
                            if record.has_key('country_name') and record['city'] is not '':
                                country = record['country_name']
                                city = record['city']
                                print "Trace:", count, "->", ip, "->", longitude + ":" + latitude, "->", city, "->", country, "->", self.hop_host_name, asn
                                count+=1
                                self.city = city
                                self.country = country
                                self.server_name = self.hop_host_name
                            elif record.has_key('country_name'):
                                country = record['country_name']
                                print "Trace:", count, "->", ip, "->", longitude + ":" + latitude, "->", country, "->", self.hop_host_name, asn
                                self.country = country
                                self.server_name = self.hop_host_name
                                count+=1
                        except:
                            print "Trace:", count, "->", "Not allowed"
                            count+=1
                        # write xml data to file
                        xml_results = xml_reporting(self)
                        xml_results.print_xml_results('data.xml')

            if self.options.debug == True:
                logfile.close()
            self.old_url = url
            self.hop_count = 0 # to start a new map
            print "\n"

    def getGEO(self):
        """
        Get Geolocation database (http://dev.maxmind.com/geoip/legacy/geolite/)
        """
        maxmind = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
        geo_db_mirror1 = 'http://xsser.sf.net/map/GeoLiteCity.dat.gz'
        print "="*45 + "\n", "GeoIP Options:\n" + '='*45 + "\n"
        # Download, extract and set geoipdatabase
        if not os.path.exists('GeoLiteCity.dat'):
            import urllib, gzip
            geo_db_path = '/'
            try:
                print "Downloading GeoIP database...\n"
                if self.options.debug == True:
                    print "Fetching from:", maxmind
                urllib.urlretrieve(maxmind,
                                   'GeoLiteCity.gz')
            except:
                try:
                    if self.options.debug == True:
                        print "Fetching from:", geo_db_mirror1 
                    urllib.urlretrieve(geo_db_mirror1,
                                        'GeoLiteCity.gz')
                except:
                    print("[Error] - Something wrong fetching GeoIP maps from the Internet. Aborting..."), "\n"
                    sys.exit(2)
            f_in = gzip.open('GeoLiteCity.gz', 'rb')
            f_out = open('GeoLiteCity.dat', 'wb')
            f_out.write(f_in.read())
            f_in.close()

            os.remove('GeoLiteCity.gz')

        maxmind_asn = 'http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum.dat.gz'
        # Download, extract and set geoipdatabase
        if not os.path.exists('GeoIPASNum.dat'):
            import urllib, gzip
            geo_db_path = '/'
            try:
                print "Downloading GeoIP ASN database...\n"
                if self.options.debug == True:
                    print "Fetching from:", maxmind_asn
                urllib.urlretrieve(maxmind,
                                   'GeoIPASNum.gz')
            except:
                print("[Error] - Something wrong fetching GeoIP maps from the Internet. Aborting..."), "\n"
                sys.exit(2)
            f_in = gzip.open('GeoIPASNum.gz', 'rb')
            f_out = open('GeoIPASNum.dat', 'wb')
            f_out.write(f_in.read())
            f_in.close()

            os.remove('GeoIPASNum.gz')
        print "Database: GeoIPASNum \n"

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
        # run traceroutes
        match_ip = self.url[0].strip('http://').strip(':8080')
        if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip):
            pass
        else:
            traces = self.try_running(self.traces, "\nInternal error tracerouting.")
        # start web mode (on a different thread)
        try:
            t = threading.Thread(target=BorderCheckWebserver, args=(self, ))
            t.start()
            time.sleep(2)
        except:
            print "Error: unable to start thread"
            pass
        # open same browser of history access on a new tab
        try:
            webbrowser.open('http://127.0.0.1:8080', new=1)
        except:
            print "Error: Browser is not responding correctly.\n"

        print '='*45 + "\n"
        print "Status: Waiting for new urls ...\n"
        # stay latent waiting for new urls
        while True:
            url = urlparse(self.getURL()).netloc
            url = url.replace('www.','')
            match_ip = url.strip('http://').strip(':8080')
            if url != self.old_url:
                if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip):
                    pass
                else:
                    traces = self.try_running(self.traces, "\nInternal error tracerouting.")

if __name__ == "__main__":
    app = bc()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
