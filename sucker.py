
import logging
logger = logging.basicConfig(level=logging.WARNING)

import sqlite3

from sys import exit
from time import sleep
from threading import Lock
from functools import partial
from base64 import b64encode

from IoticAgent import IOT


DBFILE = "sucker.db"
PREFIX = "t_"


def data_to_create(tablename, data):
    ret = "CREATE TABLE " + tablename + " ("
    for key in data:
        if isinstance(data[key], str):
            ret += key + " TEXT, "
        elif isinstance(data[key], int):
            ret += key + " INTEGER, "
        elif isinstance(data[key], float):
            ret += key + " REAL, "
        #elif isinstance(data[key], bool):
        #    ret += key + " INTEGER, "
        elif isinstance(data[key], bytes):
            ret += key + " BLOB, "
        else:
            print("Error: unable to handle ", key, " with type ", type(data[key]))
            return None
    ret = ret[:-2]
    ret += ");"
    return ret


def data_to_insert(tablename, rec):
    for key in rec:
        if isinstance(rec[key], bytes):
            rec[key] = b64encode(rec[key]).decode('utf8')
    keys = ','.join(rec.keys())
    vals = tuple(rec.values())
    return 'INSERT INTO ' + tablename + ' (' + keys + ') VALUES ' + str(vals) + ';'


def table_exists(conn, tablename):
    ret = False
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';".format(tablename.replace('\'', '\'\'')))
    if cur.fetchone() is not None:
        ret = True
    cur.close()
    return ret


def data_cb(lock, data):
    if not (data['mime'] is None and isinstance(data['data'], dict)):
        print("Error: data must be automatically decoded to dict.  Give up.")
        return
    for key in data['data']:
        if isinstance(data['data'][key], bool):
            data['data'][key] = int(data['data'][key])
    with lock:
        tablename = PREFIX + data['pid']
        sdb = sqlite3.connect(DBFILE)
        if not table_exists(sdb, tablename):
            sql = data_to_create(tablename, data['data'])
            print(sql)
            cur = sdb.cursor()
            cur.execute(sql)
            cur.close()
        sql = data_to_insert(tablename, data['data'])
        print(sql)
        cur = sdb.cursor()
        cur.execute(sql)
        cur.close()
        sdb.commit()
        sdb.close()


if __name__ == '__main__':
    #
    data_lock = Lock()
    #
    client = None
    try:
        client = IOT.Client()
        client.register_catchall_feeddata(partial(data_cb, data_lock))
        client.register_catchall_controlreq(partial(data_cb, data_lock))
        client.start()
    except Exception as exc:
        print("Failed to start.  Give up.")
        print(exc)
        exit(1)
    while True:
        try:
            print("Main loop is running.  Press ctrl+c to quit.")
            sleep(60)
        except KeyboardInterrupt:
            break
    client.stop()

