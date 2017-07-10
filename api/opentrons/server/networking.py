# Server which handles all networking and connectivity aspects of the robot
# Opentrons
import subprocess


INTERFACE = 'wlan0'  # 'wlp7s0'
WPA_CONF = '/etc/wpa_supplicant/wpa_supplicant.conf'
DEFAULT_HEADER = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\n\n"


def activate():
    # TODO: don't use a hardcorded interface
    down_proc = subprocess.call('/sbin/ifdown wlan0', shell=True)
    up_proc = subprocess.call('/sbin/ifup wlan0', shell=True)


def save_network(ssid, passkey, network_type):
    """
    TODO: Handle other network types (open, WPA2)
    Writes a new /etc/wpa_supplicant/wpa_supplicant.conf file with a network config

        network={
                ssid="NETWORK_SSID"
                psk="PASWORD_UNENCRYPTED"
        }
    """
    if network_type is 'wpa':
        config = '\nnetwork={{\n\tssid="{}"\n\tpsk="{}"\n}}'.format(ssid,
                                                                    passkey)
    with open(WPA_CONF, 'w') as wpa_file:
        file_contents = DEFAULT_HEADER + config
        wpa_file.write(file_contents)


def is_wireless_connection():
    if not subprocess.call('ip -4 addr show wlan0 | grep -oP "(?<=inet ).*(?=/)"', shell=True):
        return True
    return False
