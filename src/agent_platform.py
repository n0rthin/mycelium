from src.transport import Transport, Address
from src.agent_message import AgentMessage
from src.agent import Agent
from src.helpers.logic import xor
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

    def deregister_agent(self, agentOrAddress: Agent | Address):
        if isinstance(agentOrAddress, Address):
            existing_agent = self.find_agent_by_address(agentOrAddress)
        elif isinstance(agentOrAddress, Agent):
            existing_agent = self.find_agent_by_address(agentOrAddress.address)
        else:
            raise ValueError(f"agentOrAddress must be either an instance of Address or Agent")
            
        if existing_agent:
            self.agents.remove(existing_agent)

    def send_message(self, message: AgentMessage, to: Address, sender: Address):
        '''
        send_message is used for sending and receiving messages

        Raises:
        ValueError: If message is not valid
        '''
        self.validate_message(message)

        agent = self.find_agent_by_address(to)
        if agent:
            agent.receive_message(sender, message)
        else:
            self.transport.send_message(to, sender, "send_message", message)

    def validate_message(self, message: AgentMessage):
        """
        Validates the given message. 

        Raises:
        ValueError: If message is not valid
        """
        if xor(message.protocol, message.current_protocol_node_id):
            raise ValueError("Either both or none of 'protocol' and 'current_protocol_node_id' should be set.")
        
        if message.protocol and not message.conversation_id:
            raise ValueError("If 'protocol' is set, 'conversation_id' must also be set.")

    def find_agent_by_address(self, address: Address):
        for agent in self.agents:
            if agent.address.is_equal(address):
                return agent
