from persistqueue import Queue

class FileQueue:
    def __init__(self, filename: str):
        self.queue = Queue(filename, autosave=True)
    
    def is_empty(self) -> bool:
        return self.queue.empty()

    def get_items(self):
        if self.is_empty():
            return

        yield self.queue.get()

    def enqueue(self, value: str):
        self.queue.put(value)