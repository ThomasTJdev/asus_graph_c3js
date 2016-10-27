#!/usr/bin/python python3
import time
import re
import GeoIP
import logging
import sqlite3
import sys

from apscheduler.schedulers.blocking import BlockingScheduler # Requires: yaourt -S python-pytz python-tzlocal
from datetime import datetime
from rainbow_logging_handler import RainbowLoggingHandler


#=======================================#
#              Settings                 #
#=======================================#

vGeoIPlocation = "/usr/local/share/GeoIP/GeoLiteCity.dat"
# Want some test data? Change vFile to 'logs/asusrtn66u.log
vFile = "/var/log/asusrtn66u.log"

#=======================================#
#           Settings - end              #
#=======================================#



#=======================================#
#            Logger - Start             #
#=======================================#

# Create logger
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)

# Create file handler
#fh = logging.FileHandler("flask-rpi-smarthouse.log")
#fh.setLevel(logging.DEBUG)

# Create console handler
ch = RainbowLoggingHandler(
    sys.stderr,
    # Customizing each column's color
    color_asctime=('magenta' , None, False), color_levelname=('yellow', None, False),
    color_funcName=('cyan' , None, False), color_module=('green' , None, False),
    )
ch.setLevel(logging.DEBUG)

# Create formatter and at it to the handlers
# Formatter for fh
#formatter_fh = logging.Formatter('{"time": %(asctime)s, "levelname": %(levelname)s, "module": %(module)s, "funcName": %(funcName)s, "message": %(message)s}', datefmt="%Y-%m-%d %H:%M:%S")
#fh.setFormatter(formatter_fh)

