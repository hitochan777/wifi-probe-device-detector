from datetime import datetime

from attendance_type import AttendanceType

class Attendance:
    def __init__(self, attendance_type: AttendanceType, occurredAt: datetime):
        self.attendance_type = attendance_type 
        self.occurredAt = occurredAt