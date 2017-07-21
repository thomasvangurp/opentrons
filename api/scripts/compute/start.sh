#!/bin/bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export PORTAL_SSID=Opentrons_Robot

echo "[BOOT] Exported env variables"

echo "[BOOT] Starting status light daemon"
python /usr/src/api/scripts/compute/status_light.py &



echo "[BOOT] Starting access point daemon"
python /usr/src/api/scripts/compute/start_access_point.py &

echo "[BOOT] Starting server"
python /usr/src/api/scripts/compute/start_server.py

