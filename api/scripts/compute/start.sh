#!/bin/bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export PORTAL_SSID=Opentrons_Robot


echo "[BOOT] Exported env variables"

python /usr/src/api/scripts/compute/status_light.py &
python /usr/src/api/scripts/compute/startAP.py &
python /usr/src/api/scripts/compute/startServer.py

