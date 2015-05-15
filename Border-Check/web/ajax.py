#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013-2014-2015 by psy (epsylon@riseup.net)
"""
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import re
import traceback
reload=False

try:
  bc_status_file = open('bc.status')
  s = str(bc_status_file.read())
  if s =='fresh':
    with open('bc.status', 'w') as file:
      file.write("old")
    reload=True
except:
  pass

# todo :
# * call ajax.py from here
# * save last url timestamp as get parameter
# * do parsing only if timestamp changes
# * ui integration

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


def extract_data():
  url=""
  hop_list = []
  hop_ip_list =[]
  geoarray = []
  latlong= []
  asn_list =[]
  server_name_list = []
  timestamp_list = []
  telco_list = []
  country_code_list = []
  last_hop = 0
  n_hops=0
  unique_country_code_list = []
  # extract data from a xml file
  f = open('data.xml', 'r')
  f2 = open('data.xml', 'r')
  xml = ET.parse(f)
  data = f2.read()
  dom = parseString(data.encode('utf-8'))
  f.close()
  f2.close()
  last_hop = int(xml.findall('hop')[-1].text)
  n_hops = dom.getElementsByTagName('hop')[-1].toxml().replace('<hop>', '').replace('</hop','')


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
    asn_list.append(ASN_Split(asn.encode('utf-8'))[0])
    telco_list.append(ASN_Split(asn.encode('utf-8'))[1])
    hop = int(hop) +1
    hop_list.append(str(hop))
    hop_ip_list.append(hop_ip.encode('utf-8'))
    server_name_list.append(server_name.encode('utf-8'))
    timestamp_list.append(float(timestamp))
    country_code_list.append(country_code.encode('utf-8'))

    unique_country_code_list = set(country_code_list)
  return """
<script type="text/javascript">
    counter_max = """+str(last_hop)+"""
    latlong = """+str(geoarray)+"""
    asn_list = """+str(asn_list)+"""
    hop_ip_list = """+str(hop_ip_list)+"""
    telco_list = """+str(telco_list)+"""
    server_name_list = """+str(server_name_list)+"""
    timestamp_list = """+str(timestamp_list)+"""
    country_code_list = """+str(country_code_list)+"""
    unique_country_code_list = """+str(list(unique_country_code_list))+"""
    bcHistory.add('"""+url+"""',Array(counter_max,latlong,asn_list, hop_ip_list,telco_list,server_name_list,timestamp_list,country_code_list,unique_country_code_list))
</script>
"""

try:
  if reload:
    output=extract_data()

except:
  args['error']="No data available"
  traceback.print_exc()
  reload=False

if 'error' in args:
  output=output+'<script>$("#error").html("'+args['error']+'")</script>'
