import threading

import requests
import sys
import signal
from os import getenv
from time import sleep
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
from requests import ConnectTimeout, ReadTimeout

class TasmotaCollector(object):
    def __init__(self):
        self.ips = getenv('DEVICE_IPS')
        if not self.ips:
            self.ips = "192.168.178.41"
        self.user = getenv('USER')
        self.password = getenv('PASSWORD')
        self.discover = getenv('DISCOVER_TASMOTAS')
        if not self.discover:
            self.discover = True
        self.discover_range = getenv('DISCOVER_RANGE')
        if not self.discover_range:
            self.discover_range = "192.168.178."

    def autodiscover(self):
        if self.discover:
            while True:
                found_tasmotas = self.find_tasmotas()
                for found in found_tasmotas.values():
                    if found in self.ips:
                        print(found + " in " + self.ips)
                    else:
                        print("adding " + found + " to Tasmota IPs")
                        self.ips = self.ips + "," + found
                sleep(60*60)

    def find_tasmotas(self):
        print("Autodiscovering started")
        target_range = range(1, 256)
        found_tasmotas = {}
        for sub_ip in target_range:
            ip = self.discover_range + str(sub_ip)
            try:
                url = 'http://' + ip + '/?m=1'
                response = requests.get(url=url, timeout=1)
                values = self.extract_values(response.text)
                if len(values.keys()) > 0:
                    found_tasmotas[ip] = ip
                    print(ip + ": " + str(values.keys()))
                    print(ip + ": is Tasmota device")
            except ConnectTimeout as e:
                print(ip + ": no Tasmota Device")
            except ReadTimeout as e:
                print(ip + ": no Tasmota Device")
            except OSError as e:
                print(ip + ": no Tasmota Device")
        print("Autodiscovering done")
        print("Found: " + str(found_tasmotas))
        return found_tasmotas

    def collect(self):
        all_ips = self.ips.split(",")

        for ip in all_ips:
            response = self.fetch(ip)
            for key in response:
                metric_name = "tasmota_" + self.replace_chars(key)
                metric = response[key].split()[0]
                unit = None
                if len(response[key].split()) > 1:
                    unit = response[key].split()[1]

                if "today" in metric_name or "yesterday" in metric_name or "total" in metric_name:
                    r = CounterMetricFamily(metric_name, key, labels=['device'], unit=unit)
                else:
                    r = GaugeMetricFamily(metric_name, key, labels=['device'], unit=unit)
                r.add_metric([ip], metric)
                yield r

    def replace_chars(self, key) -> Any:
        replacements = {
            "ä": "ae",
            "ö": "oe",
            "ü": "ue",
            "ß": "ss",
            "Ä": "Ae",
            "Ö": "Oe",
            "Ü": "Ue"
        }
        result = key.lower()
        for umlaut, replacement in replacements.items():
            result = result.replace(umlaut, replacement)
        return result.replace(" ", "_")

    def fetch(self, target_ip):
        url = 'http://' + target_ip + '/?m=1'
        session = requests.Session()
        extract_values = []
        if self.user and self.password:
            session.auth = (self.user, self.password)
        try:
            page = session.get(url=url, timeout=4)
            text = page.text
            extract_values = self.extract_values(text)
        except:
            return extract_values
        return extract_values

    def extract_values(self, text):
        values = {}
        string_values = str(text).split("{s}")
        for i in range(1, len(string_values)):
            try:
                label = string_values[i].split("{m}")[0]
                value = string_values[i].split("{m}")[1].split("{e}")[0]
                if "<td" in value:
                    value = value.replace("</td><td style='text-align:left'>", "")
                    value = value.replace("</td><td>&nbsp;</td><td>", "")

                values[label] = value
            except IndexError:
                continue
        return values


def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':

    print("starting exporter")
    port = getenv('EXPORTER_PORT')
    if not port:
        port = 8000

    start_http_server(int(port))
    collector = TasmotaCollector()
    REGISTRY.register(collector)

    tasmota_discover = threading.Thread(name='tasmota_switch', target=collector.autodiscover, args=())
    tasmota_discover.deamon = True
    tasmota_discover.start()

    while(True):
        sleep(10)
