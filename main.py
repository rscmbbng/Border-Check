#!/usr/bin/env python 
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
    print "\nError importing: pygeoip lib. \n\n On Debian based systems:\n\n $ apt-get install python-pip and $ pip install pygeoip \n"
    sys.exit(2)
try:
    import sqlite3
except: #this should be a standard package of python 2.5+
    print "\nError importing: sqlite3 lib. \n\nOn Debian based systems, please try like root:\n\n $ apt-get install sqlite3\n"
    sys.exit(2)

import subprocess, socket, threading
from options import BCOptions
from webserver import BorderCheckWebserver
from xml_exporter import xml_reporting
import webbrowser

class bc(object):
    """
    BC main Class
    """
    def __init__(self):
        """
        Init defaults
        """
        # Global variables organised by the function in which they first occur.

        # check_browser():
        self.operating_system = '' #The operating system being used. Either darwin/linux
        self.browser = "" # "F" Firefox / "C" Chrome / "S" Safari / "CHROMIUM" Chromium
        self.browser_path = "" #the path to the browser application
        self.browser_history_path = "" # the path to the browser history file
        self.browser_version = "" # the version of the browser

        # lft():
        self.content = '' # the un-parsed results of a traceroute
        self.attempts = 0 # the number of attempts at a traceroute
        self.method = '-e' # the tracing method, -e to use TCP packets, -u for UDP packets

        # traces():
        self.url = "" # the last visited url from the history file, type is tuple
        self.old_url = "" # the before last url from the history file
        self.destination_ip = "" #the ip adress of self.url
        self.hop_ip = "" #the ip of the servers/router on a hop
        self.timestamp = "1" #the time it took to go to a hop in miliseconds.

        # these variables are all the result of Maxmind DB lookups
        self.longitude = "" # the lat/long that corresponds the an ip as per Maxmind DB
        self.latitude = "" # idem
        self.asn = '' #ASN number of a server
        self.hop_host_name = "" #hostname of server/router on a hop
        self.city = "" #
        self.country = "" #
        self.server_name = "" # same as self.hop_host_name. perhaps good to clean this.
        self.hop_count = 1 # number of the current hop in a trace
        self.result_list = []  #list to collect all the variables of a trace
        self.vardict ={} #dict to store all the variables of a hop
        
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
            if not options.debug:
                print("[Error] - Something went wrong! Try to run again with the '--debug' argument for more info via the a traceback output."), "\n"
            else:
                print("[Error] - Something went wrong! Have a look the traceback. If you don't understand what happened, copy it and get in touch with one of the project contributors via https://github.com/rscmbbng/Border-Check."), "\n"
            if options.debug == 1:
                traceback.print_exc()
                print "" # \n after traceback ouput
            sys.exit(2)

    def check_root(self):
        """     
        Check root permissions
        """
        if not os.geteuid()==0:
            sys.exit("Warning: Only root can launch traceroutes. (Try: 'sudo ./bc')\n")

    def check_browser(self):
        """
        Check browsers used by system
        """
        print "Browser Options:\n" + '='*45 + "\n"
        # make browser set manually by user
        if self.options.browser:
            if self.options.browser == "F" or self.options.browser == "f": # Firefox
                if sys.platform == 'darwin': # on darwin
                    self.operating_system = 'darwin'
                    f_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Firefox/Profiles')
                    f_osx = '/Applications/Firefox.app/Contents/MacOS/firefox' 
                    try:
                        if os.path.exists(f_his_osx):
                            if len(os.listdir(f_his_osx)) > 2:
                                print 'You have multiple profiles, choosing the last one used'
                                # filter to use the directory that was last modified.
                                all_subdirs = [os.path.join(f_his_osx,d)for d in os.listdir(f_his_osx)]
                                try:
                                    all_subdirs.remove(os.path.join(f_his_osx,'.DS_Store')) # throwing out .DS_store
                                except:
                                    pass
                                latest_subdir = max(all_subdirs, key=os.path.getmtime)
                                osx_profile = os.path.join(f_his_osx, latest_subdir)
                                if self.options.browser_history: # if exists, extract user browser's history path
                                    self.browser_history_path = self.options.browser_history
                                else:
                                    self.browser_history_path = os.path.join(osx_profile, 'places.sqlite')
                            else:
                                for folder in os.listdir(f_his_osx):
                                    if folder.endswith('.default'):
                                        osx_default = os.path.join(f_his_osx, folder)
                                        if self.options.browser_history: # if exists, extract user browser's history path
                                            self.browser_history_path = self.options.browser_history
                                        else:
                                            self.browser_history_path = os.path.join(osx_default, 'places.sqlite')
                            self.browser = "F"
                            self.browser_path = f_osx
                    except:
                        print "Warning: Firefox hasn't been detected on your Darwin system.\n"
                        sys.exit(2)
                elif sys.platform.startswith('linux'): # on unix
                    self.operating_system = 'linux'
                    f_lin = os.path.join(os.path.expanduser('~'), '.mozilla/firefox/') #add the next folder
                    if os.path.exists(f_lin):
                        #missing multiple profile support
                        for folder in os.listdir(f_lin):
                            if folder.endswith('.default'):
                                lin_default = os.path.join(f_lin, folder)
                                if self.options.browser_history: # if exists, extract user browser's history path
                                    self.browser_history_path = self.options.browser_history
                                else:
                                    self.browser_history_path = os.path.join(lin_default, 'places.sqlite')
                                self.browser = "F"
                    else:
                        print "Warning: Firefox hasn't been detected on your Unix system.\n"
                        sys.exit(2)
                else:
                    print "Warning: Only GNU/Linux or Darwin operating systems supported.\n"
                    sys.exit(2)
            elif self.options.browser == "C" or self.options.browser == "c": # Chrome
                if sys.platform == 'darwin': # on darwin
                    self.operating_system = 'darwin'
                    c_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Google/Chrome/Default/History')
                    c_osx = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
                    try:
                        if os.path.exists(c_his_osx):
                            self.browser = "C"
                            if self.options.browser_history: # if exists, extract user browser's history path
                                self.browser_history_path = self.options.browser_history
                            else:
                                self.browser_history_path = c_his_osx
                            self.browser_path = c_osx
                    except:
                        print "Warning: Chrome hasn't been detected on your Darwin system.\n"
                        sys.exit(2)
                elif sys.platform.startswith('linux'): # on unix
                    self.operating_system = 'linux'
                    c_lin = os.path.join(os.path.expanduser('~'), '.config/google-chrome/History')
                    if os.path.exists(c_lin):
                        self.browser = "C"
                        if self.options.browser_history: # if exists, extract user browser's history path
                            self.browser_history_path = self.options.browser_history
                        else:
                            self.browser_history_path = c_lin
                    else:
                        print "Warning: Chrome hasn't been detected on your Unix system.\n"
                        sys.exit(2)
                else:
                    print "Warning: Only GNU/Linux or Darwin operating systems supported.\n"
                    sys.exit(2)
            elif self.options.browser == "Ch" or self.options.browser == "CH" or self.options.browser == "ch": # Chromium
                if sys.platform == 'darwin': # on darwin
                    self.operating_system = 'darwin'
                    chromium_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Application Support/Chromium/Default/History')
                    chromium_osx = '/Applications/Chromium.app/Contents/MacOS/Chromium'
                    try:
                        if os.path.exists(chromium_his_osx):
                            self.browser = "CHROMIUM"
                            if self.options.browser_history: # if exists, extract user browser's history path
                                self.browser_history_path = self.options.browser_history
                            else:
                                self.browser_history_path = chromium_his_osx
                            self.browser_path = chromium_osx
                    except:
                        print "Warning: Chromium hasn't been detected on your Darwin system.\n"
                        sys.exit(2)
                elif sys.platform.startswith('linux'): # on unix
                    self.operating_system = 'linux'
                    chromium_lin = os.path.join(os.path.expanduser('~'), '.config/chromium/Default/History')
                    if os.path.exists(chromium_lin):
                        self.browser = "CHROMIUM"
                        if self.options.browser_history: # if exists, extract user browser's history path
                            self.browser_history_path = self.options.browser_history
                        else:
                            self.browser_history_path = chromium_lin
                    else:
                        print "Warning: Chromium hasn't been detected on your Unix system.\n"
                        sys.exit(2)
                else:
                    print "Warning: Only GNU/Linux or Darwin operating systems supported.\n"
                    sys.exit(2)
            elif self.options.browser == "S" or self.options.browser == "s": # Safari
                if sys.platform == 'darwin': # on darwin
                    self.operating_system = 'darwin'
                    s_his_osx = os.path.join(os.path.expanduser('~'), 'Library/Safari/History.plist')
                    s_osx = '/Applications/Safari.app/Contents/MacOS/Safari'
                    try:
                        if os.path.exists(s_his_osx):
                            self.browser = "S"
                            if self.options.browser_history: # if exists, extract user browser's history path
                                self.browser_history_path = self.options.browser_history
                            else:
                                self.browser_history_path = s_his_osx
                            self.browser_path = s_osx
                    except:
                        print "Warning: Safari hasn't been detected on your Darwin system.\n"
                        sys.exit(2)
                elif sys.platform.startswith('linux'): # on unix
                    self.operating_system = 'linux # check needed'
                    safari_lin = os.path.join(os.path.expanduser('~'), 'Library/Safari/History.plist') # check needed
                    if os.path.exists(safari_lin):
                        self.browser = "S"
                        if self.options.browser_history: # if exists, extract user browser's history path
                            self.browser_history_path = self.options.browser_history
                        else:
                            self.browser_history_path = safari_lin
                    else:
                        print "Warning: Safari hasn't been detected on your Unix system.\n"
                        sys.exit(2)
                else:
                    print "Warning: Only GNU/Linux or Darwin operating systems supported.\n"
                    sys.exit(2)
            else: # browser not supported error
                print "You must enter a correct input to set your browser manually: F = Firefox / C = Chrome / S = Safari / Ch = Chromium\n"
                sys.exit(2)
        # make browser set, automatically
        else:
            if sys.platform == 'darwin':
                self.operating_system = 'darwin'
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
                            # filter to use the directory that was last modified.
                            all_subdirs = [os.path.join(f_his_osx,d)for d in os.listdir(f_his_osx)]
                            try:
                                all_subdirs.remove(os.path.join(f_his_osx,'.DS_Store')) # throwing out .DS_store
                            except:
                                pass
                            latest_subdir = max(all_subdirs, key=os.path.getmtime)
                            osx_profile = os.path.join(f_his_osx, latest_subdir)
                            if self.options.browser_history: # if exists, extract user browser's history path
                                self.browser_history_path = self.options.browser_history
                            else:
                                self.browser_history_path = os.path.join(osx_profile, 'places.sqlite')
                        else:
                            for folder in os.listdir(f_his_osx):
                                if folder.endswith('.default'):
                                    osx_default = os.path.join(f_his_osx, folder)
                                    if self.options.browser_history: # if exists, extract user browser's history path
                                        self.browser_history_path = self.options.browser_history
                                    else:
                                        self.browser_history_path = os.path.join(osx_default, 'places.sqlite')
                        self.browser = "F"
                        self.browser_path = f_osx
                    elif os.path.exists(c_his_osx):
                        self.browser = "C"
                        if self.options.browser_history: # if exists, extract user browser's history path
                            self.browser_history_path = self.options.browser_history
                        else:
                            self.browser_history_path = c_his_osx
                        self.browser_path = c_osx
                    elif os.path.exists(chromium_his_osx):
                        self.browser = "CHROMIUM"
                        if self.options.browser_history: # if exists, extract user browser's history path
                            self.browser_history_path = self.options.browser_history
                        else:
                            self.browser_history_path = chromium_his_osx
                        self.browser_path = chromium_osx
                    elif os.path.exists(s_his_osx):
                        self.browser = "S"
                        if self.options.browser_history: # if exists, extract user browser's history path
                            self.browser_history_path = self.options.browser_history
                        else:
                            self.browser_history_path = s_his_osx
                        self.browser_path = s_osx
                except:
                    print "Warning: None of the currently supported browsers (Firefox, Chrome, Chromium, Safari) are installed."

            elif sys.platform.startswith('linux'):
                self.operating_system = 'linux'
                f_lin = os.path.join(os.path.expanduser('~'), '.mozilla/firefox/') #add the next folder
                c_lin = os.path.join(os.path.expanduser('~'), '.config/google-chrome/History')
                chromium_lin = os.path.join(os.path.expanduser('~'), '.config/chromium/Default/History')
                if os.path.exists(f_lin):
                    #missing multiple profile support
                    for folder in os.listdir(f_lin):
                        if folder.endswith('.default'):
                            lin_default = os.path.join(f_lin, folder)
                            if self.options.browser_history: # if exists, extract user browser's history path
                                self.browser_history_path = self.options.browser_history
                            else:
                                self.browser_history_path = os.path.join(lin_default, 'places.sqlite')
                            self.browser = "F"
                elif os.path.exists(c_lin):
                    self.browser = "C"
                    if self.options.browser_history: # if exists, extract user browser's history path
                        self.browser_history_path = self.options.browser_history
                    else:
                        self.browser_history_path = c_lin
                elif os.path.exists(chromium_lin):
                    self.browser = "CHROMIUM"
                    if self.options.browser_history: # if exists, extract user browser's history path
                        self.browser_history_path = self.options.browser_history
                    else:
                        self.browser_history_path = chromium_lin

        # ouput browser used on different platforms
        if sys.platform.startswith('linux'):
            if self.browser == "F":
                print "Using: Firefox\n"
            if self.browser == "C":
                print "Using: Chrome\n"
            if self.browser == "CHROMIUM":
                print "Using: Chromium\n"
        else:
            print "Using:", self.browser_path.split('/')[-1], "\n"
        if self.options.debug == True:
            if sys.platform == 'darwin':
                if self.browser == "F" or self.browser == "C" or self.browser == "CHROMIUM":
                    try:
                        self.browser_version = subprocess.check_output([self.browser_path, '--version']).strip('\n')
                    except:
                        a = subprocess.Popen(['firefox', '--version'], stdout=subprocess.PIPE)
                        self.browser_version = a.stdout.read()
            elif sys.platform.startswith('linux') and self.browser == "F":
                try:
                    self.browser_version = subprocess.check_output(['firefox', '--version']).strip('\n')
                except:
                    a = subprocess.Popen(['firefox', '--version'], stdout=subprocess.PIPE)
                    self.browser_version = a.stdout.read()
            if self.browser == "S":
                print "Can't get Safari version information, you'll have to look it up manually \n"
            else:
                print "Version:", self.browser_version
            if self.options.import_xml: # history not needed on xml importing
                pass
            else:
                print "History:", self.browser_history_path, "\n"

    def getURL(self):
        """
        Set urls to visit
        """
        if self.browser == "F": 
            # Sqlite operation to get the last visited url from history db.
            conn = sqlite3.connect(self.browser_history_path)
            c = conn.cursor()
            c.execute('select url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
            url = c.fetchone()
        elif self.browser == "C" or self.browser == "CHROMIUM": # Chrome/Chromium history database
            # Hack that makes a copy of the locked database to access it while Chrome is running.
            # Removes the copied database afterwards
            import filecmp # is this a standard module?
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
                print "\nError importing: biplist lib. \n\nTo run BC with Safari you need the biplist Python library:\n\n $ pip install biplist\n"
            plist = readPlist(self.browser_history_path)
            url = [plist['WebHistoryDates'][0][''], '']
        else: # Browser not allowed
            print "Sorry, you don't have a compatible browser\n\n"
            exit(2)
        self.url = url
        return url[0]

    def lft(self):
        """
        Run an LFT
        """
        # LFT needs root
        root = self.try_running(self.check_root, "\nInternal error checking root permissions.")

        #try:
        if self.operating_system == 'darwin':
            try:
                self.content = subprocess.check_output(['lft', self.method, '-n', '-S', self.destination_ip])
            except:
                a = subprocess.Popen(['lft', self.method, '-S', '-n', self.destination_ip], stdout=subprocess.PIPE)
                self.content = a.stdout.read()

        if self.operating_system == 'linux':
            if self.method == '-e': # tcp probes
                self.method = '-E'
            try:
                self.content = subprocess.check_output(['lft', '-S', '-n', self.method, self.destination_ip])
                # support for older python versions (<2.75) that don't support subprocess.check_output
            except:
                a = subprocess.Popen(['lft', '-S', '-n', self.method, self.destination_ip], stdout=subprocess.PIPE)
                self.content = a.stdout.read()
        self.attempts += 1
        if self.options.debug == True:
            print "Tracing:", self.destination_ip, "with method:", self.method, 'attempt:', self.attempts, '\n'
        self.lft_parse()

    def lft_parse(self):
        """
        Parse the lft to see if it produced any results, if not, run another LFT using a different method
        """     
        output = self.content.splitlines()
        if output[-1] == "**  [80/tcp no reply from target]  Try advanced options (use -VV to see packets).":
            if self.options.debug == True:
                print 'TCP method doesn''t work, switching to UDP \n'
            self.method = '-u'
            time.sleep(2)
            self.lft()
        if '[target closed]' in output[-1] and self.method == '-e' or self.method == '-E':
            if self.options.debug == True:
                print 'Target closed, retrying with UDP \n'
            self.method = '-u'
            time.sleep(2)
            self.lft()
        if '[target open]' in output[-1] and len(output) < 5:
            if self.options.debug == True:
                print 'Target open, but filtered. Retrying with UDP \n'
            self.method = '-u'
            time.sleep(2)
            self.lft()
        if 'udp no reply from target]  Use -VV to see packets.' in output[-1] and len(output) > 5:
            if self.options.debug == True:
                print 'Trace ended with results \n'
            return
        if '[port unreachable]' in output[-1]:
            if self.options.debug == True:
                print 'Port unreachable \n'
            return
        if '[target open]' in output[-1] and len(output) > 5:
            if self.options.debug == True:
                print 'Target open, with results \n'
            return
        if '[prohibited]' in output[-1]:
            if self.options.debug == True:
                print 'prohibited'

    def traces(self):
        '''
        call LFT to traceroute target and pass data to webserver
        '''
        # Set the maxmind geo databases 
        self.geoip = pygeoip.GeoIP('GeoLiteCity.dat')
        self.geoasn = pygeoip.GeoIP('GeoIPASNum.dat')
        print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
        print "URL:", self.url[0], "\n"
        url = urlparse(self.getURL()).netloc #changed this for prototyping
        #url = url.replace('www.','') #--> doing a tracert to example.com and www.example.com yields different results.
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,4}$",url):
            url_ip = socket.gethostbyname(url.split(':')[0])
        else:
            url_ip = url.split(':')[0]
            pass
        self.url = url
        self.destination_ip = url_ip
        print "Host:", url, "\n"
        if url != self.old_url:
            self.hop_count = 0
            self.attempts = 0
            self.result_list = []
            self.lft()
            if self.options.debug == True:
                logfile = open('tracelogfile', 'a')
                thingstolog = ['='*45 + "\n", "Browser: ", self.browser_path.split('/')[-1], "\n", "Version: ", self.browser_version, "\n", "Path to browser: ", self.browser_path, "\n", "History db: ", self.browser_history_path, "\n","URL: ", self.url, "\n", "Host: ",url, "\n", "Host ip: ", url_ip, "\n", '='*45, "\n"]
                for item in thingstolog:
                    logfile.write(item)
            print '='*45 + "\n" + "Packages Route:\n" + '='*45
            output = self.content.splitlines()
            for line in output:
                if self.options.debug == True:
                    logfile.write(line+'\n')
                line = line.split()
                for ip in line:
                    if re.match(r'\d{1,4}\.\dms$', ip):
                        self.timestamp = ip.replace('ms', '')
                    if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', ip) or re.match('localhost', ip):
                        pass
                    else:    
                        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
                            self.hop_ip = ip
                            record = self.geoip.record_by_addr(ip)
                            try:
                                self.asn = self.geoasn.org_by_addr(ip)
                            except:
                                self.asn = 'No ASN provided'
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
                                    print "Trace:", self.hop_count, "->", ip, "->", longitude + ":" + latitude, "->", city, "->", country, "->", self.hop_host_name, "->", self.asn, '->', self.timestamp+'ms'
                                    #self.hop_count +=1
                                    self.city = city
                                    self.country = country
                                    self.server_name = self.hop_host_name
                                    cc = record['country_code'].lower()
                                elif record.has_key('country_name'):
                                    country = record['country_name']
                                    print "Trace:", self.hop_count, "->", ip, "->", longitude + ":" + latitude, "->", country, "->", self.hop_host_name, "->", self.asn, '->', self.timestamp+'ms'
                                    self.country = country
                                    self.city = '-'
                                    self.server_name = self.hop_host_name
                                    cc = record['country_code'].lower()
                                    #self.hop_count+=1
                                self.vardict = {'url': self.url, 'destination_ip': self.destination_ip, 'hop_count': self.hop_count,'hop_ip': self.hop_ip, 'server_name': self.server_name, 'country': self.country, 'city': self.city, 'longitude': self.longitude, 'latitude': self.latitude, 'asn' : self.asn, 'timestamp' : self.timestamp, 'country_code': cc  }
                            except:
                                #pass
                                print "Trace:", self.hop_count, "->", "Not allowed", ip
                                self.vardict = {'url': self.url, 'destination_ip': self.destination_ip, 'hop_count': self.hop_count,'hop_ip': self.hop_ip, 'server_name': self.server_name, 'country': '-', 'city': '-', 'longitude': '-', 'latitude': '-', 'asn' : self.asn, 'timestamp' : self.timestamp, 'country_code': '-' }

                            self.hop_count+=1
                            # write xml data to file
                            self.result_list.append(self.vardict)
                            xml_results = xml_reporting(self)
                            xml_results.print_xml_results('data.xml')
                            if self.options.export_xml:
                                open(self.options.export_xml, 'w') # starting a new xml data container in write mode
                                xml_results.print_xml_results(self.options.export_xml)

            if self.options.debug == True:
                logfile.close()
            self.old_url = url
            print "\n"
            self.hop_count = 0 # to start a new map
            return

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
                    print "Fetching from:", maxmind, '\n'
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
                    print "Fetching from:", maxmind_asn,'\n'
                urllib.urlretrieve(maxmind_asn,
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

    def importXML(self):
        """
        Import travels data directly from XML file (no root needed) and launch a web browser on a thread with a map showing them.
        """
        try:
            xml_results = xml_reporting(self)
            xml_imported = xml_results.read_xml_results() # read xml directly from file
        except:
            print("[Error] - Something wrong importing data from XML file. Aborting..."), "\n"
            sys.exit(2)

        # Set the maxmind geo databases 
        self.geoip = pygeoip.GeoIP('GeoLiteCity.dat')
        self.geoasn = pygeoip.GeoIP('GeoIPASNum.dat')
        match_ip = xml_imported[0].strip('http://').strip(':8080')
        #regex for filtering local network IPs
        if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip) or match_ip.startswith('file://') or match_ip.startswith('localhost'):
            print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
            print "URL:", self.options.import_xml, "\n"
            print "Warning: This target is not valid!.\n"
            sys.exit(2)
        else:
            if xml_imported[0].startswith('file://'):
                print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                print "URL:", self.options.import_xml, "\n"
                print "Warning: This target is not valid!.\n"
                sys.exit(2)
            else:
                print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                print "URL:", self.options.import_xml, "\n"
                print "Host:", xml_imported[0], "\n"
                os.system('cp -r ' + self.options.import_xml + ' data.xml') # copy XML data provided by user to data.xml template
                # start web mode (on a different thread)
                try:
                    webbrowser.open('http://127.0.0.1:8080', new=1)
                    BorderCheckWebserver(self)
                except (KeyboardInterrupt, SystemExit):
                    sys.exit()

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
        # read from XML or run traceroutes + stay latent mode
        if options.import_xml:
            import_xml = self.try_running(self.importXML, "\nInternal error importing XML data from file.")
        else:
            match_ip = self.url[0].strip('http://').strip(':8080')
            #regex for filtering local network IPs
            if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip) or match_ip.startswith('file://') or match_ip.startswith('localhost'):
                print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                print "URL:", self.url[0], "\n"
                print "Warning: This target is not valid!.\n"
                pass
            else:
                if self.url[0].startswith('file://'):
                    print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                    print "URL:", self.url[0], "\n"
                    print "Warning: This target is not valid!.\n"
                    pass
                else:
                    traces = self.try_running(self.traces, "\nInternal error tracerouting.")
            # start web mode (on a different thread)
            try:
                t = threading.Thread(target=BorderCheckWebserver, args=(self, ))
                t.daemon = True
                t.start()
                time.sleep(2)
            except (KeyboardInterrupt, SystemExit):
                t.join()
                sys.exit()
                # open same browser of history access on a new tab
                try:
                    webbrowser.open('http://127.0.0.1:8080', new=1)
                except:
                    print "Error: Browser is not responding correctly.\n"

            print('='*75)
            print(str(p.version))
            print('='*75 + "\n")
            print "Status: Waiting for new urls ...\n"
            print "Type 'Control+C' to exit.\n"
            # stay latent waiting for new urls
            while True:
                url = urlparse(self.getURL()).netloc
                #url = url.replace('www.','')
                try:
                    match_ip = url.strip('http://').strip(':8080')
                except:
                    print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                    print "URL:", self.url[0], "\n"
                    pass
                if url != self.old_url:
                    if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip) or match_ip.startswith('localhost'):
                        pass
                    else:
                        if self.url[0].startswith('file://'):
                            pass
                        else:
                            if os.path.exists('data.xml'): # removing xml data to has a new map each time that bc is launched
                                os.remove('data.xml')  
                            open('data.xml', 'w') # starting a new xml data container in write mode
                            traces = self.try_running(self.traces, "\nInternal error tracerouting.")
                            # open same browser of history access on a new tab
                            # try:
                            #     webbrowser.open('http://127.0.0.1:8080', new=2) # open on same tab?
                            # except:
                            #     print "Error: Browser is not responding correctly.\n"
                time.sleep(5) # To free up process time or goodbye :-)       

if __name__ == "__main__":
    app = bc()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
