from typing import Optional


class UserQuerier:
    def __init__(self):
        pass

    def get_userid(self, ssid: str, source_mac_addr: str) -> Optional[str]:
        if ssid == "hitochan-probe":
            return "hitochan"

        return "NA"