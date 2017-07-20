#!/bin/bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export PORTAL_SSID=Opentrons_Robot

echo "[BOOT] Exported env variables"

echo "[BOOT] Starting status light daemon"
python /usr/src/api/scripts/compute/status_light.py &

while [ ! -f /tmp/resin/status_light ]; do sleep 1; done
echo "[BOOT] ipc pipe created - /tmp/resin/status_light"


echo "[BOOT] Starting access point daemon"
python /usr/src/api/scripts/compute/startAP.py &

echo "[BOOT] Starting server"
python /usr/src/api/scripts/compute/startServer.py

