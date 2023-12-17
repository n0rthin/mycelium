from typing import Optional 

class AgentMessage():
    # the actual information or data being communicated. This could be a command, a query, a statement, etc.
    content: any
    # an identifier used to associate this message with a conversation or a dialogue between agents. This helps in tracking and managing multi-message exchanges.
    conversation_id: Optional[str]
    # this optional field specifies the interaction protocol that the message adheres to
    protocol: Optional[str]
    # this optional field specifies the node in the interaction protocol that the message adheres to
    current_protocol_node_id: Optional[str]
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

    def __init__(self, content: any, conversation_id: Optional[str] = None, protocol: Optional[str] = None, current_protocol_node_id: Optional[str] = None, message_id: Optional[str] = None, reply_to: Optional[str] = None, in_reply_to: Optional[str] = None, reply_by: Optional[str] = None, language: Optional[str] = None):
        self.content = content
        self.conversation_id = conversation_id
        self.protocol = protocol
        self.current_protocol_node_id = current_protocol_node_id
        self.message_id = message_id
        self.reply_to = reply_to
        self.in_reply_to = in_reply_to
        self.reply_by = reply_by
        self.language = language

