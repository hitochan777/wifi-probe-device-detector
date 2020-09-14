from datetime import datetime
from scapy.all import sniff, AsyncSniffer, Packet, Dot11Elt
import logging
import time
import argparse


def is_probe_request(packet: Packet):
    return packet.type == 0 and packet.subtype == 4


def handle_packet(packet: Packet):
    if not is_probe_request(packet):
        return

    try:
        target_ssid = packet.getlayer(Dot11Elt).getfieldval("info").decode("utf-8")
        if len(target_ssid) == 0:
            return

        source_mac_addr = packet.addr2.upper()
        logging.info(f"{target_ssid} {source_mac_addr}")
    except Exception as err:
        logging.error(err)


def main():

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',filename='wifiscanner.log',level=logging.DEBUG)
    logging.info('\n' + '\033[93m' + 'Wifi Scanner Initialized' + '\033[0m' + '\n')
    print('\n' + '\033[93m' + 'Wifi Scanner Initialized' + '\033[0m' + '\n')

    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', default='mon0', help='monitor mode enabled interface')
    args = parser.parse_args()
    t = AsyncSniffer(prn=handle_packet, store=False,iface=args.interface, monitor=True)
    t.start()
    input("Type any key to stop monitoring")
    t.stop()

if __name__ == '__main__':
    main()
