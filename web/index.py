#!/usr/local/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
from xml.dom.minidom import parseString
# extract data from a xml file
file = open('data.xml','r')
data = file.read()
file.close()
dom = parseString(data)
xmlTag = dom.getElementsByTagName('travel')[0].toxml()
xmlData= xmlTag.replace('<travel>','').replace('</travel>','')
xmlHost = dom.getElementsByTagName('host')[0].toxml()
xmlIP = dom.getElementsByTagName('ip')[0].toxml()
xmlRoutes = dom.getElementsByTagName('routes')[0].toxml()
xmlMeta = dom.getElementsByTagName('meta')[0].toxml()

output = """
<html>
<head>
  <title>Border Check - Web Visualizator</title>
</head>
<body>
<center>
<table>
 <tr>
  <td><div><center><img src="images/WM1.svg"></center></div></td>
 </tr>
  <tr>
  <td>
    <center>
    <table border="1">
        <tr>
          <td><b>Host:</b></td>
          <td>"""+xmlHost+"""</td>
        </tr>
        <tr>
          <td><b>IP:</b></td>
          <td>"""+xmlIP+"""</td>
        </tr>
        <tr>
          <td><b>Packages Route:</b></td>
        <td>"""+xmlRoutes+"""</td>
        </tr>
        <tr>
        <td><b>Metadata:</b></td>
        <td>"""+xmlMeta+"""</td>
     </tr>
    </table>
   </center>
  </tr>
</table>
</center>
</body>
</html>
"""
