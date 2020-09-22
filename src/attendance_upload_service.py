from azure.iot.device import IoTHubDeviceClient, Message

from attendance import Attendance


class AttendanceUploadService:
    @staticmethod
    def iothub_client_init(connection_string):
        client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        return client

    def __init__(self, client: IoTHubDeviceClient):
        self.iothub_client = client 

    def upload(self, attendance: Attendance):
        message = self.convert_attendance_to_message(attendance)
        self.iothub_client.send_message(message)

    def convert_attendance_to_message(self, attendance: Attendance):
        message_text= f'{{"type": {attendance.attendance_type},"attendance": {attendance.occurred_at}}}'
        return Message(message_text)