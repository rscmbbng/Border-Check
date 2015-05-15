#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013-2014-2015 by psy (epsylon@riseup.net)
"""
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import re

#function to split ISP company names from ASN
def ASN_Split(asn):
  name_parts = []
  for i in asn.split():
    if re.match(r'AS\d{1,6}$', i):
      asn = i
    elif not re.match(r'AS\d{1,6}$', i):
      name_parts.append(i)
  company = ' '.join(name_parts)
  return (asn, company)

got_data = False
msg=""
url=""

try:
  # extract data from a xml file
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
  telco_list = []
  last_hop = int(xml.findall('hop')[-1].text)
  country_code_list = []
  got_data = True
  url = xml.getroot().text
  for counter in range(0, last_hop+1):
    hop_element = parseString(dom.getElementsByTagName('hop')[counter].toxml().encode('utf-8'))
    hop = xml.findall('hop')[counter].text
    server_name = hop_element.getElementsByTagName('server_name')[0].toxml().replace('<server_name>','').replace('</server_name>','')
    asn = hop_element.getElementsByTagName('asn')[0].toxml().replace('<asn>','').replace('</asn>','')
    hop_ip = hop_element.getElementsByTagName('hop_ip')[0].toxml().replace('<hop_ip>','').replace('</hop_ip>','')
    longitude = hop_element.getElementsByTagName('longitude')[0].toxml().replace('<longitude>','').replace('</longitude>','')
    latitude = hop_element.getElementsByTagName('latitude')[0].toxml().replace('<latitude>','').replace('</latitude>','')
    timestamp = hop_element.getElementsByTagName('timestamp')[0].toxml().replace('<timestamp>','').replace('</timestamp>','')
    country_code = hop_element.getElementsByTagName('country_code')[0].toxml().replace('<country_code>','').replace('</country_code>','')

    if str(asn) == "<asn/>": #parse when no asn present/network owner present
        asn_list.append(str("Not Available"))
        telco_list.append(str("Unknown"))
    else:
        asn_list.append(ASN_Split(asn.encode('utf-8'))[0])
        telco_list.append(ASN_Split(asn.encode('utf-8'))[1])

    latlong = [float(latitude.encode('utf-8')), float(longitude.encode('utf-8'))]
    geoarray.append(latlong)
#    asn_list.append(ASN_Split(asn.encode('utf-8'))[0])
#    telco_list.append(ASN_Split(asn.encode('utf-8'))[1])
    hop = int(hop) +1
    hop_list.append(str(hop))
    hop_ip_list.append(hop_ip.encode('utf-8'))
    server_name_list.append(server_name.encode('utf-8'))
    timestamp_list.append(float(timestamp))
    country_code_list.append(country_code.encode('utf-8'))
  unique_country_code_list = set(country_code_list)

except:
  args['error']="Data error."


if 'error' in args:
  msg=args['error'];
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
  <script src="js/jquery-1.10.2.min.js"></script>
  <script src="js/rlayer-src.js"></script>
  <script src="js/raphael.js"></script>
  <script src="js/bc.js"></script>
  <script src="js/bc-history.js"></script>
  <script src="js/favicon.js"></script>
  <script src="js/cluster/leaflet.markercluster-src.js"></script>
  <script src="js/bc-control.js"></script>


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
      <div class="header" id="status">Travelling to:</div>
      <div class ="header" id="url">"""+url+"""</div>
      <div id="map" style="width: 100%; height: 100%"></div>
      <div class ="bar">
      <div id="button" class='toggle'> > </div>
      <div class = info>
      <div> <img src='images/bclogo.png'></img></div>
      <div id='info-text'>
      <br /><div class='toggle' id='about'>About</div>
      <div id='about-content'>
      <p>As you surf the net, data packets are sent from your computer to the target server. These data packets go on a journey hopping from server to server, potentially crossing multiple countries and networks, until the packets reach the desired website.</p>
      <p> Border Check allows you to retrace the path your data takes across the internet's infrastructure. It will map out all the servers your data passes and shows you in which countries or cities these servers are located. Additionally Border Check will try to provide you with additional data on these servers, such as the companies they belong to.</p>
      <p> Visit the <a href="http://bordercheck.org"> project homepage</a> for more information.
      </div>
      <p class='divider'>------------------------------</p>
      </div>
      <div class='toggle' id='legend'> Map legend </div>
      <div id='legend-content'>
      <center><pre>   <img id="home" class='toggle' src='images/markers/marker-icon-0.png'></img>    <img class='toggle' id="hop" src='images/markers/marker-icon-11.png'></img>   <img  class='toggle'id="cluster" src='images/markers/cluster-marker.png'></img>    <img class='toggle' id="destination" src='images/markers/marker-icon-last.png'></img>    </pre></center>
      <div id=legend-text></div></div>
      <p class='divider'>------------------------------</p>
      <div class='toggle' id='form'>New Travel (enter URL)</div>
      <br />
      <div id='form-content'>
       <center> 
         <form onsubmit="return false" id='host'><input id='form-host' name='hostname' placeholder='http://bordercheck.org'><input id='form-submit' type='button' value='GO'>
       </center>
         <div id='ajax-out'></div>
       <div id='form-target'></div>
       </div>
      <div class='toggle' id='history'>History</div>
      <div id='history-content'>
      </div>
      <p class='divider'>------------------------------</p>
      <div class='toggle' id='contact'>Get in touch</div>
      <div id='contact-content'>
      <br />
      <center>
      Roel Roscam Abbing (rscmbbng@riseup.net) <br />
      psy (epsylon@riseup.net)
      </center>
      <div>
      </div>
      </div>
      <div id='error' style='display:block;color:red'>"""+msg+""" </div>
      </div> 
  </div>"""
if got_data:
  output +="""
<script type="text/javascript">
  cur_url = '"""+url+"""'
  counter_max = """+str(last_hop)+"""
  latlong = """+str(geoarray)+"""
  asn_list = """+str(asn_list)+"""
  hop_ip_list = """+str(hop_ip_list)+"""
  telco_list = """+str(telco_list)+"""
  server_name_list = """+str(server_name_list)+"""
  timestamp_list = """+str(timestamp_list)+"""
  country_code_list = """+str(country_code_list)+"""
  unique_country_code_list = """+str(list(unique_country_code_list))+"""
window.onload = function(){  
  initMap()
  bcHistory.add(cur_url,Array(counter_max,latlong,asn_list, hop_ip_list,telco_list,server_name_list,timestamp_list,country_code_list,unique_country_code_list))
}
  </script>
</html>
"""
