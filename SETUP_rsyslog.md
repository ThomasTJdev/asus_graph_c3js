SETUP rsyslog
=============

Setup rsyslog on raspberry pi and forward router ASUS RT-N66U logs:
-------------------------------------------------------------------
sudo nano /etc/rsyslog.conf

Uncomment:
----------
$ModLoad imudp
$UDPServerRun 514

$ModLoad imtcp
$InputTCPServerRun 514

Touch file (actually not needed unless you going for a dry-run)
---------------------------------------------------------------
sudo touch /var/log/asuslog.log

Config rsyslog
--------------
sudo nano /etc/rsyslog.d/asus.conf

#Insert
$template NetworkLog, "/var/log/asuslog.log"
:fromhost-ip, isequal, "192.168.1.1" -?NetworkLog
& stop

Restart rsyslog
---------------
sudo service rsyslog restart


Rotate log
----------
sudo nano /etc/logrotate.d/asuslog

#Insert
/var/log/asuslog.log {
        rotate 5
        size 3000k
        notifempty
        compress
        postrotate
                invoke-rc.d rsyslog rotate > /dev/null
        endscript
}
#OR THIS
/var/log/asuslog.log {
    missingok
    notifempty
    compress
    size 20k
    daily
    create 0600 root root
}