# Formatter for ch
formatter_ch = logging.Formatter('%(asctime)s [%(levelname)s] [%(module)s] %(funcName)s : %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter_ch)

# Add the handlers to the logger
#logger.addHandler(fh)
logger.addHandler(ch)

#=======================================#
#             Logger - End              #
#=======================================#



def parse_syslog(conn, vFile):

    # Speed - 11.680 lines
    # real   0m8.734s
    # user   0m6.390s
    # sys    0m0.110s

    # Speed - 81.973 lines
    # real    0m47.838s
    # user    0m45.500s
    # sys     0m0.220s




    # Check if table exist or create
    # Table: asus_syslog_conn
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS asus_syslog_conn
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,            
            status TEXT NOT NULL,
            ipaddress TEXT NOT NULL,
            port INTEGER,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL);''')

    except Error as e:
        #print(e)
        logger.error("Table create fail - asus_syslog_conn. Error msg: " + str(e))

    # Table: asus_syslog_dhcp
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS asus_syslog_dhcp
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,            
            message TEXT NOT NULL,
            ipaddress TEXT,
            mac TEXT);''')

    except Error as e:
        #print(e)
        logger.error("Table create/check failed - asus_syslog_dhcp. Error msg: " + str(e))


    # Get latest inserted row instead of tailing file
    # Solution due to log rotation
    # You'll might get duplicates if table dhcp has newer data - do 2 select and choose highest?
    # There might be a better solution
    cursor = conn.execute("SELECT date FROM asus_syslog_conn ORDER BY date DESC LIMIT 1")
    last_date = ''
    for row in cursor:
        last_date = str(row[0])

    if not last_date:
        last_date = '1970-01-01 00:00:00'
        last_date = time.strptime(last_date, "%Y-%m-%d %H:%M:%S")
    else:
        last_date = time.strptime(last_date, "%Y-%m-%d %H:%M:%S")


    # Open GEO database
    geo = GeoIP.open(vGeoIPlocation, GeoIP.GEOIP_MEMORY_CACHE | GeoIP.GEOIP_CHECK_CACHE)
    #geo = GeoIP.open("/usr/local/share/GeoIP/GeoLiteCity.dat",GeoIP.GEOIP_MEMORY_CACHE | GeoIP.GEOIP_CHECK_CACHE)
    vGeoIP = ""
    tl = [] # Connections list
    dl = [] # DHCP list

    tl_count = 0 # Counter
    dl_count = 0 # Counter

    # Parse logfile
    with open(vFile) as f:
        currentYear = datetime.now().year
        for line in f:

            # Get date first due to use in 'if' for checking new data
            #mDate = re.search('(\A.{2,3}\s\d{2,3})(?<=: )\S+', line)
            mDatetime = re.search('(\A.{2,3}\s{1,2}\d{1,3}\s\d{2,3}:\d{2,3}:\d{2,3})', line)
            if not mDatetime.group(0):
                logger.info('No datetime for line' + line)
                continue    

            date_object = datetime.strptime('2016 ' + mDatetime.group(0), '%Y %b %d %H:%M:%S')
            current_line_date = time.strptime(str(date_object), "%Y-%m-%d %H:%M:%S")

            # If data is new
            # You'll might miss one ot two due to multiple connections on same second. Needs to be optimized.
            if current_line_date > last_date:

                # ===========================================
                #             Parse connections
                # ==========================================

                # !!! Missing DST ip

                # Check if line contains src ip
                mSRC = re.search('(?<=SRC=)\S+', line)
                if mSRC:

                    mDPT = re.search('(?<=DPT=)\S+', line)
                    # Avoid date from torrent port - bloating the log
                    if mDPT != '1194':
                        mSTATUS = re.search('(?<=:\s)\S+', line)

                        if not mSTATUS:
                            mSTATUS = ''
                        else:
                            mSTATUS = mSTATUS.group(0)

                        if not mSRC:
                            mSRC = ''
                        else:
                            record = geo.record_by_addr(mSRC.group(0))
                        mSRC = mSRC.group(0)

                        if not mDPT:
                            mDPT = ''
                        else:
                            mDPT = mDPT.group(0)

                        if record is None:
                            latitude = ""
                            longitude = ""
                            country_name = ""
                            city = ""
                        else:
                            latitude = str(record['latitude'])
                            longitude = str(record['longitude'])
                            country_name = str(record['country_name'])
                            city = str(record['city'])

                        tl_count += 1

                        # Append to list
                        tl.append([str(date_object), mSTATUS, mSRC, mDPT, country_name, city, latitude, longitude])


                # ===========================================
                #             Parse dhcp messages
                # ==========================================

                mDHCP = re.search('dhcp', line)
                if mDHCP:
                    mDHCPmac = re.search('([0-9a-fA-F]:?){12}', line)
                    if mDHCPmac:
                        mDHCPmessage = re.search('(?<=]: )\S+\w[^\(br0\)]', line)
                        mDHCPip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                        mDHCPmac = re.search('([0-9a-fA-F]:?){12}\s\w{1,30}', line)

                        if not mDHCPmac:
                            mDHCPmac = re.search('([0-9a-fA-F]:?){12}', line)
                        if not mDHCPmac:
                            mDHCPmac = ''
                        else:
                            mDHCPmac = mDHCPmac.group(0)

                        if not mDHCPmessage:
                            mDHCPmessage = ''
                        else:
                            mDHCPmessage = mDHCPmessage.group(0)

                        if not mDHCPip:
                            mDHCPip = ''
                        else:
                            mDHCPip = mDHCPip.group(0)

                        dl_count += 1

                        # Append to list
                        dl.append([str(date_object), mDHCPmessage, mDHCPip, mDHCPmac])

        # Insert data in db
        try:
            c.executemany("INSERT INTO asus_syslog_conn (date, status, ipaddress, port, country, city, latitude, longitude) VALUES (?,?,?,?,?,?,?,?)", tl)
            conn.commit()
            #print ("Insert OK - asus_syslog_conn. Inserted: " + str(tl_count))
            logger.info("Insert OK - asus_syslog_conn. Inserted: " + str(tl_count))
        except:
            logger.error("Insert failed - asus_syslog_conn")
            #pass

        try:
            c.executemany("INSERT INTO asus_syslog_dhcp (date, message, ipaddress, mac) VALUES (?,?,?,?)", dl)
            conn.commit()
            #print ("Insert OK - asus_syslog_dhcp. Inserted: " + str(tl_count))
            logger.info("Insert OK - asus_syslog_dhcp. Inserted: " + str(dl_count))
        except:
            logger.error("Insert failed - asus_syslog_dhcp")
            #pass




def parse_it():
    # Connect to sqlite3
    try:
        conn=sqlite3.connect('data/log_syslog.db')
        logger.info("Database opened succesfully")
    except Error as e:
        #print(e)
        logger.error("Database couldn't open. Error msg: " + str(e))

    parse_syslog(conn, vFile)


    # Close db
    conn.close()
    logger.info("Database closed")

def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(parse_it, 'cron', minute=5)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    
main()
#parse_it()

