#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013-2014-2015 by psy (epsylon@riseup.net)
"""
class xml_reporting(object):
    """
    Print results from a traceroute in an XML fashion
    """
    def __init__(self, bc):
        # initialize main BC
        self.instance = bc

    def print_xml_results(self, filename):
        import xml.etree.ElementTree as ET
        root = ET.Element("travel")
        i = 1
        for i in self.instance.result_list:
            hop = ET.SubElement(root, "hop")
            host = ET.SubElement(hop, "host")
            hop_ip = ET.SubElement(hop, "hop_ip")
            longitude = ET.SubElement(hop, "longitude")
            latitude = ET.SubElement(hop, "latitude")
            city = ET.SubElement(hop, "city")
            country = ET.SubElement(hop, "country")
            server_name = ET.SubElement(hop, "server_name")
            asn = ET.SubElement(hop, "asn")
            timestamp = ET.SubElement(hop, "timestamp")
            country_code = ET.SubElement(hop,"country_code")
            meta = ET.SubElement(hop, "meta")

            root.text = i['url']
            hop.text = str(i['hop_count'])
            host.text = i['destination_ip']
            hop_ip.text = i['hop_ip']
            longitude.text = i['longitude']
            latitude.text = i['latitude']
            city.text = i['city']
            country.text = i['country']
            server_name.text = i['server_name']
            asn.text = i['asn']
            timestamp.text = i['timestamp']
            country_code.text = i['country_code']
            meta.text = "Connect here XML metadata"

            tree = ET.ElementTree(root)
            tree.write(filename)

    def read_xml_results(self):
        from xml.dom.minidom import parseString   
        file = open(self.instance.options.import_xml,'r')
        data = file.read()  
        file.close()        
        dom = parseString(data)
        travel_tag = dom.getElementsByTagName('travel')[0].toxml()
        travel_data = travel_tag.replace('<travel>','').replace('</travel>','').split('<')[0]
        hop_tag = dom.getElementsByTagName('hop')[0].toxml()
        hop_data = hop_tag.replace('<hop>','').replace('</hop>','')
        host_tag = dom.getElementsByTagName('host')[0].toxml()
        host_data = host_tag.replace('<host>','').replace('</host>','')
        hop_ip_tag = dom.getElementsByTagName('hop_ip')[0].toxml()
        hop_ip_data = hop_ip_tag.replace('<hop_ip>','').replace('</hop_ip>','')
        longitude_tag = dom.getElementsByTagName('longitude')[0].toxml()
        longitude_data = longitude_tag.replace('<longitude>','').replace('</longitude>','')
        latitude_tag = dom.getElementsByTagName('latitude')[0].toxml()
        latitude_data = hop_tag.replace('<latitude>','').replace('</latitude>','')
        city_tag = dom.getElementsByTagName('city')[0].toxml()
        city_data = city_tag.replace('<city>','').replace('</city>','')
        country_tag = dom.getElementsByTagName('country')[0].toxml()
        country_data = country_tag.replace('<country>','').replace('</country>','')
        server_name_tag = dom.getElementsByTagName('server_name')[0].toxml()
        server_name_data = server_name_tag.replace('<server_name>','').replace('</server_name>','')
        asn_tag = dom.getElementsByTagName('asn')[0].toxml()
        asn_data = asn_tag.replace('<asn>','').replace('</asn>','')
        timestamp_tag = dom.getElementsByTagName('timestamp')[0].toxml()
        timestamp_data = timestamp_tag.replace('<timestamp>','').replace('</timestamp>','')
        country_code_tag = dom.getElementsByTagName('country_code')[0].toxml()
        country_code_data = country_code_tag.replace('<country_code>','').replace('</country_code>','')
        meta_tag = dom.getElementsByTagName('meta')[0].toxml()
        meta_data = meta_tag.replace('<meta>','').replace('</meta>','')
        
        return travel_data, hop_data, hop_ip_data, longitude_data, latitude_data, city_data, country_data, server_name_data, asn_data, timestamp_data, country_code_data, meta_data
