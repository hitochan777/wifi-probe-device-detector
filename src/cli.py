from datetime import datetime
import logging
import time
import argparse

from device_sniffer import DeviceSniffer


def print_capture(capture):
    logging.info(f"{capture[0]} {capture[1]}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='mon0', help='monitor mode enabled interface')
    parser.add_argument('--log-file', '-l', default='wifiscanner.log', help='path to filename to output log')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename='wifiscanner.log',level=logging.DEBUG)
    logging.info('\n' + '\033[93m' + 'Wifi Scanner Initialized' + '\033[0m' + '\n')
    print('\n' + '\033[93m' + 'Wifi Scanner Initialized' + '\033[0m' + '\n')

    device_sniffer = DeviceSniffer(args.interface)
    device_sniffer.start()
    device_sniffer.get_observable().subscribe(print_capture)
    input("Type any key to stop monitoring")
    device_sniffer.stop()

if __name__ == '__main__':
    main()
