from typing import Optional, List

from config import Config


class UserQuerier:
    def __init__(self, configs: List[Config]):
        self.ssid_lookup = {}
        self.mac_address_lookup = {}
        for config in configs:
            assert config.ssid not in self.ssid_lookup 
            assert config.mac_address not in self.mac_address_lookup
            self.ssid_lookup[config.ssid] = config.userid
            self.ssid_lookup[config.mac_address] = config.userid


    def get_userid(self, ssid: str, source_mac_addr: str) -> Optional[str]:
        if ssid in self.ssid_lookup:
            return self.ssid_lookup[ssid]

        if source_mac_addr in self.mac_address_lookup:
            return self.mac_address_lookup[source_mac_addr]

        return None