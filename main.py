import argparse
import os
import time
import json
from typing import List
from dataclasses import dataclass

from src.device_sniffer import DeviceSniffer
from src.attendance_upload_service import AttendanceUploadService
from src.state_context_manager import AttendanceStateContextManager
from src.config import Config
from src.user_querier import UserQuerier
from src.file_queue import FileQueue


@dataclass
class CommandLineArgs:
    interface: str
    queue_path: str
    configs: List[Config]


def cmdline() -> CommandLineArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='mon0', help='monitor mode enabled interface')
    parser.add_argument('--config', '-c', required=True, help='path to JSON config file')
    parser.add_argument('--queue-path', '-q', required=True, help='path for saving queue')
    args = parser.parse_args()

    configs: List[Config] = []
    with open(args.config, "r") as f:
        raw_configs = json.load(f)
        for raw_config in raw_configs:
            configs.append(Config(raw_config["userid"], raw_config["ssid"], raw_config["mac_address"], raw_config["absence_due_second"]))

    return CommandLineArgs(interface=args.interface, queue_path=args.queue_path, configs=configs)


if __name__ == "__main__":
    args = cmdline()
    print(f"Listening on {args.interface}")

    queue = FileQueue(args.queue_path)

    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    assert len(connection_string) > 0, "IoTHub connection string should not be empty"
    upload_service = AttendanceUploadService.create(connection_string, queue, is_dry_run=False)
    user_querier = UserQuerier(args.configs)
    device_sniffer = DeviceSniffer(user_querier, args.interface)
    state_context_manager = AttendanceStateContextManager(args.configs, device_sniffer.get_observable(), upload_service)
    try:
        device_sniffer.start()
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        device_sniffer.stop()
        print("Exiting program...")
