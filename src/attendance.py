from datetime import datetime

from attendance_type import AttendanceType

class Attendance:
    def __init__(self, userId: str, attendance_type: AttendanceType, occurredAt: datetime):
        self.userId = userId
        self.attendance_type = attendance_type 
        self.occurredAt = occurredAt