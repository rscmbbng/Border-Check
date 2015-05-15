Border Check v0.2 - 2015
========================

Border Check (BC) is a browser extension that illustrates the physical and political realities of the internet's infrastructure using free software tools.

As one surfs the net, data packets are sent from the user's computer to the target server. These data packets go on a journey hopping from server to server, potentially crossing multiple countries, until the packets reach the desired website. In each of the countries that are passed different laws and practices can apply to the data, influencing whether or not authorities can inspect, store or modify that data.

In realtime BC lets you know which countries you surf through as you browse the web. Additionally BC will illustrate this process on a world map and (where available) provide you with contextualizing information on that country's laws and practices regarding your data.

BC runs on OSx and Unix systems.

Currently supporting the following browsers on OSX and Unix systems: Firefox, Chromium, Chrome, Safari

NOTE: Browser history has to be enabled.


### Installing BC:

BC v0.2 (2015) provides a "Wizard" installer that makes installing the required libraries and packages for BC easier. 

The wizard runs automatically the first time you run BC. It will check if your system has all the dependencies met for BC and if not the wizard will download and install them automagically. During the wizard BC will also install the required maps and databases.

Border Check has the following dependencies:

### Python:

* [pygeoip](https://pypi.python.org/pypi/pygeoip/0.2.7) 
* [lxml](https://pypi.python.org/pypi/lxml/3.2.3)
* [biplist](https://pypi.python.org/pypi/biplist/0.5) (if you plan to use Safari)

For **Debian**-based systems (ex: Ubuntu), first run:

`sudo apt-get install python-pip` to install [pip](https://pypi.python.org/pypi/pip/), python's super usefull package manager.

If you already have pip: `pip install lxml` and `pip install pygeoip`

On **OSX** it's recommended you install [Homebrew](http://brew.sh/) first and use that to get [python + pip](https://github.com/mxcl/homebrew/wiki/Homebrew-and-Python).


### LFT

BC uses [LFT v3.73 (08/2014)](http://pwhois.org/lft/) for tracerouting.

On **Debian** and **Ubuntu** it needs to be built from source and requires libpcap [`sudo apt-get install python-libpcap`]

To make this process more easy, BC (v0.2 2015) provides you a binary with the source. It is called `lft.linux` and is on folder `bin`.

On **OSX** you can use Homebrew: `brew install lft` which will automatically download and build the package.

#### Note on provided LFT binary

We do provide a static compiled binary of lft in the bin directory.

Please consider that this is for convenience only, you are invited to make your own.


### GeoIP databases and js libraries

BC will automatically unpack the newest geoip databases on the first run. 

Javascript mapping libraries are included in the package.


## Options and features:

See the included examples for usage.

```
bc [OPTIONS] 

  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d, --debug           debug mode
  -l LFT_PATH           path to lft (fetch from source or use provided binary)
  --xml=EXPORT_XML      export traces to xml (ex: --xml foo.xml)
  --load=IMPORT_XML     import traces (non root required) (ex: --load bar.xml)
  --bh=BROWSER_HISTORY  set browser's history path
  -b BROWSER            set browser type to be used: F = Firefox / C = Chrome / S = Safari / Ch = Chromium / N = None

```

#### Examples of usage:

Normal BC run:

`$ python bc`

Debug mode:

`$ python bc --debug`

Export 'tracing' results to xml:

`$ python bc --xml "mytravel.xml"`


#### More options (set browsers, paths, etc):

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

Import 'traces' from xml:

`$ python bc --load "mytravel.xml"`

Set lft path to be used by BC traces:

`$ python bc -l "/usr/bin/lft"`


### License

Border Check is free software, and may be redistributed under [GPL v3].


### Contribute: 

If you want to contribute to BC development, reporting a bug, providing a patch, commenting 
on the code base or simply need to find help to run it, please go to:

      irc.freenode.net / channel: #BorderCheck

If nobody gets back to you, then drop an e-mail.

To make donations use the following hashes:
  
      - Bitcoin: 1Q63KtiLGzXiYA8XkWFPnWo7nKPWFr3nrc
      - Ecoin: ETtSteMWxjY7RKWZGMNSkX7eC3BJ21VYXE


### Contact

Please report any problems you encounter using/installing Border Check to:

 - Roel Roscam Abbing (rscmbbng@riseup.net)
 - psy (epsylon@riseup.net)

