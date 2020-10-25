from typing import Optional
from datetime import datetime
import logging
from scapy.all import sniff, AsyncSniffer, Packet
from scapy.layers.dot11 import Dot11Elt
from rx.core import Observer
from rx.subject import Subject
import rx

from .attendance import Attendance
from .user_querier import UserQuerier


class DeviceSniffer:
    def __init__(self, user_querier: UserQuerier, interface="mon0"):
        self.async_sniffer = AsyncSniffer(prn=self.handle_packet, store=False,iface=interface, monitor=True)
        self.device_dectect_stream = Subject()
        self.user_querier = user_querier

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
            userid = self.user_querier.get_userid(target_ssid, source_mac_addr)
            if userid is not None:
                self.device_dectect_stream.on_next(userid)

        except Exception as err:
            self.device_dectect_stream.on_error(err)
    
    def get_observable(self) -> Subject:
        return self.device_dectect_stream

    def start(self):
        self.async_sniffer.start()

    def stop(self):
        self.async_sniffer.stop()