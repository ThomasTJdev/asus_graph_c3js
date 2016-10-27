import logging
import sys

from flask import Flask, render_template, request
from rainbow_logging_handler import RainbowLoggingHandler

import parser_asus_sqlite_to_C3js as psC3js


#################################################
## Logger - Start
#################################################

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

#################################################
## Logger - End
#################################################



app = Flask(__name__)

@app.route('/charts')
@app.route('/charts/<vDateReq>')
def charts(vDateReq=None):

    data = psC3js.port_count(vDateReq)
    port_count_accept = psC3js.port_count_accept(vDateReq)
    port_count_drop = psC3js.port_count_drop(vDateReq)

    date_count = psC3js.date_count(vDateReq)
    #date_count = psC3js.date_count_7d()
    status_count = psC3js.status_count()

    country_count = psC3js.country_count()
    cc_list = ''
    for row in country_count:
        cc_list = cc_list + '<tr>'
        for cell in row:
            cc_list = cc_list + '<td>' + str(cell) + '</td>'
        cc_list = cc_list + '</tr>'
    cc_list = '<table class="table table-inverse system_information"><thead><tr><th>Country</th><th>Connections</th></tr></thead><tbody>' + cc_list + '</tbody></table>'

    accept_closed = psC3js.accept_closed()
    if accept_closed:
        ac_list = ''
        for row in accept_closed:
            ac_list = ac_list + '<tr>'
            for cell in row:
                ac_list = ac_list + '<td>' + str(cell) + '</td>'
            ac_list = ac_list + '</tr>'
        ac_list = '<table class="table table-inverse system_information"><thead><tr><th>Date</th><th>Status</th><th>IP</th><th>Port</th><th>Country</th><th>City</th></tr></thead><tbody>' + ac_list + '</tbody></table>'
    else:
        ac_list = 'No accepted connections on closed ports.'

    conn_last = psC3js.conn_last()
    if conn_last:
        co_list = ''
        for row in conn_last:
            co_list = co_list + '<tr>'
            for cell in row:
                co_list = co_list + '<td>' + str(cell) + '</td>'
            co_list = co_list + '</tr>'
        co_list = '<table class="table table-inverse system_information"><thead><tr><th>Date</th><th>Status</th><th>IP</th><th>Port</th><th>Country</th><th>City</th></tr></thead><tbody>' + co_list + '</tbody></table>'
    else:
        co_list = 'No accepted connections on closed ports.'

    internal_ip = psC3js.internal_ip()
    if internal_ip:
        ii_list = ''
        for row in internal_ip:
            ii_list = ii_list + '<tr>'
            for cell in row:
                ii_list = ii_list + '<td>' + str(cell) + '</td>'
            ii_list = ii_list + '</tr>'
        ii_list = '<table class="table table-inverse system_information"><thead><tr><th>Date</th><th>Status</th><th>IP</th><th>Port</th></tr></thead><tbody>' + ii_list + '</tbody></table>'
    else:
        ii_list = 'No internal IP data'

    count_conn_time = psC3js.count_conn_time()
    if count_conn_time:
        cct_list = ''
        for row in count_conn_time:
            cct_list = cct_list + '<tr>'
            for cell in row:
                cct_list = cct_list + '<td>' + str(cell) + '</td>'
            cct_list = cct_list + '</tr>'
        cct_list = '<table class="table system_information"><thead><tr><th>Time</th><th>Count</th></tr></thead><tbody>' + cct_list + '</tbody></table>'
    else:
        cct_list = 'No internal IP data'


    dhcp_data = psC3js.dhcp_data()
    if dhcp_data:
        dhcp_list = ''
        for row in dhcp_data:
            dhcp_list = dhcp_list + '<tr>'
            for cell in row:
                dhcp_list = dhcp_list + '<td>' + str(cell) + '</td>'
            dhcp_list = dhcp_list + '</tr>'
        dhcp_list = '<table class="table table-inverse system_information"><thead><tr><th>Time</th><th>Count</th></tr></thead><tbody>' + dhcp_list + '</tbody></table>'
    else:
        dhcp_list = 'No internal IP data'


    heatmap_data = psC3js.latlng_count(vDateReq)
    heatmap_data_drop = psC3js.latlng_count_drop()
    heatmap_data_accept = psC3js.latlng_count_accept()

    #date_count2 = psC3js.date_count2() # WAY TO SLOW


    return render_template('charts.html', port_count=data, port_count_accept=port_count_accept, port_count_drop=port_count_drop, date_count=date_count, status_count=status_count, country_count=cc_list, accept_closed=ac_list, conn_last=co_list, internal_ip=ii_list, count_conn_time=cct_list, heatmap_data=heatmap_data, dhcp_list=dhcp_list)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
