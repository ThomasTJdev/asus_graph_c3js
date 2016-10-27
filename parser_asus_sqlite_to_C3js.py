#!/usr/bin/python python3
import sqlite3
import datetime
import logging
import sys
import re

from rainbow_logging_handler import RainbowLoggingHandler


#==================================
## Settings - start
#==================================

# Change to your location
db_location = 'data/log_syslog.db'

# Standard timeperiode for data
def getTimeperiode(vDateReq):
    vDate = vDateReq
    if vDate: 
        m = re.match(r"([0-9]+)([a-zA-Z]+)",vDate)
        if not m.group(2):
            stdDate = '0'
        elif m.group(2) == 'seconds':
            dd = datetime.datetime.now() - datetime.timedelta(seconds=int(m.group(1)))
            stdDate = dd.strftime("%Y-%m-%d %H:%M:%S")
        elif m.group(2) == 'minutes':
            dd = datetime.datetime.now() - datetime.timedelta(minutes=int(m.group(1)))
            stdDate = dd.strftime("%Y-%m-%d %H:%M:%S")
        elif m.group(2) == 'hours':
            dd = datetime.datetime.now() - datetime.timedelta(hours=int(m.group(1)))
            stdDate = dd.strftime("%Y-%m-%d %H:%M:%S")
        elif m.group(2) == 'days':
            dd = datetime.datetime.now() - datetime.timedelta(days=int(m.group(1)))
            stdDate = dd.strftime("%Y-%m-%d %H:%M:%S")
        elif m.group(2) == 'months':
            dd = datetime.datetime.now() - datetime.timedelta(months=int(m.group(1)))
            stdDate = dd.strftime("%Y-%m-%d %H:%M:%S")
        elif m.group(2) == 'years':
            dd = datetime.datetime.now() - datetime.timedelta(years=int(m.group(1)))
            stdDate = dd.strftime("%Y-%m-%d %H:%M:%S")
        else:
            stdDate = '0'
    else:
        stdDate = '0'

    return stdDate

#==================================
## Settings - end
#==================================


#==================================
## Logger - Start
#==================================

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
#logger.addHandler(ch)

#==================================
## Logger - end
#==================================



#==================================
## Parsing functions - start
#==================================

def port_count(vDateReq):
    # Count of ports
    conn = conn_sqlite3()
    stdDate = getTimeperiode(vDateReq)
    cursor = conn.execute("SELECT port, count(port) FROM asus_syslog_conn WHERE date > ? AND port <> '' GROUP BY port LIMIT 20", (stdDate, ))
    port_count = ''
    for row in cursor:
        port_count = (port_count + '[\'' + str(row[0]) + '\', ' + str(row[1]) + '],')
    close_sqlite3(conn)
    port_count = port_count[:-1]

    return port_count

def port_count_accept(vDateReq):
    # Count of ports
    conn = conn_sqlite3()
    stdDate = getTimeperiode(vDateReq)
    cursor = conn.execute("SELECT port, count(port) FROM asus_syslog_conn WHERE date > ? AND port <> '' AND status = 'ACCEPT' GROUP BY port LIMIT 20", (stdDate, ))
    port_count = ''
    for row in cursor:
        port_count = (port_count + '[\'' + str(row[0]) + '\', ' + str(row[1]) + '],')
    close_sqlite3(conn)
    port_count = port_count[:-1]

    return port_count

def port_count_drop(vDateReq):
    # Count of ports
    conn = conn_sqlite3()
    stdDate = getTimeperiode(vDateReq)
    cursor = conn.execute("SELECT port, count(port) FROM asus_syslog_conn WHERE date > ? AND port <> '' AND status = 'DROP' GROUP BY port LIMIT 20", (stdDate, ))
    port_count = ''
    for row in cursor:
        port_count = (port_count + '[\'' + str(row[0]) + '\', ' + str(row[1]) + '],')
    close_sqlite3(conn)
    port_count = port_count[:-1]

    return port_count

def date_count(vDateReq):
    # Connection count per timestamp
    conn = conn_sqlite3()
    stdDate = getTimeperiode(vDateReq)
    cursor = conn.execute("SELECT date, count(date) FROM asus_syslog_conn WHERE date >= ? GROUP BY strftime('%Y-%m-%d %H:%M', date) ORDER BY date", (stdDate, ))
    date_count = '["Connections"'
    date_count_x = '["x"'
    for row in cursor:
        date_count = (date_count + ', ' + str(row[1]))
        date_count_x = (date_count_x + ', \'' + str(row[0]) + '\'')
    close_sqlite3(conn)
    date_count = date_count + ']'
    date_count_x = date_count_x + ']'

    final = date_count_x + ',' + date_count

    return final

