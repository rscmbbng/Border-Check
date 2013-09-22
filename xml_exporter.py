#!/usr/local/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
import xml.etree.ElementTree as ET

class xml_reporting(object):
    """
    Print results from a traceroute in an XML fashion
    """
    def __init__(self, bc):
        # initialize main BC
        self.instance = bc

    def print_xml_results(self, filename):
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

