from azure.iot.device import IoTHubDeviceClient, Message

from attendance import Attendance
from queue_service import FileQueue


class AttendanceUploadService:
    @staticmethod
    def create(connection_string, queue_path: str, is_dry_run = False):
        client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        queue = FileQueue(queue_path)
        return AttendanceUploadService(client, queue, is_dry_run=is_dry_run)

    def __init__(self, client: IoTHubDeviceClient, queue: FileQueue, is_dry_run = False):
        self.iothub_client = client
        self.is_dry_run = is_dry_run
        self.queue = queue

    def send_message(self, message: Message):
        try:
            self.iothub_client.send_message(message)
        except:
            self.queue.enqueue(message)

    def process_queued_messages(self):
        for item in self.queue.get_items():
            self.send_message(item)

    def upload(self, attendance: Attendance):
        message = self.convert_attendance_to_message(attendance)
        if not self.is_dry_run:
            self.send_message(message)
            self.process_queued_messages()

    def convert_attendance_to_message(self, attendance: Attendance):
        message_text = f'{{"type": {attendance.attendance_type.value},"occurredAt": "{attendance.occurred_at.isoformat(timespec="seconds")}", "userId": "{attendance.userid}"}}'
        return Message(message_text)