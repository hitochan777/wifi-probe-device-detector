from persistqueue import Queue

from .queue import Queue as QueueInterface

class FileQueue(QueueInterface):
    def __init__(self, path: str):
        self.queue = Queue(path, autosave=True)
    
    def is_empty(self) -> bool:
        return self.queue.empty()

    def get_items(self):
        while not self.is_empty():
            yield self.queue.get()

        return

    def enqueue(self, value: str):
        self.queue.put(value)