def date_count_7d():
    # Connection count per timestamp
    conn = conn_sqlite3()
    dd = datetime.datetime.now() - datetime.timedelta(days=7)
    week_ago = dd.strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute("SELECT date, count(date) FROM asus_syslog_conn WHERE date > ? GROUP BY strftime('%Y-%m-%d %H:%M', date) ORDER BY date", (week_ago, ))
    date_count = '["Connections"'
    date_count_x = '["x"'
    for row in cursor:
        date_count = (date_count + ', ' + str(row[1]))
        date_count_x = (date_count_x + ', \'' + str(row[0]) + '\'')
    close_sqlite3(conn)
    date_count = date_count + ']'
    date_count_x = date_count_x + ']'

    final = date_count_x + ',' + date_count

    return final

def date_count2():
    # Connection count per timestamp // WAY TO SLOW!!
    conn = conn_sqlite3()

    c = conn.cursor()
    c.execute("select date, port from asus_syslog_conn where port <> '' AND port != '1194'")
    #c.execute("select date, port from asus_syslog_conn where port <> ''")
    #c.execute("select date, port from asus_syslog_conn where date > '2016-08-21 10:55:00'")
    kl = c.fetchall()

    a = conn.cursor()
    #a.execute("SELECT DISTINCT port FROM asus_syslog_conn WHERE port = '80' OR port = '1194'")
    a.execute("SELECT DISTINCT port FROM asus_syslog_conn WHERE port <> '' AND port != '1194'")
    al = a.fetchall()

    date_count = ''
    date_x = '[\'x\', '

    for x in kl:
        date_x = date_x + '\'' + x[0] + '\', '
    date_x = date_x[:-2]
    date_x = date_x + '], '

    for c in al:
        date_count = date_count + '[\'' + str(c[0]) + '\', '
        for k in kl:
            if c[0] == k[1]:
                date_count = date_count + "1, "
            else:
                date_count = date_count + "0, "

        date_count = date_count[:-2]
        date_count = date_count + '], '

    date_count = date_count[:-2]

    close_sqlite3(conn)

    final = date_x + date_count

    return final

def status_count():
    # Count of status
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT status, count(status) FROM asus_syslog_conn group by status")
    status_count = ''
    for row in cursor:
        status_count = (status_count + '["' + str(row[0]) + '", ' + str(row[1]) + '],')
    close_sqlite3(conn)
    status_count = status_count[:-1]

    return status_count

def latlng_count(vDateReq):
    # Count of latlng
    conn = conn_sqlite3()
    stdDate = getTimeperiode(vDateReq)
    cursor = conn.execute("SELECT latitude, longitude, count(latitude) FROM asus_syslog_conn WHERE date > ? AND latitude <> '' GROUP BY latitude", (stdDate, ))
    latlng_count = ''
    for row in cursor:
        latlng_count = (latlng_count + '{location: new google.maps.LatLng(' + str(row[0]) + ', ' + str(row[1]) + '), weight: ' + str(row[2]) + '},')
    close_sqlite3(conn)

    latlng_count = latlng_count[:-1]

    return latlng_count

def latlng_count_drop():
    # Count of latlng - status = DROP
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT latitude, longitude, count(latitude) FROM asus_syslog_conn WHERE status = 'DROP' AND latitude <> '' GROUP BY latitude")
    latlng_count_drop = ''
    for row in cursor:
        latlng_count_drop = (latlng_count_drop + '{location: new google.maps.LatLng(' + str(row[0]) + ', ' + str(row[1]) + '), weight: ' + str(row[2]) + '},')
    close_sqlite3(conn)
    latlng_count_drop = latlng_count_drop[:-1]

    return latlng_count_drop

def latlng_count_accept():
    # Count of latlng - status = ACCEPT
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT latitude, longitude, count(latitude) FROM asus_syslog_conn WHERE status = 'ACCEPT' AND latitude <> '' GROUP BY latitude")
    latlng_count_accept = ''
    for row in cursor:
        latlng_count_accept = (latlng_count_accept + '{location: new google.maps.LatLng(' + str(row[0]) + ', ' + str(row[1]) + '), weight: ' + str(row[2]) + '},')
    close_sqlite3(conn)
    latlng_count_accept = latlng_count_accept[:-1]

    return latlng_count_accept

def country_count():
    # Count of SRC countrys top 15
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT country, count(country) FROM asus_syslog_conn WHERE country <> '' GROUP BY country ORDER BY count(country) DESC LIMIT '20'")
    cl = []
    for row in cursor:
        cl.append([row[0], row[1]])

    close_sqlite3(conn)

    return cl


