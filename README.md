# wifi-probe-device-detector

Detects devices' arrival and departure using WiFi probe request (MAC address or SSID)

## Requirements

Python >= 3.8 or Docker

## Installation

### Python

```
pipenv install
```

### Docker

```
$ docker pull docker.pkg.github.com/hitochan777/wifi-probe-device-detector/wifi-probe-device-detector:0.0.1
```

## Usage

1. Create configuration file. This file contains a list of configuration which enables the detector to map SSID or MAC address to an username, and other optional information.

   ```json
		[
			{
				"userid": "foo",
				"ssid": "foo-probe",
				"mac_address": null,
				"absence_due_second": 600
			},
			{
				"userid": "bar",
				"ssid": null,
				"mac_address": "01:23:45:67:89:01",
				"absence_due_second": 300
			}
		]
	 ```
1. Export environment variable necessary to run detector server

```
$ export IOTHUB_DEVICE_CONNECTION_STRING="azure iothub connection string here"
$ export MONITOR_INTERFACE_NAME="monitor interface name here"
$ export PATH_TO_CONFIG_FILE="path/to/config/file.json"
```

1. Run a detector server
```
$ python src/main.py -i $MONITOR_INTERFACE_NAME -c $PATH_TO_CONFIG_FILE # For Python
$ docker run -it --net="host" --env IOTHUB_DEVICE_CONNECTION_STRING="$IOTHUB_DEVICE_CONNECTION_STRING" -v \$(pwd):/code wifi-scanner python src/main.py -i $MONITOR_INTERFACE_NAME -c $PATH_TO_CONFIG_FILE # For Docker
```

Everytime it detects arrival or departure of a configured device, it will automatically upload a payload to IoTHub.

## Payload structure

The payload uploaded to IoTHub has the following format.
`type` is either 0 (arrival) or 1 (departure).
As an example, You can then invoke Azure Function via IoTHub Trigger to further process the payloads.

```json
{
	"userid": "foo",
	"type": 0,
	"occurred_at": "2020-09-30T09:02:32"
}
```

## Future work

- CRUD operation of configuration via IoTHub
