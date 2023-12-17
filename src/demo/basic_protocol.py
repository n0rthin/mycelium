from src.agent import Agent
from src.agent_platform import AgentPlatform
from src.agent_message import AgentMessage
from src.protocol_engine import ProtocolEngine, ProtocolMessage
from src.protocol import Protocol
from src.transport import HTTPTransport, Address

contract_net_protocol = Protocol({
    "name": "contract-net",
    "version": "1.0.0",
    "roles": ["manager", "contractor"],
    "first_node_ids": ["0"],
    "nodes": [
        {
            "role": "manager",
            "node_id": "0",
            "prompt": "call-for-proposal",
            "next_node_ids": ["2", "3"],
        },
        {
            "role": "contractor",
            "node_id": "2",
            "prompt": "propose",
            "next_node_ids": ["0", "4", "5"],
        },
        {
            "role": "contractor",
            "node_id": "3",
            "prompt": "reject",
            "next_node_ids": None,
        },
        {
            "role": "manager",
            "node_id": "4",
            "prompt": "reject",
            "next_node_ids": None,
        },
         {
            "role": "manager",
            "node_id": "5",
            "prompt": "accept",
            "next_node_ids": ["6", "7"],
        },
         {
            "role": "contractor",
            "node_id": "6",
            "prompt": "inform",
            "next_node_ids": None,
        },
        {
            "role": "contractor",
            "node_id": "7",
            "prompt": "cancel",
            "next_node_ids": None,
        },
    ]
})

transport = HTTPTransport()
agent_platform = AgentPlatform(transport=transport)
protocol_engine = ProtocolEngine()

protocol_engine.load_protocol(contract_net_protocol)

agent_a = Agent(
    address=Address("http://127.0.0.1:8001", "agent_a"),
    agent_platform=agent_platform,
    protocol_engine=protocol_engine
)
agent_b = Agent(
    address=Address("http://127.0.0.1:8001", "agent_b"),
    agent_platform=agent_platform,
    protocol_engine=protocol_engine
)

def get_agent_cb(agent: Agent):
    def agent_cb(sender: Address, message):
        offset = " " * 5
        if isinstance(message, ProtocolMessage):
            guiding_prompt = "\n".join([offset * 2 + line for line in message.guiding_prompt.splitlines()]) if message.guiding_prompt else ""
            print(f"[{sender.name}]:")
            print(offset + f"Protocol: {message.agent_message.protocol}")
            print(offset + f"Protocol node id: {message.agent_message.current_protocol_node_id}")
            print(offset + f"Guiding prompt:")
            print(f"{guiding_prompt}")
            print(offset + f"Message: {message.agent_message.content}")
        elif isinstance(message, AgentMessage):
            print(f"[{sender.name}]: {message.content}")

    return agent_cb

agent_a.register_callback(get_agent_cb(agent_a))
agent_b.register_callback(get_agent_cb(agent_b))

agent_platform.register_agent(agent=agent_a)
agent_platform.register_agent(agent=agent_b)

# print(agent_a.start_protocol(contract_net_protocol.name))

agent_a.send_message(
    message=AgentMessage(
        content="call-for-proposal",
        conversation_id="conversation_id",
        protocol=contract_net_protocol.name,
        current_protocol_node_id="0",
        message_id="id",
        reply_to=agent_b.address,
    ),
    to=agent_b.address
)

agent_b.send_message(
    message=AgentMessage(
        content="propose",
        conversation_id="conversation_id",
        protocol=contract_net_protocol.name,
        current_protocol_node_id="2",
        message_id="id",
        reply_to=agent_a.address,
    ),
    to=agent_a.address
)