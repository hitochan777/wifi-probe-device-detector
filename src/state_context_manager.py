from typing import List
from rx.subject import Subject
from rx import Observable
from rx import operators
import json

from attendance_type import AttendanceType
from device_sniffer import DeviceSniffer
from config import Config
from state_context import AttendancenStateContext 


class AttendanceStateContextManager:
    def __init__(self, sniff_configs: List[Config], attend_notifier: Observable):
        self.attend_notifier = attend_notifier
        attend_notifier.subscribe(lambda x: print(x)) 
        self.observable_map = dict()
        for config in sniff_configs:
            self.add_by_user_id(config.userid, config)

    def delete_by_user_id(self, userid: str):
        if userid not in self.observable_map:
            raise KeyError(f"{userid} not found")

        del self.observable_map[userid]

    def add_by_user_id(self, userid: str, sniff_config: Config):
        assert userid == sniff_config.userid
        assert userid not in self.observable_map
        filtered_notification = self.attend_notifier.pipe(operators.filter(lambda uid: uid == userid))
        context = AttendancenStateContext(userid, False, filtered_notification)
        self.observable_map[sniff_config.userid] = context.get_observable()
        self.observable_map[sniff_config.userid].subscribe(self.handle_state_change)

    def handle_state_change(self, payload):
        if payload["type"] == AttendanceType.Attend:
            print(f"{payload['userid']} is attending")
            # TODO: write to db and publish message
            pass
        elif payload["type"] == AttendanceType.Leave:
            print(f"{payload['userid']} is leaving")
            # TODO: write to db and publish message
            pass
        else:
            raise ValueError(f"{payload['type']} is not expected")


    def update_by_user_id(self, userid: str, sniff_config: Config):
        self.delete_by_user_id(userid)
        self.add_by_user_id(userid, sniff_config)
    