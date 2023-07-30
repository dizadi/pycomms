from __future__ import annotations
import abc
import enum

class InformationFlow(enum.Enum):
    INCOMING: str = "<--"
    OUTGOING: str = "-->"
    BIDIRECTIONAL: str = "<->"


class NetworkMessage:
    address: str
    message: bytes
    direction: InformationFlow

class CommunicationLink(abc.ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.direction.value} {self.address}"

    @abc.abstractproperty
    def address(self) -> str:
        pass

    @abc.abstractproperty
    def direction(self) -> InformationFlow:
        pass


class Receiver(CommunicationLink):
    @abc.abstractmethod
    def receive(self) -> bytes | None:
        pass

    @property
    def direction(self) -> InformationFlow:
        return InformationFlow.INCOMING


class Transmitter(CommunicationLink):
    @abc.abstractmethod
    def send(self, message: bytes) -> None:
        pass

    @property
    def direction(self) -> InformationFlow:
        return InformationFlow.OUTGOING


class Channel(abc.ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} :\n {self.links}"

    @abc.abstractproperty
    def links(self) -> list[CommunicationLink]:
        pass

    @property
    def incoming_links(self) -> list[CommunicationLink]:
        return [link for link in self.links if link.direction is not InformationFlow.OUTGOING]
    
    @property
    def outgoing_links(self) -> list[CommunicationLink]:
        return [link for link in self.links if link.direction is not InformationFlow.INCOMING]

    @abc.abstractmethod
    def receive_from(self, address: str) -> bytes | None:
        pass

    @abc.abstractmethod
    def send_to(self, message: bytes, address: str) -> None:
        pass

    def receive(self) -> bytes | None:
        messages = self.receive_all()
        while len(messages):
            yield messages.pop(0)

    def send(self, message: bytes) -> None:
        self.send_all(message=message)

    def send_all(self, message: bytes) -> None:
        [self.send_to(message=message, address=link.address) for link in self.outgoing_links]
    
    def receive_all(self) -> dict[str, bytes | None]:
        return [{repr(incoming_link) : self.receive_from(incoming_link.address)} for incoming_link in self.links]

class Network(abc.ABC):
    @abc.abstractproperty
    def channels(self) -> list[Channel]:
        pass
    
    def __repr__(self) -> str:
        return f"{self.channels}"