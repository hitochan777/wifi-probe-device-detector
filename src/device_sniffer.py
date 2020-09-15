from datetime import datetime
import logging
from scapy.all import sniff, AsyncSniffer, Packet
from scapy.layers.dot11 import Dot11Elt
from rx.core import Observer
from rx.subject import Subject
import rx

class DeviceSniffer():
    def __init__(self, interface="mon0"):
        self.async_sniffer = AsyncSniffer(prn=self.handle_packet, store=False,iface=interface, monitor=True)
        self.device_dectect_stream = Subject()

    def __del__(self):
        self.device_dectect_stream.on_completed()

    @staticmethod
    def is_probe_request(packet: Packet):
        return packet.type == 0 and packet.subtype == 4

    def handle_packet(self, packet: Packet):
        if not DeviceSniffer.is_probe_request(packet):
            return

        try:
            target_ssid = packet.getlayer(Dot11Elt).getfieldval("info").decode("utf-8")
            if len(target_ssid) == 0:
                return

            source_mac_addr = packet.addr2.upper()
            # logging.info(f"{target_ssid} {source_mac_addr}")
            self.device_dectect_stream.on_next((target_ssid, source_mac_addr))
        except Exception as err:
            # logging.error(err)
            self.device_dectect_stream.on_error(err)
    
    def get_observable(self):
        return self.device_dectect_stream

    def start(self):
        self.async_sniffer.start()

    def stop(self):
        self.async_sniffer.stop()