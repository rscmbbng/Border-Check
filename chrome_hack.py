#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sqlite3, os, filecmp


def Chrome_History_Hack(history_path):
	# A hack to deal with the fact that Chrome puts an exclusive lock on the history database
	# It copies the history database and accesses that instead of the locked file.
	# Afterwards the database copy is removed. 
	a = history_path+'Copy'
	if os.path.exists(a):
		if filecmp.cmp(history_path, a) == False:
			os.system('rm '+a)
			os.system('cp "'+history_path+'" "'+a+'"')
	else:
		os.system('cp "'+history_path+'" "'+a+'"')

	conn = sqlite3.connect(a)
	c = conn.cursor()
	c.execute('select urls.url, urls.last_visit_time FROM urls ORDER BY urls.last_visit_time DESC')
	url = c.fetchone()
	os.system('rm "'+a+'"')
	return url[0]

#print Chrome_History_Hack(chromium_osx)

