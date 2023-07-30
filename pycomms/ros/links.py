
from pycomms import core
import rospy

class ROSReceiver(core.Receiver):
    def __init__(self, address):  
        self._address=address
        self._rospy_subscriber = rospy.Subscriber(self._address,rospy.String, callback=self._rospy_callback)
        self._received_data = b""
    
    @property
    def address(self) -> str:
        return self._address

    def receive(self) -> bytes | None:
        return self._received_data

    def _rospy_callback(self, message):
        self._received_data = message.data

class ROSTransmitter(core.Transmitter):
    def __init__(self, address: str, queue_size: int = 1):
        self._address=address
        self._rospy_publisher = rospy.Publisher(self._address, rospy.String, queue_size=queue_size)

    @property
    def address(self) -> str:
        return self._address
       
    def send(self, message: bytes) -> None:
        msg = rospy.String()
        msg.data = message
        self._rospy_publisher.publish(msg)
        