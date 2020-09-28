from typing import List
from rx.subject import Subject
from rx import Observable
from rx import operators
import json
from datetime import datetime, timezone

from attendance_type import AttendanceType
from device_sniffer import DeviceSniffer
from config import Config
from state_context import AttendancenStateContext 
from attendance_upload_service import AttendanceUploadService
from attendance import Attendance


class AttendanceStateContextManager:
    def __init__(self, sniff_configs: List[Config], attend_notifier: Observable, upload_service: AttendanceUploadService):
        self.attend_notifier = attend_notifier
        self.observable_map = dict()
        for config in sniff_configs:
            self.add_by_user_id(config.userid, config)

        self.upload_service = upload_service

    def delete_by_user_id(self, userid: str):
        if userid not in self.observable_map:
            raise KeyError(f"{userid} not found")

        del self.observable_map[userid]

    def add_by_user_id(self, userid: str, sniff_config: Config):
        assert userid == sniff_config.userid
        assert userid not in self.observable_map
        filtered_notification = self.attend_notifier.pipe(operators.filter(lambda uid: uid == userid)).pipe(operators.throttle_first(1))
        context = AttendancenStateContext(userid, False, filtered_notification)
        self.observable_map[sniff_config.userid] = context.get_observable()
        self.observable_map[sniff_config.userid].subscribe(self.handle_state_change)

    def handle_state_change(self, payload):
        now = datetime.now(timezone.utc)
        if payload["type"] in [AttendanceType.Attend, AttendanceType.Leave]:
            self.upload_service.upload(Attendance(payload["userid"], payload["type"], now))
        else:
            raise ValueError(f"{payload['type']} is not expected")


    def update_by_user_id(self, userid: str, sniff_config: Config):
        self.delete_by_user_id(userid)
        self.add_by_user_id(userid, sniff_config)
    