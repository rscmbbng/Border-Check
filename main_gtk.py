#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""
BC (Border-Check) is a tool to retrieve info of traceroute tests over website navigation routes.
GPLv3 - 2013 by psy (epsylon@riseup.net)
"""
import sys
try:
    import gtk, gtk.glade
except:
    print ("\nError importing: Gtk/Glade libs. \n\nOn Debian based systems, please try like root:\n\n $ apt-get install python-gtk2\n")
    sys.exit(2)

class GuiUtils(object):
    @staticmethod
    def GetBuilder(name):
        builder = gtk.Builder()
        if not builder.add_from_file('builder.xml'):
            print 'XML file not found!'
            sys.exit(1)
        else:
            return builder

    @staticmethod
    def Error(title, text):
        """Show error popup"""
        dialog = gtk.MessageDialog(
            parent         = None,
            flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
            type           = gtk.MESSAGE_ERROR,
            buttons        = gtk.BUTTONS_OK,
            message_format = text)
        dialog.set_title(title)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
        print text
    
    @staticmethod
    def Info(title, text):
        """Show info popup"""
        dialog = gtk.MessageDialog(
            parent         = None,
            flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
            type           = gtk.MESSAGE_INFO,
            buttons        = gtk.BUTTONS_OK,
            message_format = text)
        dialog.set_title(title)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
 
    @staticmethod
    def Loading(title, text):
        """Show loading popup"""
        dialog = gtk.MessageDialog(
            parent         = None,
            flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
            type           = gtk.MESSAGE_INFO,
            buttons        = gtk.BUTTONS_NONE,
            message_format = text)
        dialog.set_title(title)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
        return dialog

    @staticmethod
    def Warning(title, text):
        """Show warning popup"""
        dialog = gtk.MessageDialog(
            parent         = None,
            flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
            type           = gtk.MESSAGE_WARNING,
            buttons        = gtk.BUTTONS_OK,
            message_format = text)
        dialog.set_title(title)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
        return dialog

    @staticmethod
    def Question(title, text):
        """Show question popup"""
        dialog = gtk.MessageDialog(
            parent         = None,
            flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
            type           = gtk.MESSAGE_QUESTION,
            buttons        = gtk.BUTTONS_YES_NO,
            message_format = text)
        dialog.set_title(title)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.show()
        return dialog

class GuiStarter(object):
    """
    Init the starter GUI box.
    """
    def __init__(self):
        """
        Start the GUI up and set the connections with the components.
        """
        builder = GuiUtils.GetBuilder('builder')

        # get objects
        self.window = builder.get_object('builder')

        # defaults

        # signals
