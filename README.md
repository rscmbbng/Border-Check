Border Check v.01
=====================
[(información en castellano sobre el uso e instalación de BC aquí)](http://hackingaround.net/pub/seguridad/Border-check-Conociendo-al-gran-hermano-cruzando-leyes-y-trazas.pdf)


Border Check (BC) is a browser extension that illustrates the physical and political realities of the internet's infrastructure using free software tools.

As one surfs the net, data packets are sent from the user's computer to the target server. These data packets go on a journey hopping from server to server, potentially crossing multiple countries, until the packets reach the desired website. In each of the countries that are passed different laws and practices can apply to the data, influencing whether or not authorities can inspect, store or modify that data.

In realtime BC lets you know which countries you surf through as you browse the web. Additionally BC will illustrate this process on a world map and (where available) provide you with contextualizing information on that country's laws and practices regarding your data.

Currently supporting the following browsers on OSX and Unix systems:
Firefox, Chromium, Chrome, Safari

## Options and features:

See the included examples for usage.
```
bc [OPTIONS] 

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d, --debug           debug mode
  --xml=EXPORT_XML      export traces to xml (ex: --xml foo.xml)
  --bh=BROWSER_HISTORY  set browser's history path
  -b BROWSER            set browser manually: F = Firefox / C = Chrome / S = Safari / Ch = Chromium
```

#### Examples of usage:

Normal BC run:

`$ python bc`

Debug mode:

`$ python bc --debug`


Export 'tracing' results to xml:

`$ python bc --xml "mytravel.xml"`

#### Forcing browsers and setting browser history paths manually:

Use Firefox browser: 

`$ python bc -b F`

Use Chromium browser: 

`$ python bc -b Ch` 

Set browser's history path manually, on Galeon/Unix:

`$ python bc --bh ".galeon/mozilla/galeon/places.sqlite"`


Set browser's history path manually, on Chrome/OSx:

`$ python bc --bh "Library/Application Support/Google/Chrome/Default/History"`

Set browser's history path manually, on Safari/OSx:

`$ python bc --bh "Library/Safari/History.plist"` 

Set browser's history path manually, on Firefox/Unix:

`$ python bc --bh "Library/Safari/History.plist"` 

## Installing BC:

BC runs on OSx and Unix systems. It requires the following libraries/dependencies:
###     Python:
* [pygeoip](https://pypi.python.org/pypi/pygeoip/0.2.7) 
* [lxml](https://pypi.python.org/pypi/lxml/3.2.3)
* [biplist](https://pypi.python.org/pypi/biplist/0.5) (if you plan to use Safari)

For **Debian**-based systems (ex: Ubuntu), first run:
`sudo apt-get install python-pip` to install [pip](https://pypi.python.org/pypi/pip/), python's super usefull package manager.

If you already have pip: `pip install lxml` and `pip install pygeoip`

On **OSX** it's recommended you install [Homebrew](http://brew.sh/) first and use that to get [python + pip](https://github.com/mxcl/homebrew/wiki/Homebrew-and-Python).

### LFT
BC uses [LFT v3.35](http://pwhois.org/lft/) for tracerouting.

On **Debian** and **Ubuntu** it needs to be built from source and requires libpcap

On **OSX** you can use Homebrew: `brew install lft` which will automatically download and build the package.


### GeoIP databases and js libraries
BC will automatically download and unpack the newest geoip databases on the first run. Javascript mapping libraries are included in the package at moment.

### License

Border Check is free software, and may be redistributed under [GPL v3](https://github.com/rscmbbng/Border-Check/blob/master/doc/COPYING).

### Contact

Please report any problems you encounter using/installing Border Check to:

 - Roel Roscam Abbing (rscmbbng@riseup.net)
 - psy (epsylon@riseup.net)

Or visit IRC Community:

 - Server: irc.freenode.net 
 - Channel: #BorderCheck

