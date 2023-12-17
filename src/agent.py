from typing import Optional
from src.transport import Address
from src.agent_message import AgentMessage
from src.protocol_engine import ProtocolEngine

class Agent:
    def __init__(self, address: Address, agent_platform, protocol_engine: ProtocolEngine):
        self.address = address
        self.agent_platform = agent_platform
        self.protocol_engine = protocol_engine
        self.message_callbacks = []

    def receive_message(self, sender: Address, message: AgentMessage):
        if message.protocol:
            message = self.protocol_engine.wrap_message(message)

        for callback in self.message_callbacks:
            callback(sender, message)

    def send_message(self, message: AgentMessage, to: Address, sender: Optional[Address] = None):
        if message.protocol:
            self.protocol_engine.validate_message(message)
            
        self.agent_platform.send_message(message, to, sender if sender else self.address)

    def start_protocol(self, protocol: str):
        return self.protocol_engine.start_protocol(protocol)
    
    def register_callback(self, callback):
        self.message_callbacks.append(callback)