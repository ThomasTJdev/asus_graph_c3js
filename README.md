Convert logs to C3js format
===========================

Formatting ASUS router logs to C3js format. The purpose is to visualize the logs online in charts. The base code is defined for ASUS RTN66u.

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

parse_asus_syslog_to_sqlite.py
------------------------------

This script takes the raw ASUS syslog and parses it to a sqlite3 database.

Go to your routers settings and activate syslog forwarding. Setup syslog on your pc (tested on pc and RPi v3).

Change the location in the file to the logfile or move the logfile to the folder **logs**. (There is a test-logfile in **logs**)

Run the script:
**python parse_asus_to_sqlite.py**

This will create a database (db) in the folder **data** and create 2 tables. 1 for connections and 1 for DHCP information.

The logfile is parsed line by line and the lines date is checked against the latest date in the db. This solution is instead of tailing the logfile. Please go through the file and check if the suggested ports suits you. In the script, there's included some sample ports to ignore - e.g. 1194 is totally ignored.

The data is found by regex and inbound connections (from other IP's) are runned through geoip to get their locations. You'll need GeoIP (yaourt -S GeoIP) and MaxMinds GeoIP city database. Download the GeoIP database and place it here: /usr/local/share/GeoIP/GeoLiteCity.dat
* wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
* gunzip GeoLiteCity.dat.gz
* mv GeoLiteCity.dat /usr/local/share/GeoIP/GeoLiteCity.dat

For logging add 'import logging' and uncomment lines.

parse_asus_sqlite_to_C3js.py
----------------------------

This script parses the sqlite data to C3js format.

Please note that due to testing, some of date are returned in list format, so these needs to be formattet where you use them. At the moment the formatting is done in the app.py.

Configure your ports in the functions.

app.py
------

This is the script for running the flask webserver.

Using
-----

Start the webserver:
python app.py

Access the webserver:
0.0.0.0:5002/charts

Start the cron for checking logs:
python parse_asus_syslog_to_sqlite.py

