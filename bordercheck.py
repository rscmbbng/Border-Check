#!/usr/bin/python

import sqlite3, os, time, pygeoip,re
from urlparse import urlparse
import subprocess, socket




def getURL():
	## function to get the last visited URL from the browser history database. This is only for Firefox.
	## However the Chrome database works in a similar way, just with different tables. I believe it's not to hard
	## to produce a function like this for every browser. The difficulty would be for a user to give the path to the 
	## history file.

	conn = sqlite3.connect('path/to/firefox/places.sqlite')
	c = conn.cursor()
	c.execute('select url, last_visit_date from moz_places ORDER BY last_visit_date DESC')
	url = c.fetchone()
	return url[0]



## Location of the GeoIP database. Currently using this one: http://dev.maxmind.com/geoip/legacy/geolite/
## Perhaps better databases are available. 
geoip= pygeoip.GeoIP('path/to/geoipdatabase.dat')

old_url=""

## the main loop, always running, checks once in 5 seconds if there is a new URL in the browser history.
while True:

	## get the URL from the browser history, strip it down to the host, convert that to ip adress.
	url = urlparse(getURL()).netloc
	# url = url.replace('www.','') --> doing a tracert to for example.com and www.example.com yields different results most of the times.
	url_ip = socket.gethostbyname(url)
	if url != old_url:
		count = 0
		print url

		## Run LFT (layer four traceroute) on the ip as a subprocess and pipe back into script.
		## In NL this has worked flawlessly for me
		## however since i'm in the Laboral all tracerts using TCP fail and the one with UDP find a path, but
		## fail to reach the destination. Perhaps it has to do with the network configuration here, but we should 
		## look into it. 

		#a = subprocess.Popen(['lft', '-S', '-n', '-e', url_ip], stdout=subprocess.PIPE) -> using tcp
		a = subprocess.Popen(['lft', '-S', '-n', '-u', url_ip], stdout=subprocess.PIPE) # -> using udp
		logfile = open('logfile', 'a')

		for line in a.stdout:
			#log results.
			logfile.write(line)

			## Parsing the results from LFT. If it finds an ip adress compare it against the database and print the results
			parts = line.split()
			for ip in parts:
				if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
					record = geoip.record_by_addr(ip)
					#print record
					if record.has_key('country_name') and record['city'] is not '':
						country = record['country_name']
						city = record['city']
						print count, "While surfing you got to "+ip+" which is in "+city+", "+country
					elif record.has_key('country_name'):
						country = record['country_name']		
						print count, "While surfing you got to "+ip+" which is in "+country
					time.sleep(0.1)
					count+=1
		old_url = url
		print"old url =",old_url
	logfile.close()
	time.sleep(5)
