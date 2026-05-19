import json
from datetime import datetime
from typing import Any, Dict, Optional

class Packet:
    def __init__(self, type: str, payload: Dict[str, Any], timestamp: Optional[str] = None):
        self.type = type
        self.payload = payload
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "payload": self.payload,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'Packet':
        data = json.loads(json_str)
        return cls(
            type=data["type"],
            payload=data["payload"],
            timestamp=data.get("timestamp")
        )

    def __repr__(self):
        return f"<Packet type={self.type} timestamp={self.timestamp}>"
