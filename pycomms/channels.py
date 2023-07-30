from __future__ import annotations

from pycomms import links, core

class BaseChannel(core.Channel):
    def send_to(self, message: bytes, address: str):
        link = self._find_link_by_address(address=address)
        if link is not None and link.direction is not core.InformationFlow.INCOMING:
            link.send(message)

    def receive_from(self, address: str) -> bytes | None:
        link = self._find_link_by_address(address=address)
        if link is not None and link.direction is not core.InformationFlow.OUTGOING:
            return link.receive()
        return None
        
    def _find_link_by_address(self, address: str) -> core.CommunicationLink | None:
        for link in self.links:
            if link.address == address:
                return link
        print(f"ERROR: {self.__class__.__name__} not connected {address}.")
        return None

class TXRXChannel(BaseChannel):
    def __init__(
        self, transmitter: core.Transmitter | None = None, receiver: core.Receiver | None = None
    ) -> None:
        if transmitter is None:
            transmitter = links.DummyTransmitter()
        if receiver is None:
            receiver = links.DummyReceiver()
        super().__init__(self, links=[transmitter, receiver])
        self._transmitter = transmitter
        self._receiver = receiver

    def links(self) -> list[core.CommunicationLink]:
        return [self._receiver, self._transmitter]


class SIMOChannel(BaseChannel):
    def __init__(
        self, receiver: core.CommunicationLink, transmitters: list[core.Transmitter]
    ) -> None:
        self._receiver = receiver
        self._transmitters = transmitters

    def links(self) -> list[core.CommunicationLink]:
        return [self._receiver] + self._transmitters


class MISOChannel(BaseChannel):
    def __init__(self, receivers: list[core.Receiver], transmitter: core.Transmitter) -> None:
        self._receivers = receivers
        self._transmitter = transmitter

    def links(self) -> list[core.CommunicationLink]:
        return [self._receiver] + self._transmitters


class MIMOChannel(BaseChannel):
    def __init__(
        self, receivers: list[core.Receiver], transmitters: list[core.Transmitter]
    ) -> None:
        self._receivers = receivers
        self._transmitters = transmitters

    def links(self) -> list[core.CommunicationLink]:
        return self._receivers + self._transmitters
