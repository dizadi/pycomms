from __future__ import annotations
import abc
import threading
import time

class CommunicationLink(abc.ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.address}"

    @abc.abstractproperty
    def address(self) -> str:
        pass

class Receiver(CommunicationLink):
    @abc.abstractmethod
    def receive(self) -> bytes | None:
        pass

class DummyReceiver(Receiver):
    def receive(self) -> bytes | None:
        return None

class ThreadedReceiver(Receiver):
    def __init__(self, receiver: Receiver, message_processing_time_sec: float = 0.01) -> None:      
        self._receiver = receiver
        self._message_processing_time_sec = message_processing_time_sec
        self._message_queue = []
        self._receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
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

class Transmitter(CommunicationLink):
    @abc.abstractmethod
    def send(self, message: bytes) -> None:
        pass

class DummyTransmitter(CommunicationLink):
    def send(self, message: bytes) -> None:
        pass

class Channel(abc.ABC):
    def __repr__(self) -> str:
        return f"{[link for link in self.links]}"

    @abc.abstractproperty
    def links(self) -> list[CommunicationLink]:
        pass

class CommunicationChannel(Channel):
    def __init__(self, transmitter: Transmitter | None = None, receiver: Receiver | None = None) -> None:
        if transmitter is None:
            transmitter = DummyTransmitter()
        if receiver is None:
            receiver = DummyReceiver()
        super().__init__(self, links=[transmitter,receiver])
        self._transmitter = transmitter
        self._receiver = receiver

    def links(self) -> list[CommunicationLink]:
        return [self._receiver, self._transmitter]

    def receive(self) -> bytes | None:
        return self._receiver.receive()

    def send(self, message: bytes) -> None:
        self._transmitter.send(message)


class Network(abc.ABC):
    @abc.abstractproperty
    def channels(self) -> list[Channel]:
        pass