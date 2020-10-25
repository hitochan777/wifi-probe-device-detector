from azure.iot.device import IoTHubDeviceClient, Message

from .attendance import Attendance
from .queue import Queue


class AttendanceUploadService:
    @staticmethod
    def create(connection_string, queue: Queue, is_dry_run = False):
        client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        return AttendanceUploadService(client, queue, is_dry_run=is_dry_run)

    def __init__(self, client: IoTHubDeviceClient, queue: Queue, is_dry_run = False):
        self.iothub_client = client
        self.is_dry_run = is_dry_run
        self.queue = queue

    def send_message(self, message: Message) -> bool:
        try:
            print(f"Sending: {message}")
            self.iothub_client.send_message(message)
            print(f"Sent: {message}")
        except:
            self.queue.enqueue(message)

    def process_queued_messages(self):
        # get_items keeps yielding item as long as there is an item so first get a list at the certain point
        items = list(self.queue.get_items())
        print(items)
        for item in items:
            self.send_message(item)

    def upload(self, attendance: Attendance):
        message = self.convert_attendance_to_message(attendance)
        if not self.is_dry_run:
            self.process_queued_messages()
            self.send_message(message)

    def convert_attendance_to_message(self, attendance: Attendance):
        message_text = f'{{"type": {attendance.attendance_type.value}, "occurredAt": "{attendance.occurred_at.isoformat(timespec="seconds")}", "userId": "{attendance.userid}"}}'
        return Message(message_text)