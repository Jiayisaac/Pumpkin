import subprocess
import time


class WiFi:
    INTERFACE = 'wlan0'
    HOTSPOT_NAME = 'Pumpkin-Setup'
    HOTSPOT_PASSWORD = 'pumpkin123'

    @staticmethod
    def _run(*args):
        return subprocess.run(
            ['nmcli', *args],
            capture_output=True,
            text=True,
            check=True
        )

    @classmethod
    def connected(cls):
        result = subprocess.run(
            [
                'nmcli',
                '-t',
                '-f',
                'DEVICE,STATE',
                'device'
            ],
            capture_output=True,
            text=True
        )

        return f'{cls.INTERFACE}:connected' in result.stdout

    @classmethod
    def networks(cls):
        cls._run(
            'device',
            'wifi',
            'rescan',
            'ifname',
            cls.INTERFACE
        )

        time.sleep(2)

        result = cls._run(
            '-t',
            '-f',
            'SSID',
            'device',
            'wifi',
            'list',
            'ifname',
            cls.INTERFACE
        )

        networks = set()

        for line in result.stdout.splitlines():
            ssid = line.strip()

            if ssid:
                networks.add(ssid)

        return sorted(networks)

    @classmethod
    def connect(cls, ssid, password):
        cls.stop_hotspot()

        cls._run(
            'device',
            'wifi',
            'connect',
            ssid,
            'password',
            password,
            'ifname',
            cls.INTERFACE
        )

    @classmethod
    def start_hotspot(cls):
        if cls.connected():
            return

        cls._run(
            'device',
            'wifi',
            'hotspot',
            'ifname',
            cls.INTERFACE,
            'con-name',
            cls.HOTSPOT_NAME,
            'ssid',
            cls.HOTSPOT_NAME,
            'password',
            cls.HOTSPOT_PASSWORD
        )

    @classmethod
    def stop_hotspot(cls):
        subprocess.run(
            [
                'nmcli',
                'connection',
                'down',
                cls.HOTSPOT_NAME
            ],
            capture_output=True
        )
