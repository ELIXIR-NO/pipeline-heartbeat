from datetime import datetime, timezone


class Component:
    def __init__(self, name, status, timestamp=None):
        # Instance variables with default values
        self.name = name
        self.status = status
        self.timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') if timestamp is None else timestamp

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "timestamp": self.timestamp
        }
