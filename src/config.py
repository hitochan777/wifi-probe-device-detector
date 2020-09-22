from typing import Optional


class Config:
    def __init__(self, userid: str, ssid: Optional[str], mac_address: Optional[str], absence_due_second: int = 60 * 10):
        self.userid = userid
        self.ssid = ssid
        self.mac_address = mac_address
        self.absence_due_second = absence_due_second