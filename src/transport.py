from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn
import threading
import time

class Message(BaseModel):
    to: str
    sender: str
    date: float
    procedure: str
    payload: dict

class Transport():
    def __init__(self, address):
        self.address = address

    def set_service(self, service):
        self.service = service
        self.app = FastAPI()

        @self.app.post("/")
        async def process(msg: Message):
            print("incomming message", msg)
            procedure = getattr(self.service, msg.procedure, None)

            if not callable(procedure):
                return {"error": "Procedure not found"}
            
            return procedure(msg)
        
        return self.app
        

    def start(self, port=8000, host="127.0.0.1"):
        def run():
            uvicorn.run(self.app, host=host, port=port, log_level="info")

        threading.Thread(target=run).start()

    def send_message(self, to, procedure, payload):
        print("sending message", to, procedure, payload)
        requests.post(to, json={
            "to": to,
            "sender": self.address,
            "date": time.time(),
            "procedure": procedure,
            "payload": payload
        })
    
    