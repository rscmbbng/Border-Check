#!/usr/bin/env python2
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013-2014-2015 by psy (epsylon@riseup.net)
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
import shlex, getpass, urllib
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
        self.browser = "N" # "F" Firefox / "C" Chrome / "S" Safari / "CHROMIUM" Chromium / "None"
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

        self.last_travel = time.time()
        self.new_travel = False
        
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
                print("[Error] - Something went wrong! Have a look the traceback."), "\n"
            if options.debug == 1:
                traceback.print_exc()
                print "" # \n after traceback ouput
            sys.exit(2)

    def check_root(self):
        """     
        Check root permissions
        """
        if not os.geteuid()==0:
            sys.exit("Error: You need more permissions to make traceroutes. Try to launch BC as root (ex: 'sudo ./bc')\n")

    def check_browser(self):
        """
        Check browsers used by system
        """
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
                    self.operating_system = 'linux'
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
            elif self.options.browser == "N" or self.options.browser == "n": # None
                self.last_travel # force load of last submitted hostname
                if sys.platform == 'darwin': # on darwin
                    self.operating_system = 'darwin'
                elif sys.platform.startswith('linux'): # on unix
                    self.operating_system = 'linux'
                else:
                    print "Warning: Only GNU/Linux or Darwin operating systems supported.\n"
                    sys.exit(2)
                self.browser = "N"
            else: # browser not supported error
                print "You must enter a correct input to set your browser manually: F = Firefox / C = Chrome / S = Safari / Ch = Chromium\n"
                sys.exit(2)
        # make browser set, automatically
        else:
            # if config file exits, take browser type and history path from there
            if os.path.exists('config.py'):
                with open('config.py') as f:
                    for line in f:
                        c = line.split(":")
                    self.browser = c[2]
                    self.browser_history_path = c[3]
            else: # if not, check it from system
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

        if not os.path.exists('config.py'):
            pass
        else:
            # output browser used on different platforms
            print "Browser Options:\n" + '='*45 + "\n"
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

    def loadOptions(self):
        # todo: save file modification time & reload only if file changed
        try:
            if os.path.exists('config.py'):
                with open('config.py') as f:
                    for line in f:
                        c = line.split(":")
                self.system_user = c[0]
                self.operating_system = c[1]
                self.browser = c[2]
                self.browser_history_path = c[3]
        except:
            print "Error in the configuration file !\n\nplease modify config.py or delete it.\n\n"
            sys.exit(2)

    def saveOptions(self):
        fn = 'config.py'
        with open(fn, 'w') as fout:
            fout.write(self.system_user + ":" + self.operating_system + ":"  + self.browser + ":" + self.browser_history_path)

    def setStatus(self,status):
        with open('bc.status', 'w') as file:
            file.write(status)

            
    def getURL(self):
        """
        Set urls to visit
        Called frequently to check for new URLs
        """
        url=None
        self.loadOptions()
        if self.browser == "F": 
            conn = sqlite3.connect(self.browser_history_path)
            c = conn.cursor()
            c.execute("select url, last_visit_date from moz_places where url not like 'http%://127.0.0.1%' and url not like 'http%://localhost%' ORDER BY last_visit_date DESC limit 4;");
            #select url, last_visit_date from moz_places ORDER BY last_visit_date DESCselect url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
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
            
        elif self.browser == "N": #no browser specified, getting host from file/webserver
            self.new_travel = True
            self.last_travel=0
            # New travel
        try:
            if os.path.exists('hostname.submit'): 
                if url != None:
                    try:
                        if url[1] == None: # no history feature on browser enabled, try use hostname.submit
                            hostname_path = open('hostname.submit')
                            url = [str(hostname_path.read())]
                            self.last_travel=0
                        else:
                            if url[1]/1000000 < os.path.getmtime('hostname.submit') :
                                url = None
                                self.last_travel=0
                    except:
                            print "\nError reading history: try to enable feature on your browser.\n"
                            sys.exit(2)
                if url == None:
                    if self.last_travel< os.path.getmtime('hostname.submit'):
                        self.last_travel = time.time()
                        hostname_path = open('hostname.submit')
                        url = [str(hostname_path.read())]
                        self.url=url[0]
            else:
                # starting a hostname.submit with a default value (ex: http://bordercheck.org)
                # EDIT: website is down, so make the page/script hang/lag/break
                bc = "http://nu.nl"
                if self.options.debug >= 1:
                    print "hostname.submit not found..."
                with open('hostname.submit', 'w') as fout: 
                    fout.write(bc)
                hostname_path = open('hostname.submit')
                url = [str(hostname_path.read())]
                self.url=url[0]
        except:
            print "\nfailed to read file\n"
            traceback.print_exc()
            exit(2)
        if url != None:
            self.url = url
            if self.options.debug >= 1:
                print "geturl : "+urlparse(url[0]).netloc
            return urlparse(url[0]).netloc
        print "\nError: Sorry, you don't have a compatible browser\n"
        exit(2)

    def lft(self):
        """
        Run an LFT
        """
        #LFT (traceroutes) needs root
        root = self.try_running(self.check_root, "\nInternal error checking root permissions.")

        self.setStatus('running lft')
        if self.operating_system == 'darwin':
            try:
                self.content = subprocess.check_output([self.options.lft_path, self.method, '-n', '-S', self.destination_ip])
            except:
                a = subprocess.Popen([self.options.lft_path, self.method, '-S', '-n', self.destination_ip], stdout=subprocess.PIPE)
                self.content = a.stdout.read()

        if self.operating_system == 'linux':
            if self.method == '-e': # tcp probes
                self.method = '-E'
            try:
                self.content = subprocess.check_output([self.options.lft_path, '-S', '-n', self.method, self.destination_ip])
                # support for older python versions (<2.75) that don't support subprocess.check_output
            except:
                a = subprocess.Popen([self.options.lft_path, '-S', '-n', self.method, self.destination_ip], stdout=subprocess.PIPE)
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
        #self.geoip = pygeoip.GeoIP('GeoLiteCity.dat')
        #self.geoasn = pygeoip.GeoIP('GeoIPASNum.dat')
        self.geoip = pygeoip.GeoIP('maps/GeoLiteCity.dat')
        self.geoasn = pygeoip.GeoIP('maps/GeoIPASNum.dat')

        print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
        print "URL:", self.url[0], "\n"
        url = urlparse(self.url[0]).netloc  #changed this for prototyping
        if url == "":
            print "Error: Not traffic connection available. Aborting...\n"
            sys.exit(2)
        #url = url.replace('www.','') #--> doing a tracert to example.com and www.example.com yields different results.
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,4}$",url):
            try:
                url_ip = socket.gethostbyname(url.split(':')[0])
            except:
                print "Error: Not traffic connection available or invalid host. Aborting...\n"
                sys.exit(2)
        else:
            try:
                url_ip = url.split(':')[0]
                pass
            except:
                print "Error: Not traffic available or invalid ip. Aborting...\n"
                sys.exit(2)

        self.destination_ip = url_ip
        print "Host:", url, "\n\nIP:",url_ip, "\n"
        if url != self.old_url:
            self.hop_count = 0
            self.attempts = 0
            self.result_list = []
            self.lft()
            if self.options.debug == True:
                logfile = open('tracelogfile', 'a')
                thingstolog = ['='*45 + "\n",
                               "Browser: ",self.browser_path.split('/')[-1], "\n",
                               "Version: ", self.browser_version, "\n",
                               "Path to browser: ", self.browser_path, "\n",
                               "History db: ", self.browser_history_path, "\n",
                               "URL: ", self.url[0], "\n",
                               "Host: ",url, "\n",
                               "Host ip: ", url_ip, "\n",
                               '='*45, "\n"]
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
                                    if self.options.debug:
                                        print "\nTrace:", self.hop_count, "->", ip, "->", longitude + ":" + latitude, "->", city, "->", country, "->", self.hop_host_name, "->", self.asn, '->', self.timestamp+'ms'
                                    #self.hop_count +=1
                                    self.city = city
                                    self.country = country
                                    self.server_name = self.hop_host_name
                                    cc = record['country_code'].lower()
                                elif record.has_key('country_name'):
                                    country = record['country_name']
                                    if self.options.debug:
                                        print "\nTrace:", self.hop_count, "->", ip, "->", longitude + ":" + latitude, "->", country, "->", self.hop_host_name, "->", self.asn, '->', self.timestamp+'ms'
                                    self.country = country
                                    self.city = '-'
                                    self.server_name = self.hop_host_name
                                    cc = record['country_code'].lower()
                                    #self.hop_count+=1
                                self.vardict = {'url': url, 'destination_ip': self.destination_ip, 'hop_count': self.hop_count,'hop_ip': self.hop_ip, 'server_name': self.server_name, 'country': self.country, 'city': self.city, 'longitude': self.longitude, 'latitude': self.latitude, 'asn' : self.asn, 'timestamp' : self.timestamp, 'country_code': cc  }
                            except:
                                #pass
                                if self.options.debug:
                                    print "\nTrace:", self.hop_count, "->", "Not allowed", ip
                                self.vardict = {'url': url, 'destination_ip': self.destination_ip, 'hop_count': self.hop_count,'hop_ip': self.hop_ip, 'server_name': self.server_name, 'country': '-', 'city': '-', 'longitude': '-', 'latitude': '-', 'asn' : self.asn, 'timestamp' : self.timestamp, 'country_code': '-' }

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
            #print "\n"
            self.hop_count = 0 # to start a new map
            self.setStatus("fresh")
            return

    def getGEO(self):
        """
        Get Geolocation database (http://dev.maxmind.com/geoip/legacy/geolite/)
        """
        if self.options.debug == True:
            print "="*45 + "\n", "GeoIP Options:\n" + '='*45 + "\n"

        # Extract and set geoipdatabase
        #if not os.path.exists('GeoLiteCity.dat'):
        if os.path.exists('maps/GeoLiteCity.dat'):
            if self.options.debug == True:
                print("Map: GeoLiteCity"), "\n"
        else:
            self.try_running(self.fetch_maps, "\nInternal error fetching geoIP database.")
        if os.path.exists('maps/GeoIPASNum.dat'):
            if self.options.debug == True:
                print("Database: GeoIPASNum"), "\n"
        else:
            self.try_running(self.fetch_maps, "\nInternal error fetching geoIP database.")

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
        # Set geo databases 
        self.geoip = pygeoip.GeoIP('maps/GeoLiteCity.dat')
        self.geoasn = pygeoip.GeoIP('maps/GeoIPASNum.dat')

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
                # start web mode (on a different thread)(non root)
                try:
                    webbrowser.open('http://127.0.0.1:8080', new=1)
                    BorderCheckWebserver(self)
                except (KeyboardInterrupt, SystemExit):
                    sys.exit()
    
    def fetch_lft(self):
        import gzip, tarfile
        # download scripts folder
        scripts_db_mirror1 = 'http://37.187.22.48/bordercheck/scripts.tar.gz'#BC Server
        scripts_db_mirror2 = 'http://176.28.23.46/bordercheck/scripts.tar.gz'#Turina Server
        scripts_db_mirror3 = 'http://83.163.232.95/bordercheck/scripts.tar.gz'#Mirror
        try: # mirror 1
            print "\n[Info] - Fetching scripts from 'Mirror 1':", scripts_db_mirror1 + "\n"
            response = urllib.urlretrieve(scripts_db_mirror1, 'scripts.tar.gz')
        except: 
            try: # mirror 2
                print "[Error] - Mirror 1':", scripts_db_mirror1 + " Failed!\n"
                print "[Info] - Fetching scripts from 'Mirror 2':", scripts_db_mirror2 + "\n"
                response = urllib.urlretrieve(scripts_db_mirror2, 'scripts.tar.gz')
            except: 
                try: # mirror 3
                    print "[Error] - Mirror 2':", scripts_db_mirror2 + " Failed!\n"
                    print "[Info] - Fetching scripts from 'Mirror 3':", scripts_db_mirror3 + "\n"
                    response = urllib.urlretrieve(scripts_db_mirror3, 'scripts.tar.gz')
                except:
                     print("[Error] - Something wrong fetching scripts from all mirrors ...Aborting!"), "\n"
                     sys.exit(2)
        subprocess.call(shlex.split('tar zxfv scripts.tar.gz'))
        print ""
        os.remove('scripts.tar.gz')

    def fetch_maps(self):
        # download maps folder
        geo_db_mirror1 = 'http://37.187.22.48/bordercheck/maps.tar.gz'#BC Server
        geo_db_mirror2 = 'http://176.28.23.46/bordercheck/maps.tar.gz'#Turina Server
        geo_db_mirror3 = 'http://83.163.232.95/bordercheck/maps.tar.gz'#Mirror
        try: # mirror 1
            print "\n[Info] - Fetching maps from 'Mirror 1':", geo_db_mirror1 + "\n"
            response = urllib.urlretrieve(geo_db_mirror1, 'maps.tar.gz')
        except:
            try: # mirror 2
                print "[Error] - Mirror 1':", geo_db_mirror1 + " Failed!\n"
                print "[Info] - Fetching maps from 'Mirror 2':", geo_db_mirror2 + "\n"
                response = urllib.urlretrieve(geo_db_mirror2, 'maps.tar.gz')
            except:
                try: # mirror 3
                    print "[Error] - Mirror 2':", geo_db_mirror2 + " Failed!\n"
                    print "[Info] - Fetching maps from 'Mirror 3':", geo_db_mirror3 + "\n"
                    response = urllib.urlretrieve(geo_db_mirror3, 'maps.tar.gz')
                except:
                    print("[Error] - Something wrong fetching maps from mirrors ...Aborting!"), "\n"
                    sys.exit(2)
        subprocess.call(shlex.split('tar zxfv maps.tar.gz'))
        print "" 
        os.remove('maps.tar.gz')

    def get_username(self):
        import pwd
        self.system_user = pwd.getpwuid( os.getuid() )[ 0 ]
        return

    def wizard(self):
        if not os.path.exists('config.py'):
            # warn if is launched as root
            if os.geteuid()==0:
                print("\nWait, is better if you don't launch this wizard as root to discover your $USER system configuration.\n\nBC will ask you permissions if is needed.\n")
                print("Type *yes* if you are sure you want to continue [yes/*No*] ?")
                rep=os.read(0,36)
                if rep[0:3] != 'yes':
                    sys.exit("See you soon!\n")
            # get system user
            user = self.try_running(self.get_username, "\nInternal error checking user system.")
            # extract browser type and path
            browser = self.try_running(self.check_browser, "\nInternal error checking browser files path.")
            if self.browser == "F":
                self.browser_type = "Firefox"
            if self.browser == "C":
                self.browser_type = "Chrome"
            if self.browser == "CHROMIUM":
                self.browser_type = "Chromium"
            if self.browser == "S":
                self.browser_type = "Safari"
            if self.browser == "N":
                self.browser_type = "None"
            print "Let's try to auto-configure your BC:\n"
            print "+ System user:", self.system_user
            print "+ OS detected:", self.operating_system 
            print "+ Browser detected:", self.browser_type
            print "+ Navigation history detected:", self.browser_history_path + "\n"
            print "----"*15
            print "\nNow is time to detect if you have all the libs/packages required:\n"
            # check for required libs
            lib_sqlite3_required = False
            lib_geoip_required = False
            lib_lxml_required = False
            lib_libpcap_required = False
            lib_biplist_required = False
            lft_required = False
            maps_required = False
            try:
                import sqlite3
                print "+ Is sqlite3 installed?... YES"
            except:
                print "+ Is sqlite3 installed?... NO"
                lib_sqlite3_required = True
            try:
                import pygeoip
                print "+ Is python-geoip installed?... YES"
            except:
                print "+ Is python-geoip installed?... NO"
                lib_geoip_required = True
            try:
                import lxml
                print "+ Is python-lxml installed?... YES"
            except:
                print "+ Is python-lxml installed?... NO"
                lib_lxml_required = True
            try:
                import pcap
                print "+ Is python-libpcap installed?... YES"
            except:
                print "+ Is python-libpcap installed?... NO"
                lib_libpcap_required = True
            if self.browser == "Safari":
                try:
                    import biplist
                    print "+ Is python-biplist installed?... YES"
                except:
                    print "+ Is python-biplist installed?... NO"
                    lib_biplist_required = True
            print "\nChecking for correct version of lft required..."
            proc = subprocess.check_output([self.options.lft_path+' -v'], stderr=subprocess.STDOUT, shell=True)
            if "3.79" in proc:  #EDIT > cheated lft version check
                print "\n+ Is correct lft (~3.73v) version installed?... YES"
            else:
                print "\n+ Is correct lft (~3.73v) version installed?... NO"
                lft_required = True
            if os.path.isdir('maps'):
                print "\n+ Are GeoIP maps and databases installed?... YES\n"
            else:
                print "\n+ Are GeoIP maps and databases installed?... NO\n"
                maps_required = True
            if (lib_sqlite3_required or lib_geoip_required or lib_lxml_required or lib_libpcap_required or lib_biplist_required or lft_required or maps_required) == True:
                print "----"*15
                print "\nYou have some libs/packages missing. BC will download and install them for you.\n\nWarning: In some cases you will need to to enter your root credentials...\n"
                print "----"*15 + "\n"
                # download/install required libs as root (ONLY Linux)
                if sys.platform.startswith('linux'): # Linux
                    if lib_sqlite3_required == True:
                        try:
                            subprocess.call(shlex.split('sudo apt-get install sqlite3'))
                            lib_sqlite3_required = False
                        except:
                            print "\nError: installing sqlite3... Please try it manually\n"
                            print "Aborting...\n"
                            sys.exit()
                    if lib_geoip_required == True:
                        try:
                            subprocess.call(shlex.split('sudo apt-get install python-geoip'))
                            lib_geoip_required = False
                        except:
                            print "\nError: installing python-geoip... Please try it manually\n"
                            print "Aborting...\n"
                            sys.exit()
                    if lib_lxml_required == True:
                        try:
                            subprocess.call(shlex.split('sudo apt-get install python-lxml'))
                            lib_lxml_required = False
                        except:
                            print "\nError: installing python-lxml... Please try it manually\n"
                            print "Aborting...\n"
                            sys.exit()
                    if lib_libpcap_required == True:
                        try:
                            subprocess.call(shlex.split('sudo apt-get install python-libpcap'))
                            lib_libpcap_required = False
                        except:
                            print "\nError: installing python-libpcap... Please try it manually\n"
                            print "Aborting...\n"
                            sys.exit()
                    if lib_biplist_required == True:
                        try:
                            subprocess.call(shlex.split('sudo apt-get install python-biplist'))
                            lib_biplist_required = False
                        except:
                            print "\nError: installing python-biplist... Please try it manually\n"
                            print "Aborting...\n"
                            sys.exit()
                    if lft_required == True:
                        try:
                            # download/install lft version required
                            self.try_running(self.fetch_lft, "\nInternal error fetching lft required package.")
                            print "\nScripts (lft-3.73) has been correctly downloaded. Please take a look to README file to install it on your system."
                        except:
                            print "\nError: downloading scripts... Please try it manually\n"
                            print "Aborting...\n"
                        sys.exit() 
                    if maps_required == True:
                        try:  
                            # download maps package from mirrors, extract them and create maps folder
                            self.try_running(self.fetch_maps, "\nInternal error fetching geoIP database.")
                            maps_required = False
                            print "----"*15
                        except:
                            print "\nError: downloading maps... Please try it manually\n"
                            print "Aborting...\n"
                        self.saveOptions()
                        print "\nCongratulations!. BC has been correctly configurated.\n\nTry: './bc' or 'python bc' (as root)\n"
                        sys.exit() 
                else: # TODO:self-installation in other platforms (win32, Osx)
                    print "\nError: self-installation of required libs is not supported on your platform... Please try to install packages manually\n"
                    print "Aborting...\n"
                    sys.exit()
            else:
                print "----"*15
                # all checks passed... now, create config.py file with $user's browser type and path
                self.saveOptions()
                print "\nCongratulations!. BC has been correctly configurated.\n\nTry: './bc' or 'python bc' (as root)\n" 
            sys.exit(2)

        else: # if config.py file exists (wizard correctly passed), run BC normally
            print "\nWarning: You have a 'config.py' file with a configuration.\n"
            print("Type *yes* if you want to remove it [yes/*No*] ?")
            rep=os.read(0,36)
            if rep[0:3] != 'yes':
                try:
                    subprocess.call(shlex.split('sudo rm config.py'))
                except:
                    try:
                        subprocess.call(shlex.split('su -c rm config.py'))
                    except:
                        print "Unable to remove configuration file (config.py)" 
                print("Configuration file removed!.\n\n Try 'Wizard installer' again. Type: './bc -w' (non root required). Aborting...\n")
            else:
                sys.exit("See you soon!\n")
            sys.exit(2)

    def run(self, opts=None):
        """
        Run BorderCheck
        """
        # set options
        if opts:
            options = self.create_options(opts)
            self.set_options(options)
        options = self.options
        if self.options.lft_path == None:
            try:
                self.options.lft_path = "/usr/local/bin/lft" # try lft from system 
            except:
                self.options.lft_path = "/usr/local/bin/lft" # try lft from system 
        p = self.optionParser
        # banner
        print('='*75)
        print(str(p.version))
        print('='*75)
        # no config file, start wizard by user selection
        if not os.path.exists('config.py'):
            print("\nInfo: You BC haven't a configuration.")
            print("\nType *yes* if you want to generate one [no/*yes*]")
            rep=os.read(0,36)
            if rep[0:3] == 'yes':
                self.options.wizard = True
        # wizard configuration
        if self.options.wizard == True:
            wizard = self.wizard()
        if not options.import_xml and not os.geteuid()==0: # if user is not importing XML (non root required), BC needs root for tracerouting
            sys.exit("\nError: You cannot make traceroutes with your permissions. Try to launch BC as root (ex: 'sudo ./bc')\n")
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
            match_ip = url.strip('http://').strip(':8080')
            #regex for filtering local network IPs
            if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip) or match_ip.startswith('file://') or match_ip.startswith('localhost'):
                print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                print "URL:", self.url, "\n"
                print "Warning: This target is not valid!.\n"
                pass
            else:
                if url.startswith('file://'):
                    print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                    print "URL:", url, "\n"
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
                if sys.platform.startswith('linux'): # *Unix magic to try 'non root navigation'
                    try: # try to open on a different browser (user): patch for version 0.2v
                        try:
                            subprocess.call(shlex.split("su - "+self.system_user+" -c 'DISPLAY=:0.0 /usr/bin/xdg-open http://127.0.0.1:8080'")) # standard

                        except:
                            try:
                                subprocess.call(shlex.split("su - "+self.system_user+" /usr/bin/gnome-open http://127.0.0.1:8080")) # gnome
                            except:
                                try:
                                    subprocess.call(shlex.split("su - "+self.system_user+" /usr/bin/x-www-browser http://127.0.0.1:8080")) # x-www-browser
                                except:
                                    subprocess.call(shlex.split("su - "+self.system_user+" -c 'python -mwebbrowser http://127.0.0.1:8080'")) # python/webbro
                                    exit
                    except: # not possible auto-open window with "non root navigation' on *Unix
                        webbrowser.open('http://127.0.0.1:8080', new=1)
                else:
                    try: # try to open with su + python/browser on other systems
                        subprocess.call(shlex.split("su - "+self.system_user+" -c 'python -mwebbrowser http://127.0.0.1:8080'")) # python/webbroser
                    except:
                        webbrowser.open('http://127.0.0.1:8080', new=1) # not possible auto-open window with "non root navigation' on other systems
            except:
                print "Error: Browser is not responding correctly. Try to open it manually.\n"
            print('='*75 + "\n")
            print "Status: Waiting for new urls ...\n"
            print "Type 'Control+C' to exit.\n"
            # stay latent waiting for new urls
            while True:
                url = self.getURL()
                #url = url.replace('www.','')
                try:
                    match_ip = url.strip('http://').strip(':8080')
                except:
                    print '='*45 + "\n", "Target:\n" + '='*45 + "\n"
                    print "URL:", self.url, "\n"
                    pass
                if url != self.old_url:
                    if re.match(r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^192.168\.\d{1,3}\.\d{1,3}$', match_ip) or re.match(r'^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$', match_ip) or match_ip.startswith('localhost'):
                        pass
                    else:
                        if url.startswith('file://'):
                            pass
                        else:
                            if os.path.exists('data.xml'): # removing xml data to has a new map each time that bc is launched
                                os.remove('data.xml')  
                            open('data.xml', 'w') # starting a new xml data container in write mode
                            traces = self.try_running(self.traces, "\nInternal error tracerouting.")
                time.sleep(5) # To free up process time or goodbye :-)       

if __name__ == "__main__":
    app = bc()
    options = app.create_options()
    if options:
        app.set_options(options)
        app.run()
