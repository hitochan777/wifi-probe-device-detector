import argparse
import os
import time

from device_sniffer import DeviceSniffer
from attendance_upload_service import AttendanceUploadService


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='mon0', help='monitor mode enabled interface')
    args = parser.parse_args()

    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    upload_service = AttendanceUploadService(connection_string)
    device_sniffer = DeviceSniffer(args.interface)
    try:
        device_sniffer.start()
        observable = device_sniffer.get_observable()
        # observable.subscribe()
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        device_sniffer.stop()
        print("Exiting program...")
