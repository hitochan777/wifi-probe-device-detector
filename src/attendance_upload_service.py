from azure.iot.device import IoTHubDeviceClient, Message

from attendance import Attendance


class AttendanceUploadService:
    @staticmethod
    def create(connection_string, is_dry_run = False):
        client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        return AttendanceUploadService(client, is_dry_run=is_dry_run)

    def __init__(self, client: IoTHubDeviceClient, is_dry_run = False):
        self.iothub_client = client
        self.is_dry_run = is_dry_run

    def upload(self, attendance: Attendance):
        message = self.convert_attendance_to_message(attendance)
        print(message)
        if not self.is_dry_run:
            self.iothub_client.send_message(message)

    def convert_attendance_to_message(self, attendance: Attendance):
        message_text = f'{{"type": {attendance.attendance_type.value},"occurredAt": {attendance.occurred_at.isoformat(timespec="seconds")+"Z"}, "userId": {attendance.userid}}}'
        return Message(message_text)