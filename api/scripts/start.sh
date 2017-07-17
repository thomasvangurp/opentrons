#!/bin/bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export PORTAL_SSID=Opentrons_Robot

python /usr/src/api/scripts/startAP.py &
python /usr/src/api/scripts/startServer.py &