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

class HTTPTransport():
    def __init__(self, address: Address):
        self.address = address

    def set_service(self, service):
        self.service = service
        self.app = FastAPI()

        @self.app.post("/")
        async def process(msg: TransportMessage):
            msg.to = Address(msg.to.url, msg.to.name)
            msg.sender = Address(msg.sender.url, msg.sender.name)
            procedure = getattr(self.service, msg.procedure, None)

            if not callable(procedure):
                return {"error": "Procedure not found"}
            
            return procedure(msg)
        
        return self.app
        

    def start(self, port=8000, host="127.0.0.1"):
        def run():
            uvicorn.run(self.app, host=host, port=port, log_level="info")

        threading.Thread(target=run).start()

    def send_message(self, to: Address, procedure: str, payload: dict):
        print("sending message", to.url, procedure, payload)
        requests.post(to.url, json={
            "to": to.to_dict(),
            "sender": self.address.to_dict(),
            "date": time.time(),
            "procedure": procedure,
            "payload": payload
        })
    
