import argparse
import os
import time
import json
from typing import List

from device_sniffer import DeviceSniffer
from attendance_upload_service import AttendanceUploadService
from state_context_manager import AttendanceStateContextManager 
from config import Config
from user_querier import UserQuerier

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='mon0', help='monitor mode enabled interface')
    parser.add_argument('--config', '-c', default='mon0', help='path to JSON config file')
    args = parser.parse_args()
    print(f"Listening on {args.interface}")

    configs: List[Config] = []
    with open(args.config, "r") as f:
        raw_configs = json.load(f)
        for raw_config in raw_configs:
            configs.append(Config(raw_config["userid"], raw_config["ssid"], raw_config["mac_address"], raw_config["absence_due_second"]))

    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    assert len(connection_string) > 0, "IoTHub connection string should not be empty"
    upload_service = AttendanceUploadService.create(connection_string, is_dry_run=False)
    user_querier = UserQuerier(configs)
    device_sniffer = DeviceSniffer(user_querier, args.interface)
    state_context_manager = AttendanceStateContextManager(configs, device_sniffer.get_observable(), upload_service)
    try:
        device_sniffer.start()
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        device_sniffer.stop()
        print("Exiting program...")
