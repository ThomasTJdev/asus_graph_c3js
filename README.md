Convert logs to C3js format
===========================

These scripts are formatting logs to C3js format. The purpose is to visualize the logs online in charts.

License
-------

ThomasTJ - MIT

Requirements
------------

* MaxMind GeoIP (pip/yaourt)
* GeoLiteCity.dat (see below for details)
* RainbowLoggingHandler (pip/yaourt)
* APScheduler (pip/yaourt)

* Setup rsyslog. Description in the file "SETUP_rsyslog.md"

parse_asus_syslog_to_sqlite
----------------------------

This script takes the raw Asus RTN66u syslog and parses it to a sqlite3 database.

Go to your RTN66u settings and activated syslog forward. Setup syslog on your pc (tested on RPi v3).

Change location in script to logfile or move logfile to folder **logs**. (There is a test-logfile in **logs**)

Run script:
**python parse_asus_to_sqlite.py**

This will create a database (db) in the folder **data** and create 2 tables. 1 for connections and 1 for DHCP information.

The logfile is parsed line by line, and checking the date against latest date in db. This solution is instead of tailing the logfile. Please go through the and check if the suggested ports suits you. In the script, theres is included sample ports to ignore - e.g. 1194 is totally ignore.

The data is found by regex and connections from other IP's (inbound) are runned through geoip to get location. You'll need GeoIP (yaourt -S GeoIP) and MaxMinds GeoIP city 
database. Download the GeoIP database and place it here: /usr/local/share/GeoIP/GeoLiteCity.dat.
* wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
* gunzip GeoLiteCity.dat.gz
* mv GeoLiteCity.dat /usr/local/share/GeoIP/GeoLiteCity.dat

For logging add 'import logging' and uncomment lines.

parse_asus_sqlite_to_C3js
--------------------

This script parses the sqlite data to C3js format.

Please note that due testing some returns are in list format, so these needs to be formattet where you use them. At the moment this is done in the app.py.

Configure your ports in function: def accept_closed()

app.py
------

Run flask - access on 0.0.0.0:5002/charts.

Using
-----

Start the webserver:
python app.py

Start the cron for checking logs:
python parse_asus_syslog_to_sqlite.py

