from src.agent_message import AgentMessage
from src.protocol import Protocol

prompt_template = "\n".join([
    "This message is a part of {protocol_name} protocol.",
    "You can only respond with messages that comply with one of the following instruction:",
    "{instructions}"
])

instruction_prompt = "Node id: {node_id}, Instruction: {instruction}"

last_message_prompt = "This the last message in the {protocol_name} protocol"

class ProtocolMessage:
    agent_message: AgentMessage
    next_nodes: list | None
    guiding_prompt: str | None

    def __init__(self, agent_message: AgentMessage, next_nodes: list | None, guiding_prompt: str | None):
        self.agent_message = agent_message
        self.guiding_prompt = guiding_prompt
        self.next_nodes = next_nodes

class ProtocolEngine:
    def __init__(self):
        self.protocols = {} # Store protocols by name

    def load_protocol(self, protocol: Protocol):
        """Load a new protocol into the engine."""
        self.protocols[protocol.name] = protocol

    def start_protocol(self, protocol_name):
        """
        Initiates protocol.
        
        Raises:
        ValueError: If the protocol name is not found in the loaded protocols.
        """
        if protocol_name not in self.protocols:
            raise ValueError(f"Unknown protocol: {protocol_name}")

        protocol = self.protocols[protocol_name]
        first_nodes = protocol.get_next_nodes()

        return {
            "next_nodes": first_nodes,
            "guiding_prompt": self.get_guiding_prompt_for_nodes(protocol_name, first_nodes)
        }
    
    def wrap_message(self, message: AgentMessage) -> ProtocolMessage:
        """
        Wraps the message in a ProtocolMessage.
        
        Raises:
        ValueError: If the protocol in the message is not found in the loaded protocols.
        """
        if message.protocol not in self.protocols:
            raise ValueError(f"Unknown protocol: {message.protocol}")
         
        protocol = self.protocols[message.protocol]
        next_nodes = protocol.get_next_nodes(message.current_protocol_node_id)
        guiding_prompt = last_message_prompt.format(protocol_name=protocol.name)

        if len(next_nodes) > 0:
            guiding_prompt = self.get_guiding_prompt_for_nodes(message.protocol, next_nodes)

        return ProtocolMessage(
            agent_message=message,
            next_nodes=next_nodes,
            guiding_prompt=guiding_prompt,
        )

    def validate_message(self, message: AgentMessage):
        """Validate a message against the protocol."""
        if message.protocol not in self.protocols:
            raise ValueError(f"Unknown protocol: {message.protocol}")
        
        protocol = self.protocols[message.protocol]
        node = protocol.get_node_by_id(message.current_protocol_node_id)
        if node is None:
            raise ValueError(f"Unknown node id: {message.current_protocol_node_id} in the protocol: {message.protocol}. Message id: {message.message_id}")

    def get_guiding_prompt_for_nodes(self, protocol_name, nodes):
        instructions = "\n".join([instruction_prompt.format(node_id=node["node_id"], instruction=node["prompt"]) for node in nodes])
        return prompt_template.format(protocol_name=protocol_name, instructions=instructions)