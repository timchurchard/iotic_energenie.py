#!/usr/bin/env python3

# Path/Filename of the pyenergenie/src/monitor.py output
EG_CSV_FN = 'energenie.csv'

# Time in seconds to poll the csv file.
# Note: Each new record will be published individually
EG_POLL = 5


import logging
logging.basicConfig(level=logging.WARNING)

import sys
import time

import csv
import json

import IoticAgent.IOT as IOT
# from IoticAgent import Datatypes as DT
# from IoticAgent import Units as UT


def egcsv_read(last_time=0):
    """Read the monitor.py output and return any new rows > last_time
    Rows are returns as list of dicts
    """
    ret = []
    reader = csv.reader(open(EG_CSV_FN))
    names = None
    for row in reader:
        if 'timestamp' in row[0]:
            names = row
        elif float(row[0]) > last_time:
            drow = {}
            for x in range(0, len(row)):
                if names[x] == 'timestamp' or names[x] == 'freq':
                    row[x] = float(row[x])
                elif row[x] == 'None':
                    row[x] = 0
                else:
                    row[x] = int(row[x])
                drow[names[x]] = row[x]
            ret.append(drow)
    return ret


def iot_setup(client):
    thing = client.create_thing('tims_energenie')
    #
    thing_meta = thing.get_meta()
    thing_meta.set_label("Tim's Energenie")
    thing_meta.set_description("Energenie monitor attached to home office power outlet (laptop, server, monitor, switch, UPS)")
    thing_meta.set_location(52.526787, 0.387971)  # My village, not house.
    thing_meta.set()
    #
    thing.create_tag(['energenie', 'power', 'monitor'])
    thing.set_public()
    #
    point = thing.create_feed('data')
    #
    point_meta = point.get_meta()
    point_meta.set_label("Data feed")
    point_meta.set_description("dict of 1 row from pyenergenie/monitor.py csv output")
    point_meta.set()
    #
    # TODO
    #point.value_create('time', DT.INTEGER, lang='en')
    #point.value_create('mfrid', DT.INTEGER, lang='en')
    #point.value_create('prodid', DT.INTEGER, lang='en')
    #point.value_create('sensorid', DT.INTEGER, lang='en')
    #point.value_create('flags', DT.INTEGER, lang='en')
    #point.value_create('switch', DT.INTEGER, lang='en')
    #point.value_create('voltage', DT.INTEGER, lang='en', unit=UT.VOLT)
    #point.value_create('freq', DT.INTEGER, lang='en')
    #point.value_create('reactive', DT.INTEGER, lang='en')
    #point.value_create('real', DT.INTEGER, lang='en', unit=UT.WATT)
    #
    return point


def main():

    with IOT.Client() as client:
        data_point = iot_setup(client)

        last_time = 0
        while True:
            try:
                print("Running, press ctrl+c to quit.")
                #
                new_data = egcsv_read(last_time)
                for row in new_data:
                    if row['timestamp'] > last_time:
                        last_time = row['timestamp']
                    #
                    data_point.share(row)
                    time.sleep(0.11)  # todo: ensure never exceed 10 msg/s
                    print("Shared: ", row)
                #
                time.sleep(EG_POLL)
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    main()
