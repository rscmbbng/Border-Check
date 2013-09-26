#!/usr/local/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
  # extract data from a xml file
# try:
f = open('data.xml', 'r')
f2 = open('data.xml', 'r')
xml = ET.parse(f)
data = f2.read()
dom = parseString(data.encode('utf-8'))
f.close()
f2.close()
n_hops = dom.getElementsByTagName('hop')[-1].toxml().replace('<hop>', '').replace('</hop','')
hop_list = []
hop_ip_list =[]
geoarray = []
latlong= []
asn_list =[]
server_name_list = []
timestamp_list = []
last_hop = int(xml.findall('hop')[-1].text)
country_code_list = []

for counter in range(0, last_hop+1):
    url = xml.getroot().text
    hop_element = parseString(dom.getElementsByTagName('hop')[counter].toxml().encode('utf-8'))
    hop = xml.findall('hop')[counter].text
    server_name = hop_element.getElementsByTagName('server_name')[0].toxml().replace('<server_name>','').replace('</server_name>','')
    asn = hop_element.getElementsByTagName('asn')[0].toxml().replace('<asn>','').replace('</asn>','')
    hop_ip = hop_element.getElementsByTagName('hop_ip')[0].toxml().replace('<hop_ip>','').replace('</hop_ip>','')
    longitude = hop_element.getElementsByTagName('longitude')[0].toxml().replace('<longitude>','').replace('</longitude>','')
    latitude = hop_element.getElementsByTagName('latitude')[0].toxml().replace('<latitude>','').replace('</latitude>','')
    timestamp = hop_element.getElementsByTagName('timestamp')[0].toxml().replace('<timestamp>','').replace('</timestamp>','')
    country_code = hop_element.getElementsByTagName('country_code')[0].toxml().replace('<country_code>','').replace('</country_code>','')

    latlong = [float(latitude.encode('utf-8')), float(longitude.encode('utf-8'))]
    geoarray.append(latlong)
    asn_list.append(asn.encode('utf-8'))
    hop = int(hop) +1
    hop_list.append(str(hop))
    hop_ip_list.append(hop_ip.encode('utf-8'))
    server_name_list.append(server_name.encode('utf-8'))
    timestamp_list.append(float(timestamp))
    country_code_list.append(country_code.encode('utf-8'))

unique_country_code_list = set(country_code_list)

x = open('testmap.html','w')
# HTML + JS container
output = """
<html>
<head>
  <title>Border Check - Web Viewer</title>
  <link rel="stylesheet" href="js/leaflet/leaflet.css" />
  <link rel="stylesheet" href="style.css" />
  <link rel="stylesheet" href="js/cluster/MarkerCluster.Default.css"/>
  <link rel="stylesheet" href="js/cluster/MarkerCluster.css"/>
  <script src="js/leaflet/leaflet.js"></script>
  <script src="js/rlayer-src.js"></script>
  <script src="js/raphael.js"></script>
  <script src="js/jquery-1.10.2.min.js"></script>
  <script src="js/bc.js"></script>
  <script src="js/favicon.js"></script>
  <script src="js/cluster/leaflet.markercluster-src.js"></script>


  <script type="text/javascript">
        $(document).ready (function(){
          var h = $(window).innerHeight();
          var w = $(window).innerWidth();
          $("#wrapper").css({
            "width": w, "height": h
            })
          })
  </script>
</head>
<body>
  <div id="wrapper">
      <div class="header">Travelling to:</div>
      <div class ="header" id="url">"""+url+"""</div>
      <div id="map" style="width: 100%; height: 100%"></div>
      <div class ="bar">
      <div id="button"> > </div>
      <div class = info>
      <div> <img src='images/bclogo.png'></img></div>
      <div id='info-text'><p>Border Check (BC) allows you to see all the servers you visit while you browse to a specific website.</p>
      <p>As one surfs the net, data packets are sent from the user's computer to the target server. These data packets go on a journey hopping from server to server, potentially crossing multiple countries, until the packets reach the desired website. In each of the countries that are passed different laws and practices can apply to the data, influencing whether or not authorities can inspect, store or modify that data.</p>
      <p>In realtime BC lets you know which countries you surf through as you browse the web. Additionally BC will illustrate this process on a world map and (where available) provide you with contextualizing information on that country's laws and practices regarding your data.</p>
      <p>Currently supporting the following browsers on OSX and Unix systems: <br /> Firefox, Chromium, Chrome, Safari</p>
      <div>
      </div>
      </div>
      </div>
      
  </div>
<script type="text/javascript">
  hop_list = """+str(hop_list)+"""
  hop_ip_list = """+str(hop_ip_list)+"""
  counter_max = """+str(last_hop)+"""
  latlong = """+str(geoarray)+"""
  asn_list = """+str(asn_list)+"""
  server_name_list = """+str(server_name_list)+"""
  timestamp_list = """+str(timestamp_list)+"""
  country_code_list = """+str(country_code_list)+"""
  unique_country_code_list = """+str(list(unique_country_code_list))+"""
  </script>
</html>
"""
x.write(output)
x.close
# except:
#   output = """
#   <html> loading </html>
#   """
