#!/usr/bin/python
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
        for i in range(self.instance.hop_count):
            hop = ET.SubElement(root, "hop")
            host = ET.SubElement(hop, "host")
            ip = ET.SubElement(hop, "ip")
            longitude = ET.SubElement(hop, "longitude")
            latitude = ET.SubElement(hop, "latitude")
            city = ET.SubElement(hop, "city")
            country = ET.SubElement(hop, "country")
            server_name = ET.SubElement(hop, "server_name")
            meta = ET.SubElement(hop, "meta")

            hop.text = str(i)
            host.text = self.instance.url[0]
            ip.text = self.instance.ip
            longitude.text = self.instance.longitude
            latitude.text = self.instance.latitude
            city.text = self.instance.city
            country.text = self.instance.country
            server_name.text = self.instance.server_name
            meta.text = "Connect here XML metadata"

            tree = ET.ElementTree(root)
            tree.write(filename)

