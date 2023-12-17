from typing import Optional

class Protocol:
    def __init__(self, definition: dict):
        self.name = definition.get("name")
        self.version = definition.get("version")
        self.roles = definition.get("roles")
        self.first_node_ids = definition.get("first_node_ids")
        self.nodes = definition.get("nodes")
        # TODO: validate protocol on initialization

    def get_next_nodes(self, current_node_id: Optional[str] = None):
        if current_node_id is None:
            return [self.get_node_by_id(node_id) for node_id in self.first_node_ids]

        current_node = self.get_node_by_id(current_node_id)
        if current_node["next_node_ids"] is None:
            return []
        
        return [self.get_node_by_id(node_id) for node_id in current_node["next_node_ids"]]
    
    def get_node_by_id(self, id):
        for node in self.nodes:
            if node['node_id'] == id:
                return node
        return None


