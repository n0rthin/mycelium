from src.transport import Address

class Agent:
    def __init__(self, address: Address):
        self.address = address
        self.message_callbacks = []

    def receive_message(self, sender: Address, message):
        for callback in self.message_callbacks:
            callback(sender, message)
    
    def register_callback(self, callback):
        self.message_callbacks.append(callback)