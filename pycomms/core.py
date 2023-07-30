from __future__ import annotations
import abc
import enum


class InformationDirection(enum.Enum):
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


class Transmitter(CommunicationLink):
    @abc.abstractmethod
    def send(self, message: bytes) -> None:
        pass

    @property
    def direction(self) -> InformationDirection:
        return InformationDirection.OUTGOING


class Channel(abc.ABC):
    def __repr__(self) -> str:
        return f"{[link for link in self.links]}"

    @abc.abstractproperty
    def links(self) -> list[CommunicationLink]:
        pass

    @property
    def incoming_links(self) -> list[CommunicationLink]:
        return [link for link in self.links if link.direction is not InformationDirection.OUTGOING]
    
    @property
    def outgoing_links(self) -> list[CommunicationLink]:
        return [link for link in self.links if link.direction is not InformationDirection.INCOMING]

    @abc.abstractmethod
    def receive_from(self, address: str) -> bytes | None:
        pass

    @abc.abstractmethod
    def send_to(self, message: bytes, address: str) -> None:
        pass


class Network(abc.ABC):
    @abc.abstractproperty
    def channels(self) -> list[Channel]:
        pass
