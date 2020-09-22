from rx.scheduler import NewThreadScheduler
from rx.subject import Subject
from rx import Observable

from attendance_type import AttendanceType

class AttendancenStateContext:
    def __init__(self, userid: str, is_attending: bool, attend_notifier: Observable, absence_due_second: int = 3):
        self.userid = userid
        self.is_attending = is_attending
        self.schedule_obj = None
        if is_attending:
            self.detect_attendance(userid)

        self.absence_due_second = absence_due_second
        self.subject = Subject()
        attend_notifier.subscribe(self.detect_attendance)

    def __del__(self):
        self.clear_scheduler_if_running()
    
    def clear_scheduler_if_running(self):
        if self.schedule_obj is not None and not self.schedule_obj.is_disposed:
            self.schedule_obj.dispose()

    def update_scheduler(self):
        self.clear_scheduler_if_running()
        self.schedule_obj = NewThreadScheduler().schedule_relative(self.absence_due_second, self.detect_absence)

    def detect_attendance(self, userid: str):
        assert self.userid == userid
        self.update_scheduler()
        if not self.is_attending:
            self.subject.on_next({
                "type": AttendanceType.Attend,
                "userid": userid
            })

        self.is_attending = True

    def detect_absence(self, _, __):
        self.is_attending = False
        self.subject.on_next({
            "type": AttendanceType.Leave,
            "userid": self.userid
        })

    def get_observable(self):
        return self.subject