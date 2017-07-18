#!/bin/bash

echo "starting start scripts"

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
export PORTAL_SSID=Opentrons_Robot


echo "Exported env variables"

/usr/bin/python /usr/src/api/scripts/startAP.py &
/usr/bin/python /usr/src/api/scripts/startServer.py &
echo "AFTER PYTHON"

return 0