def conn_last():
    # Accepted on closed portsT
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT  date, status, ipaddress, port, country, city FROM asus_syslog_conn WHERE status = 'ACCEPT' ORDER BY date DESC LIMIT 20")

    conn_last = []
    for row in cursor:
        # Return format: [[value1, value2, value3, value4, value5], [value1, etc.]]
        conn_last.append([row[0], row[1], row[2], row[3], row[4], row[5]])

    close_sqlite3(conn)

    return conn_last


def accept_closed():
    # Accepted on closed portsT
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT  date, status, ipaddress, port, country, city FROM asus_syslog_conn WHERE status = 'ACCEPT' AND port != '80' AND port != '8080' AND port != '1194' AND port != '1196' AND port != '9091' AND port != '32400' ORDER BY date DESC LIMIT 20")

    accept_closed = []
    for row in cursor:
        # Return format: [[value1, value2, value3, value4, value5], [value1, etc.]]
        accept_closed.append([row[0], row[1], row[2], row[3], row[4], row[5]])

    close_sqlite3(conn)

    return accept_closed


def count_conn_time():
    # Accepted on closed portsT
    conn = conn_sqlite3()

    conn_time = []

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-10 minute');")
    for row in cursor:
        conn_time.append(['10 minutes', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-1 hour');")
    for row in cursor:
        conn_time.append(['60 minutes', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-6 hour');")
    for row in cursor:
        conn_time.append(['6 hours', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-12 hour');")
    for row in cursor:
        conn_time.append(['12 hours', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-1 day');")
    for row in cursor:
        conn_time.append(['1 day', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-3 day');")
    for row in cursor:
        conn_time.append(['3 days', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-7 day');")
    for row in cursor:
        conn_time.append(['7 days', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-30 day');")
    for row in cursor:
        conn_time.append(['30 days', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-180 day');")
    for row in cursor:
        conn_time.append(['180 days', row[0]])

    cursor = conn.execute("SELECT COUNT(*) FROM asus_syslog_conn WHERE date >= datetime('now','-360 day');")
    for row in cursor:
        conn_time.append(['360 days', row[0]])


    close_sqlite3(conn)

    # Return format: [[value1, value2, value3, value4, value5], [value1, etc.]]
    return conn_time



def internal_ip():
    # Internal connections
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT  date, status, ipaddress, port FROM asus_syslog_conn WHERE latitude = '' ORDER BY date DESC LIMIT 20")

    internal_ip = []
    for row in cursor:
        # Return format: [[value1, value2, value3, value4], [value1, etc.]]
        internal_ip.append([row[0], row[1], row[2], row[3]])

    """ Below will return in pre-formatted table HTML
    internal_ip = ''
    for row in cursor:
        internal_ip = (
            internal_ip + 
            '<tr>' + 
            '<td>' +
            str(row[0]) +
            '</td>' +
            '<td>' +
            str(row[1]) + 
            '</td>' +
            '<td>' + 
            str(row[2]) + 
            '</td>' +
            '<td>' + 
            str(row[3]) + 
            '</td>' +
            '</tr>')
    """

    close_sqlite3(conn)

    return internal_ip


def dhcp_data():
    # Accepted on closed portsT
    conn = conn_sqlite3()
    cursor = conn.execute("SELECT * FROM asus_syslog_dhcp ORDER BY date DESC LIMIT 20")

    dhcp = []
    for row in cursor:
        # Return format: [[value1, value2, value3, value4, value5], [value1, etc.]]
        dhcp.append([row[1], row[2], row[3], row[4]])

    close_sqlite3(conn)

    return dhcp


#==================================
## Parsing functions - end
#==================================


#==================================
## Database functions - start
#==================================

def conn_sqlite3():
    # Connect to sqlite3
    try:
        return sqlite3.connect(db_location)
        logger.info("Database opened succesfully")
    except Error as e:
        #print(e)
        logger.error("Connection to db failed. Error: " + str(e))


def close_sqlite3(conn):
    conn.close()

#==================================
## Database functions - end
#==================================



def main():


    # Test print
    #print (port_count())
    #print (date_count())
    #print (status_count())
    #print (latlng_count())
    #print (latlng_count_drop())
    #print (latlng_count_accept())
    #print (accept_closed())
    #print (internal_ip())
    #print (date_count_7d())
    #print (date_count2()) # Way to slow - do not use!
    #print (count_conn_time())
    #print (dhcp_data())
    pass


#main()

