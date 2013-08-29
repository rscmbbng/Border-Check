#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
from main_gtk import GuiStarter, GuiUtils

try:
    import gtk, gtk.glade
except:
    print ("\nError importing: Gtk/Glade libs. \n\nOn Debian based systems, please try like root:\n\n $ apt-get install python-gtk2\n")
    sys.exit(2)

class BCGTK():
    @staticmethod
    def run():
        GuiStarter()
        gtk.main()

