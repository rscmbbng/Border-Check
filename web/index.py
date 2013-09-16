#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET

# extract data from a xml file
f = open('data.xml', 'r')
f2 = open('data.xml', 'r')
xml = ET.parse(f)
data = f2.read()
dom = parseString(data.encode('utf-8'))
f.close()
f2.close()
n_hops = dom.getElementsByTagName('hop')[-1].toxml().replace('<hop>', '').replace('</hop','')
hoplist = []
geoarray = []
latlong= []

b = ''

for counter in range(1, int(xml.findall('hop')[-1].text)+1):
    hop = parseString(dom.getElementsByTagName('hop')[counter].toxml().encode('utf-8'))
    server_name = hop.getElementsByTagName('server_name')[0].toxml().replace('<server_name>','').replace('</server_name>','')
    asn = hop.getElementsByTagName('asn')[0].toxml().replace('<asn>','').replace('</asn>','')
    hop_ip = hop.getElementsByTagName('hop_ip')[0].toxml().replace('<hop_ip>','').replace('</hop_ip>','')
    longitude = hop.getElementsByTagName('longitude')[0].toxml().replace('<longitude>','').replace('</longitude>','')
    latitude = hop.getElementsByTagName('latitude')[0].toxml().replace('<latitude>','').replace('</latitude>','')

    point = """    L.marker(["""+latitude+""", """+longitude+"""]).addTo(map)
    .bindPopup("<b>"""+server_name+"""</b><br />"""+hop_ip+"""<br />"""+asn+"""<br />").openPopup(); """

    latlong = [float(latitude.encode('utf-8')), float(longitude.encode('utf-8'))]
    geoarray.append(latlong)

    hoplist.append(point)
    b = b+point

output = """
<html>
<head>
  <title>Border Check - Web Visualizator</title>
   <link rel="stylesheet" href="js/leaflet/leaflet.css" />
   <link rel="stylesheet" href="style.css" />
    <script src="js/leaflet/leaflet.js"></script>
    <!--<script src="http://cdn.leafletjs.com/leaflet-0.6.4/leaflet.js"></script>-->
    <script type="text/javascript">
    
  window.onload = function () {
    var map = L.map('map').setView(["""+latitude+""", """+longitude+"""], 2);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  
  """+b+"""
  
  var latlong = """+str(geoarray)+"""
  var polyline = L.polyline(latlong, {color: 'red'}).addTo(map);

};
</script>
</head>
<body>
 <center>
     <td><center><div id="map" style="width: 1000px; height: 800px"></div></center></td>
</body>
</html>
"""
