from datetime import datetime

from .attendance_type import AttendanceType

class Attendance:
    def __init__(self, userid: str, attendance_type: AttendanceType, occurred_at: datetime):
        self.userid = userid
        self.attendance_type = attendance_type 
        self.occurred_at = occurred_at