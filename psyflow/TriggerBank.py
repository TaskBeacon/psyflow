from dataclasses import dataclass, field
from typing import Dict, Union
import yaml
@dataclass
class TriggerBank:
    triggers: Dict[str, int] = field(default_factory=dict)

    def get(self, event: str) -> Union[int, None]:
        """Get the trigger code (0–255) for a given event."""
        return self.triggers.get(event, None)

    def add(self, event: str, code: int):
        """Add a single event-code pair."""
        if not isinstance(code, int) or not (0 <= code <= 255):
            raise ValueError(f"Trigger code must be an int in range 0–255. Got: {code}")
        self.triggers[event] = code

    def add_from_dict(self, trigger_map: Dict[str, Union[int, list]]):
        """Add multiple event-code mappings from a dictionary."""
        for event, code in trigger_map.items():
            if isinstance(code, int):
                self.add(event, code)
            elif isinstance(code, list) and len(code) == 1 and isinstance(code[0], int):
                self.add(event, code[0])  # support list format like: key: [33]
            else:
                raise ValueError(f"Invalid code for event '{event}': {code}")

    def add_from_yaml(self, yaml_path: str):
        """Load triggers from a YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        triggers = data.get("triggers", {})
        self.add_from_dict(triggers)