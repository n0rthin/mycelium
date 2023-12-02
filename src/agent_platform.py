from typing import Optional 
from src.transport import Transport, Address
from src.agent import Agent

class AgentMessage():
    # the actual information or data being communicated. This could be a command, a query, a statement, etc.
    content: str
    # an identifier used to associate this message with a conversation or a dialogue between agents. This helps in tracking and managing multi-message exchanges.
    conversation_id: Optional[str]
    # this optional field specifies the interaction protocol that the message adheres to
    protocol: Optional[str]
    # this optional field specifies the stage in the interaction protocol that the message adheres to
    protocol_stage: Optional[str]
    # an identifier set by the sender, which can be used by the receiver to reply to this specific message.
    message_id: Optional[str]
    # this optional field specifies an agent different from the sender to whom the replies should be sent
    reply_to: Optional[str]
    # if the message is a reply to a previous message, this field holds the identifier of the original message.
    in_reply_to: Optional[str]
    # an optional field indicating a time by which a reply is expected. This is useful in time-critical applications.
    reply_by: Optional[str]
    # this specifies the language in which the content of the message is expressed. This is useful in multi-lingual environments.
    language: Optional[str]

    def __init__(self, content: str, conversation_id: Optional[str] = None, protocol: Optional[str] = None, protocol_stage: Optional[str] = None, reply_with: Optional[str] = None, reply_to: Optional[str] = None, in_reply_to: Optional[str] = None, reply_by: Optional[str] = None, language: Optional[str] = None):
        self.content = content
        self.conversation_id = conversation_id
        self.protocol = protocol
        self.protocol_stage = protocol_stage
        self.reply_with = reply_with
        self.reply_to = reply_to
        self.in_reply_to = in_reply_to
        self.reply_by = reply_by
        self.language = language

class AgentPlatform():
    def __init__(self, transport: Transport):
        self.agents = []
        self.transport: Transport = transport
        self.transport.register_procedure("send_message", self.send_message)

    def register_agent(self, agent: Agent):
        existing_agent = self.find_agent_by_address(agent.address)
        if existing_agent:
            return
        
        self.agents.append(agent)

    def send_message(self, to: Address, sender: Address, message: AgentMessage):
        '''
        send_message is used for sending and receiving messages
        '''
        agent = self.find_agent_by_address(to)

        if agent:
            agent.receive_message(sender, message)
        else:
            self.transport.send_message(to, sender, "send_message", message)

    def find_agent_by_address(self, address: Address):
        for agent in self.agents:
            if agent.address.is_equal(address):
                return agent
