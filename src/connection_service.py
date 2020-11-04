import abc
import socket

class ConnectionService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_connected_to_internet(self) -> bool:
        raise NotImplementedError()

class SimpleConnectionService(ConnectionService):
    def is_connected_to_internet(self, host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            print(ex)
            return False