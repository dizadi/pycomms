
import threading
import time
from pycomms import core


class DummyTransmitter(core.Transmitter):
    def send(self, message: bytes) -> None:
        pass

class DummyReceiver(core.Receiver):
    def receive(self) -> bytes | None:
        return None

class ThreadedReceiver(core.Receiver):
    def __init__(
        self, receiver: core.Receiver, message_processing_time_sec: float = 0.01
    ) -> None:
        self._receiver = receiver
        self._message_processing_time_sec = message_processing_time_sec
        self._message_queue: list[bytes] = []
        self._receive_thread = threading.Thread(
            target=self._receive_messages, daemon=True
        )
        self._receive_thread.start()

    @property
    def address(self) -> str:
        return self._receiver.address

    def receive(self) -> bytes | None:
        if not len(self._message_queue):
            return None
        return self._message_queue.pop()

    def _receive_message_loop(self):
        while self._receive_thread.is_alive():
            next_message = self._receiver.receive()
            if next_message is not None:
                self._message_queue.append(next_message)
            time.sleep(self._message_processing_time_sec)
