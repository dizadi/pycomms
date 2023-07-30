from __future__ import annotations
import abc
import threading
import time
import enums


class InformationDirection(enums.Enum):
    INCOMING: int = 1
    OUTGOING: int = 2
    BIDIRECTIONAL: int = 3


class CommunicationLink(abc.ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.address}"

    @abc.abstractproperty
    def address(self) -> str:
        pass

    @abc.abstractproperty
    def direction(self) -> InformationDirection:
        pass


class Receiver(CommunicationLink):
    @abc.abstractmethod
    def receive(self) -> bytes | None:
        pass

    @property
    def direction(self) -> InformationDirection:
        return InformationDirection.INCOMING


class DummyReceiver(Receiver):
    def receive(self) -> bytes | None:
        return None


class ThreadedReceiver(Receiver):
    def __init__(
        self, receiver: Receiver, message_processing_time_sec: float = 0.01
    ) -> None:
        self._receiver = receiver
        self._message_processing_time_sec = message_processing_time_sec
        self._message_queue = []
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


class Transmitter(CommunicationLink):
    @abc.abstractmethod
    def send(self, message: bytes) -> None:
        pass

    @property
    def direction(self) -> InformationDirection:
        return InformationDirection.OUTGOING


class DummyTransmitter(CommunicationLink):
    def send(self, message: bytes) -> None:
        pass


class Channel(abc.ABC):
    def __repr__(self) -> str:
        return f"{[link for link in self.links]}"

    @abc.abstractproperty
    def links(self) -> list[CommunicationLink]:
        pass

    @abc.abstractmethod
    def receive_from(self, address: str) -> bytes | None:
        pass

    @abc.abstractmethod
    def send_to(self, message: bytes, address: str) -> None:
        pass

    def _find_link_by_address(self, address: str) -> CommunicationLink | None:
        for link in self.links:
            if link.address == address:
                return link
        print(f"ERROR: {self.__class__.__name__} not connected {address}.")
        return None


class BaseChannel(Channel):
    def send_to(self, message: bytes, address: str):
        link = self._find_link_by_address(address=address)
        if link is not None and link.direction is not InformationDirection.INCOMING:
            link.send(message)

    def receive_from(self, address: str) -> bytes | None:
        link = self._find_link_by_address(address=address)
        if link is not None and link.direction is not InformationDirection.OUTGOING:
            return link.receive()
        return None


class TXRXChannel(BaseChannel):
    def __init__(
        self, transmitter: Transmitter | None = None, receiver: Receiver | None = None
    ) -> None:
        if transmitter is None:
            transmitter = DummyTransmitter()
        if receiver is None:
            receiver = DummyReceiver()
        super().__init__(self, links=[transmitter, receiver])
        self._transmitter = transmitter
        self._receiver = receiver

    def links(self) -> list[CommunicationLink]:
        return [self._receiver, self._transmitter]


class SIMOChannel(BaseChannel):
    def __init__(
        self, receiver: CommunicationLink, transmitters: list[Transmitter]
    ) -> None:
        self._receiver = receiver
        self._transmitters = transmitters

    def links(self) -> list[CommunicationLink]:
        return [self._receiver] + self._transmitters


class MISOChannel(BaseChannel):
    def __init__(self, receivers: list[Receiver], transmitter: Transmitter) -> None:
        self._receivers = receivers
        self._transmitter = transmitter

    def links(self) -> list[CommunicationLink]:
        return [self._receiver] + self._transmitters


class MIMOChannel(BaseChannel):
    def __init__(
        self, receivers: list[Receiver], transmitters: list[Transmitter]
    ) -> None:
        self._receivers = receivers
        self._transmitters = transmitters

    def links(self) -> list[CommunicationLink]:
        return self._receivers + self._transmitters


class Network(abc.ABC):
    @abc.abstractproperty
    def channels(self) -> list[Channel]:
        pass
