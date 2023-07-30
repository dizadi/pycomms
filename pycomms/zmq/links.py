from pycomms import core
import zmq

class ZMQSubscriber(core.Receiver):
    def __init__(self, address: str, bind: bool=False):
        self._address = address
        context = zmq.Context()
        self._socket = context.socket(zmq.SUB)
        if not bind:
            self._socket.connect(self._address)
        else:
            self._socket.bind(address)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, "")

    @property
    def address(self) -> str:
        return self._address

    def receive(self) -> bytes | None:
        return self._socket.recv()

class ZMQPublisher(core.Transmitter):
    def __init__(self, address: str, topics: list[str] = [], bind: bool=True):
        self._address = address
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        if not bind:
            self._socket.connect(self._address)
        else:
            self._socket.bind(address)
        self._socket.setsockopt_string(zmq.PUBLISH, "")

    @property
    def address(self) -> str:
        return self._address

    def send(self, message: bytes) -> None:
        self._socket.send(message)