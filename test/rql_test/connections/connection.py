###
# Tests the driver API for making connections and excercizes the networking code
###

from sys import argv
from subprocess import Popen
from time import sleep
from sys import path
path.append('.')
from test_util import RethinkDBTestServers
path.append("../../drivers/python")

import rethinkdb as r

server_build = argv[1]
use_default_port = bool(argv[2])

print "Running py connection tests"

# No servers started yet so this should fail
try:
    conn = r.connect()
    raise Exception("No connect error")
except r.RqlDriverError as err:
    if not str(err) == "Could not connect to localhost:28015.":
        raise Exception("Connect err is wrong")

try:
    conn = r.connect(port=11221)
    raise Exception("No connect error")
except r.RqlDriverError as err:
    if not str(err) == "Could not connect to localhost:11221.":
        print str(err)
        raise Exception("Connect err is wrong")

try:
    conn = r.connect(host="0.0.0.0")
    raise Exception("No connect error")
except r.RqlDriverError as err:
    if not str(err) == "Could not connect to 0.0.0.0:28015.":
        raise Exception("Connect err is wrong")

try:
    conn = r.connect(host="0.0.0.0", port=11221)
    raise Exception("No connect error")
except r.RqlDriverError as err:
    if not str(err) == "Could not connect to 0.0.0.0:11221.":
        raise Exception("Connect err is wrong")

# Now run with an actual server running
if use_default_port:
    with RethinkDBTestServers(server_build=server_build, use_default_port=use_default_port):
        try:
            conn = r.connect()
            conn.reconnect()
            conn = r.connect(host='localhost')
            conn.reconnect()
            conn = r.connect(host='localhost', port=28015)
            conn.reconnect()
            conn = r.connect(port=28015)
            conn.reconnect()
        except r.RqlDriverError as err:
            raise Exception("Should have connected to default CPP server")

with RethinkDBTestServers(server_build=server_build) as servers:
    port = servers.cpp_port

    try:
        c = r.connect(port=port)
        r.expr(1).run(c)
        c.close()
        c.close()
        c.reconnect()
        r.expr(1).run(c)
    except r.RqlDriverError as err:
        raise Exception("Should not have thrown")

    try:
        c = r.connect(port=port)
        r.expr(1).run(c)
        c.close()
        r.expr(1).run(c)
        raise Exception("Should have thrown")
    except r.RqlDriverError as err:
        if not str(err) == "Connection is closed.":
            raise Exception("Error message wrong")

    try:
        c = r.connect(port=port)
        r.expr(1).run(c)

        servers.stop()
        sleep(0.1)

        r.expr(1).run(c)
        raise Exception("Should have thrown")
    except r.RqlDriverError as err:
        if not str(err) == "Connection is closed.":
            raise Exception("Error message wrong")

# TODO: test cursors, streaming large values
