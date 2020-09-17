from typing import Optional, List
from rx.scheduler import NewThreadScheduler
from rx.disposable import Disposable
from datetime import datetime

class State:
    def detect_existence(self, context: "StateContext"):
        raise NotImplementedError()

    def detect_absence(self, context: "StateContext"):
        raise NotImplementedError()

class AttendingState(State):
    def __init__(self, absence_due_second: int):
        scheduler = NewThreadScheduler()
        self.absence_due_second = absence_due_second
        self.schedule_obj = scheduler.schedule_relative(absence_due_second, self.detect_absence)

    def __del__(self):
        if not self.schedule_obj.is_disposed:
            self.schedule_obj.dispose()

    def detect_existence(self, context: "StateContext"):
        # Do nothing
        pass

    def detect_absence(self, context: "StateContext"):
        self.schedule_obj.dispose()
        context.set_state(AbsentState(self.absence_due_second))
        pass

class AbsentState(State):
    def __init__(self, absence_due_second: int):
        self.absence_due_second = absence_due_second

    def detect_existence(self, context: "StateContext"):
        context.set_state(AttendingState(self.absence_due_second))

    def detect_absence(self, context: "StateContext"):
        # Do nothing
        pass

class AttendanceStateContext:
    def __init__(self, initial_state: State):
        self.state = initial_state 

    def set_state(self, new_state: State):
        self.state = new_state

    def detect_exitence(self):
        self.state.detect_existence()

    def detect_absence(self):
        self.state.detect_absence()


class SniffConfig:
    def __init__(self, userid: str, ssid: Optional[str], mac_address: Optional[str], is_attending: bool, state_updated_at: datetime, absence_due_second: int = 60 * 10):
        self.userid = userid
        self.ssid = ssid
        self.mac_address = mac_address
        self.is_attending = is_attending
        self.state_updated_at = state_updated_at
        self.absence_due_second = absence_due_second


class AttendaceStateContextManager:
    def __init__(self, sniff_configs: List[SniffConfig]):
        self.state_map = dict()
        for config in sniff_configs:
            self.add_by_user_id(config.userid, config)

    # def delete_by_user_id(self, userid: str):
    #     pass

    def add_by_user_id(self, userid: str, sniff_config: SniffConfig):
        assert userid == sniff_config.userid
        assert userid not in self.state_map
        # FIXME: compute initial absence due second from state_updated_at
        initial_state = AttendingState(sniff_config.absence_due_second) if sniff_config.is_attending else AbsentState(sniff_config.absence_due_second)
        self.state_map[sniff_config.userid] = AttendanceStateContext(initial_state)

    # def update_by_user_id(self, userid: str, sniff_config: SniffConfig)
    #     pass