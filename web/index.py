#!/usr/local/bin/python
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
hop_list = []
hop_ip_list =[]
geoarray = []
latlong= []
asn_list =[]
server_name_list = []
last_hop = int(xml.findall('hop')[-1].text)

for counter in range(1, last_hop+1):
    url = xml.getroot().text
    hop_element = parseString(dom.getElementsByTagName('hop')[counter].toxml().encode('utf-8'))
    hop = xml.findall('hop')[counter].text
    server_name = hop_element.getElementsByTagName('server_name')[0].toxml().replace('<server_name>','').replace('</server_name>','')
    asn = hop_element.getElementsByTagName('asn')[0].toxml().replace('<asn>','').replace('</asn>','')
    hop_ip = hop_element.getElementsByTagName('hop_ip')[0].toxml().replace('<hop_ip>','').replace('</hop_ip>','')
    longitude = hop_element.getElementsByTagName('longitude')[0].toxml().replace('<longitude>','').replace('</longitude>','')
    latitude = hop_element.getElementsByTagName('latitude')[0].toxml().replace('<latitude>','').replace('</latitude>','')

    latlong = [float(latitude.encode('utf-8')), float(longitude.encode('utf-8'))]
    geoarray.append(latlong)
    asn_list.append(asn.encode('utf-8'))
    hop_list.append(str(hop))
    hop_ip_list.append(hop_ip.encode('utf-8'))
    server_name_list.append(server_name.encode('utf-8'))


f = open('kaart.html', 'w')
output = """
<html>
<head>
  <title>Border Check - Web Visualizor</title>
   <link rel="stylesheet" href="js/leaflet/leaflet.css" />
   <link rel="stylesheet" href="style.css" />
    <script src="js/leaflet/leaflet.js"></script>
    <script src= "js/rlayer-modified.min.js"></script>
     <script src= "js/raphael.js"></script>
     <script src="js/jquery-1.10.2.min.js"></script>
     <script type="text/javascript">
        $(document).ready (function(){
          var h = $(window).innerHeight();
          var w = $(window).innerWidth();
          $("#wrapper").css({
            "width": w, "height": h
            })
          }) 

          //$(document).ready( fullScreen())
          //$(window).resize( fullScreen())


  </script>
    </head>
<body>
<div id="wrapper">
    <div id="header">"""+url+"""</div>
    <div id="map" style="width: 100%; height: 100%"></div>
    <div id="bar"><button id='button'><</button></div>
</div>
  <script type="text/javascript">
  window.onload = function () {
    var map = L.map('map',{
        minZoom: 2,
        maxZoom:5,

        }).setView(["""+latitude+""", """+longitude+"""], 3);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

        $('#button').bind('click', function(){
            $('#bar').animate({"width": '200'})
            var info = $("<div id = info><p>this is where info goes</p><p>I will make a 'slide back' option later</p></div>")
                .appendTo("#bar")
            console.log('click')

            })


  var hop_list = """+str(hop_list)+"""
  var hop_ip_list = """+str(hop_ip_list)+"""
  var counter_max = """+str(last_hop)+"""
  var latlong = """+str(geoarray)+"""
  var asn_list = """+str(asn_list)+"""
  server_name_list = """+str(server_name_list)+"""
  //var polyline = L.polyline(latlong, {color: 'red'}).addTo(map);

index = 0

AddStep(latlong[index], latlong[index+1], index)

function AddMarker(src, index){
  var marker = L.marker([src[0], src[1]]).bindPopup(
    "Hop: <b>"+hop_list[index]+"</b><br />"+server_name_list[index]+"<br />"+asn_list[index]
    );
  marker.addTo(map).openPopup()
}

function AddStep(src, dest, index){
  var b = new R.BezierAnim([src, dest], {})
  map.addLayer(b)
  AddMarker(src, index)
  processStep(index)
}

function processStep (index) {
    map.panTo(latlong[index]);
    if (index < counter_max-2) {
      console.log('hop#', hop_list[index])
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index+1], index)
     }, 500);}
      //in the wait function we can add the ms of the actual traceroute to get the (de)acceleration of the real thing
    else
    if (index < counter_max-1){
    console.log('hop#', hop_list[index])
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index], index)
     }, 500);}

    index = index + 1
    }
};
</script>
</html>
"""
f.write(output)
f.close