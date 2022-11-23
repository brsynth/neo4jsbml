from typing import Any, Dict, List

import neo4j


class Relationship(object):
    """Relation. """

    def __init__(self, left: str, left_id: str, right: str, right_id: str, relationship: str, attributes: Dict[Any, Any] = {}) -> None:
        self.left = left
        self.left_id = left_id
        self.right = right
        self.right_id = right_id
        self.relationship = relationship
        self.attributes = attributes

    def to_list(self) -> List[Any]:
        return [self.left, self.left_id, self.relationship, self.right, self.right_id, self.attributes]
