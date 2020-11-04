import argparse
import os
import time
import json
from typing import List
from dataclasses import dataclass
import scapy
import subprocess
from rx.scheduler import NewThreadScheduler


from src.device_sniffer import DeviceSniffer
from src.attendance_upload_service import AttendanceUploadService
from src.state_context_manager import AttendanceStateContextManager
from src.config import Config
from src.user_querier import UserQuerier
from src.file_queue import FileQueue
from src.connection_service import ConnectionService, SimpleConnectionService


@dataclass
class CommandLineArgs:
    interface: str
    queue_path: str
    enable_monitor_wakeup: bool
    configs: List[Config]
    enable_regular_queue_check: bool
    regular_queue_check_interval: int


def send_queued_messages_if_connected_to_internet(upload_service: AttendanceUploadService, connection_service: ConnectionService) -> None:
    print("Checking unsent messages...")
    if not connection_service.is_connected_to_internet():
        print("No internet connection")
        return

    print("Sending unsent messages...")
    upload_service.process_queued_messages()
    print("Sent unsent messages")


def cmdline() -> CommandLineArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='mon0', help='monitor mode enabled interface')
    parser.add_argument('--config', '-c', required=True, help='path to JSON config file')
    parser.add_argument('--queue-path', '-q', required=True, help='path for saving queue')
    parser.add_argument('--enable-monitor-on-wakeup', '-w', action='store_true', help='Enable monitor mode on specified interface on startup')
    parser.add_argument('--enable-regular-queue-check', '-r', action='store_true', help='Regularly check queue and send messages if any')
    parser.add_argument('--regular-queue-check-interval', type=int, default=600, help='Interval for checking queue (seconds)')
    args = parser.parse_args()

    configs: List[Config] = []
    with open(args.config, "r") as f:
        raw_configs = json.load(f)
        for raw_config in raw_configs:
            configs.append(Config(raw_config["userid"], raw_config["ssid"], raw_config["mac_address"], raw_config["absence_due_second"]))

    return CommandLineArgs(
        interface=args.interface, 
        queue_path=args.queue_path, 
        enable_monitor_wakeup=args.enable_monitor_on_wakeup, 
        configs=configs, 
        enable_regular_queue_check=args.enable_regular_queue_check,
        regular_queue_check_interval=args.regular_queue_check_interval
    )


def enable_monitor_mode(interface: str) -> None:
    cmd_result = subprocess.run(["ip", "link", "set", interface, "down"])
    if cmd_result.returncode == -1:
        raise RuntimeError()
    
    cmd_result = subprocess.run(["iw", interface, "set", "monitor", "none"])
    if cmd_result.returncode == -1:
        raise RuntimeError()

    cmd_result = subprocess.run(["ip", "link", "set", interface, "up"])
    if cmd_result.returncode == -1:
        raise RuntimeError()

if __name__ == "__main__":
    args = cmdline()

    if args.enable_monitor_wakeup:
        try:
            enable_monitor_mode(args.interface)
        except:
            raise RuntimeError("Failed while enabling monitor mode")

    print(f"Listening on {args.interface}")

    queue = FileQueue(args.queue_path)

    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    assert len(connection_string) > 0, "IoTHub connection string should not be empty"
    upload_service = AttendanceUploadService.create(connection_string, queue, is_dry_run=False)
    user_querier = UserQuerier(args.configs)
    device_sniffer = DeviceSniffer(user_querier, args.interface)
    state_context_manager = AttendanceStateContextManager(args.configs, device_sniffer.get_observable(), upload_service)
    if args.enable_regular_queue_check:
        regular_check_task = NewThreadScheduler().schedule_periodic(
            args.regular_queue_check_interval, 
            lambda x: send_queued_messages_if_connected_to_internet(upload_service, SimpleConnectionService())
        )
    try:
        device_sniffer.start()
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        device_sniffer.stop()
        regular_check_task.dispose()
        print("Exiting program...")
