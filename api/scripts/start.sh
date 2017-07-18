#!/bin/bash

echo "starting start scripts"

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export PORTAL_SSID=Opentrons_Robot


echo "Exported env variables"

CHECK=python -c /usr/src/api/scripts/startAP.py &
echo $CHECK
CHECK_2=python -c /usr/src/api/scripts/startServer.py &
echo $CHECK_2
echo "AFTER PYTHON"

return 0
