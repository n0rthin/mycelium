from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn
import threading
import time

class Address():
    url: str
    name: str

    def __init__(self, url: str = None, name: str = None):
        self.url = url
        self.name = name

    def is_equal(self, address):
        return self.url == address.url and self.name == address.name

    def to_dict(self):
        return {
            "url": self.url,
            "name": self.name
        }
    
    
class AddressSchema(BaseModel):
    url: str
    name: str

class TransportMessage(BaseModel):
    to: AddressSchema
    sender: AddressSchema
    date: float
    procedure: str
    payload: dict

class Transport():
    def register_procedure(self, procedure, callback):
        pass

    def send_message(self, to: Address, sender: Address, procedure: str, payload: dict):
        pass

class HTTPTransport(Transport):
    def __init__(self):
        self.procedures = {}

    def register_procedure(self, procedure, callback):
        self.procedures[procedure] = callback

    def start(self, port=8000, host="127.0.0.1"):
        self.app = FastAPI()
        
        @self.app.post("/")
        async def process(msg: TransportMessage):
            msg.to = Address(msg.to.url, msg.to.name)
            msg.sender = Address(msg.sender.url, msg.sender.name)
            procedure = getattr(self.procedures, msg.procedure, None)

            if not callable(procedure):
                return {"error": "Procedure not found"}
            
            return procedure(msg)
    
        def run():
            uvicorn.run(self.app, host=host, port=port, log_level="info")

        threading.Thread(target=run).start()

    def send_message(self, to: Address, sender: Address, procedure: str, payload: dict):
        print("sending message", to.url, procedure, payload)
        requests.post(to.url, json={
            "to": to.to_dict(),
            "sender": sender.to_dict(),
            "date": time.time(),
            "procedure": procedure,
            "payload": payload
        })
    
