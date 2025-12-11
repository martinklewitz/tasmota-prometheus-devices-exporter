# tasmota-prometheus-devices-exporter

This a prometheus exporter for Tasmota devices. 

# Features

- collect metrics from Tasmota devices that are featured on the Tasmota screen
- ability to collect metrics from more than one device
- autodiscover Tasmota devices

# Running the image

## Example docker compose

### Parameters:
- EXPORTER_PORT: port of prometheus exporter
- DEVICE_IPS: list of preconfigured device IPs (comma seperated)
- DISCOVER_TASMOTAS: (True|False) should tasmota divices be autodiscovered
- DISCOVER_RANGE: subnet of IPs where exporter shoudld try to discover devices

```
version: "3.0"
services:
  tasmota-prometheus-devices-exporter:
    image: ghcr.io/martinklewitz/tasmota-prometheus-devices-exporter:latest
    restart: always
    ports:
      - 9099:8000
    environment:
      - PYTHONUNBUFFERED=1
      - EXPORTER_PORT=8000
      - DEVICE_IPS=192.168.178.85
      - DISCOVER_TASMOTAS=True
      - DISCOVER_RANGE=192.168.178.

```


# Recognition

This project was inspired by https://github.com/astr0n8t/tasmota-power-exporter

