#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
import optparse

class BCOptions(optparse.OptionParser):
    def __init__(self, *args):
        optparse.OptionParser.__init__(self, 
                           prog='bc.py',
			   version='\nBC (Border-Check) 0.1v - 2013 - (GPLv3.0) -> by psy\n',
                           usage= '\n\nbc [OPTIONS]')

        self.add_option("-d", "--debug", action="store_true", dest="debug", help="debug mode")

    def get_options(self, user_args=None):
        (options, args) = self.parse_args(user_args)
        return options

