from dotenv import load_dotenv
load_dotenv()

import uuid
from src.agent import Agent as MycAgent
from src.experiments.agent import Agent, ToolsService
from src.agent_platform import AgentPlatform
from src.agent_message import AgentMessage
from src.protocol_engine import ProtocolEngine, ProtocolMessage
from src.protocol import Protocol
from src.transport import HTTPTransport, Address

# initialize agent platform
transport = HTTPTransport()
agent_platform = AgentPlatform(transport=transport)
protocol_engine = ProtocolEngine()

# register protocol
contract_net_protocol = Protocol({
    "name": "contract-net",
    "version": "1.0.0",
    "roles": ["manager", "contractor"],
    "first_node_ids": ["0"],
    "prompt_description": "Contract-net protocol",
    "nodes": [
        {
            "role": "manager",
            "node_id": "0",
            "prompt": "call-for-proposal - ask contractor for possible solutions and when they want to do the task",
            "next_node_ids": ["2", "3"],
        },
        {
            "role": "contractor",
            "node_id": "2",
            "prompt": "propose - propose a potential solution",
            "next_node_ids": ["0", "4", "5"],
        },
        {
            "role": "contractor",
            "node_id": "3",
            "prompt": "reject - reject the task",
            "next_node_ids": None,
        },
        {
            "role": "manager",
            "node_id": "4",
            "prompt": "reject - reject the proposed solution",
            "next_node_ids": None,
        },
         {
            "role": "manager",
            "node_id": "5",
            "prompt": "accept - accept the proposed solution",
            "next_node_ids": ["6", "7"],
        },
         {
            "role": "contractor",
            "node_id": "6",
            "prompt": "inform - inform manager that the task has been completed",
            "next_node_ids": None,
        },
        {
            "role": "contractor",
            "node_id": "7",
            "prompt": "cancel - cancel the task",
            "next_node_ids": None,
        },
    ]
})
protocol_engine.load_protocol(contract_net_protocol)

# setup tools service
agents = {}
agent_to_agent_message_template = '''===Incoming message===
agent_id: {sender_id}
conversation_id: {conversation_id}
protocol: {protocol}
protocol guide:
{protocol_guide}
message_content: 
{message}
===End of Incoming message from==='''

def send_message(sender_agent_id, agent_id, message, conversation_id, protocol, protocol_node_id):
    sender_agent = agents[sender_agent_id]
    receiver_agent = agents[agent_id]

    receiver = receiver_agent.myc_agent.address
    sender_agent.myc_agent.send_message(
        message=AgentMessage(
            content=message,
            conversation_id=conversation_id,
            protocol=protocol,
            current_protocol_node_id=protocol_node_id,
            message_id=str(uuid.uuid4()),
            reply_to=sender_agent.myc_agent.address,
        ),
        to=receiver
    )
    return "Message has been sent. You will be notifed once reciever responds."

def start_protocol(sender_agent_id, protocol_name):
    initialized_protocol = agents[sender_agent_id].myc_agent.start_protocol(protocol_name)
    return initialized_protocol["guiding_prompt"] + "\n" + "Conversation id: " + str(uuid.uuid4())

tools_service = ToolsService()
tools_service.register_tool(
    "send_message",
    "Sends message to another agent",
    {
        "type": "object",
        "properties": {
            "agent_id": {
                "type": "string",
                "description": "Id of the agent"
            },
            "message": {
                "type": "string",
                "description": "Your message"
            },
            "conversation_id": {
                "type": "string",
                "description": "Conversation id, optional but required if protocol is specified"
            },
            "protocol": {
                "type": "string",
                "description": "Protocol name, optional"
            },
            "protocol_node_id": {
                "type": "string",
                "description": "Protocol node id, optional but required if protocol is specified"
            },
        }
    },
    send_message
)
tools_service.register_tool(
    "start_protocol",
    "Initiates protocol",
    {
        "type": "object",
        "properties": {
            "protocol_name": {
                "type": "string",
                "description": "Name of the protocol"
            },
        }
    },
    start_protocol
)

# create agents
myc_agent_a = MycAgent(
    address=Address("http://127.0.0.1:8001", "agent_a"),
    agent_platform=agent_platform,
    protocol_engine=protocol_engine
)
agent_a = Agent(
    id="agent_a",
    myc_agent=myc_agent_a,
    system_prompt='''
        # Mission
        You are an agent playing a role of a manager. You want to hire a contractor to do calculate the sum of 2 and 2.
        You can communicate with contractor using following protocols:
        - contract-net: you can use this protocol to allocate a task to a contractor

        # Your contact list
        This is a list of agents that you can contact:
        - agent_b

        # How protocols work
        Protocol is a set of rules that you can follow to communicate with other agents
        Protocols consists of nodes. Each node has a instruction and next nodes. Node represents a state of a conversation.
        You can only send messages that are allowed by the protocol. You can see allowed messages in the instruction.
        You must follow the instructions provided to you.
    ''',
    tools_service=tools_service,
    allowed_tools=["send_message", "start_protocol"]
)
myc_agent_b = MycAgent(
    address=Address("http://127.0.0.1:8001", "agent_b"),
    agent_platform=agent_platform,
    protocol_engine=protocol_engine
)
agent_b = Agent(
    id="agent_b",
    myc_agent=myc_agent_b,
    system_prompt='''
        # Mission
        You are an agent playing a role of a contractor. You may be contacted by a manager to do some work.
        Communication can be done through protocols.

        # How protocols work
        Protocol is a set of rules that you can follow to communicate with other agents
        Protocols consists of nodes. Each node has a instruction and next nodes. Node represents a state of a conversation.
        You can only send messages that are allowed by the protocol. You can see allowed messages in the instruction.
        You must follow the instructions provided to you.
    ''',
    tools_service=tools_service,
    allowed_tools=["send_message", "start_protocol"]
)

def get_agent_cb(agent: Agent):
    def agent_cb(sender: Address, message):
        offset = " " * 5
        if isinstance(message, ProtocolMessage):
            guiding_prompt = "\n".join([offset * 2 + line for line in message.guiding_prompt.splitlines()]) if message.guiding_prompt else ""
            # print(f"[{sender.name}]:")
            # print(offset + f"Protocol: {message.agent_message.protocol}")
            # print(offset + f"Protocol node id: {message.agent_message.current_protocol_node_id}")
            # print(offset + f"Guiding prompt:")
            # print(f"{guiding_prompt}")
            # print(offset + f"Message: {message.agent_message.content}")

            formatted_message = agent_to_agent_message_template.format(
                sender_id=sender.name,
                conversation_id=message.agent_message.conversation_id,
                protocol=message.agent_message.protocol,
                protocol_guide=message.guiding_prompt,
                message=message.agent_message.content
            )
            agent.send_message(formatted_message)
        elif isinstance(message, AgentMessage):
            # print(f"[{sender.name}]: {message.content}")
            formatted_message = agent_to_agent_message_template.format(
                sender_id=sender.name,
                conversation_id=message.conversation_id,
                protocol=message.protocol,
                protocol_guide="",
                message=message.content
            )
            agent.send_message(formatted_message)

    return agent_cb

myc_agent_a.register_callback(get_agent_cb(agent=agent_a))
myc_agent_b.register_callback(get_agent_cb(agent=agent_b))

agent_platform.register_agent(agent=myc_agent_a)
agent_platform.register_agent(agent=myc_agent_b)

agents["agent_a"] = agent_a
agents["agent_b"] = agent_b

agent_a.init()
agent_b.init()
agent_a.send_message("Begin")