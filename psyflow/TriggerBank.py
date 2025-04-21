from dataclasses import dataclass, field
from typing import Dict, Union
import yaml

@dataclass
class TriggerBank:
    """
    A container for mapping event labels to trigger codes (0–255).

    Supports adding mappings manually, from dicts, or from YAML files.
    Typically used with a TriggerSender to manage EEG/MEG event triggers.
    """

    triggers: Dict[str, int] = field(default_factory=dict)

    def get(self, event: str) -> Union[int, None]:
        """
        Retrieve the trigger code for a given event.

        Parameters
        ----------
        event : str
            Name of the event.

        Returns
        -------
        int or None
            The corresponding trigger code (0–255) or None if not found.
        """
        return self.triggers.get(event, None)

    def add(self, event: str, code: int):
        """
        Add a single event-to-code mapping.

        Parameters
        ----------
        event : str
            Event name.
        code : int
            Integer code between 0 and 255.

        Raises
        ------
        ValueError
            If code is not an int in the allowed range.
        """
        if not isinstance(code, int) or not (0 <= code <= 255):
            raise ValueError(f"Trigger code must be an int in range 0–255. Got: {code}")
        self.triggers[event] = code

    def add_from_dict(self, trigger_map: Dict[str, Union[int, list]]):
        """
        Add multiple trigger codes from a dictionary.

        Parameters
        ----------
        trigger_map : dict
            Dictionary with keys as event names and values as ints or single-item lists.
        """
        for event, code in trigger_map.items():
            if isinstance(code, int):
                self.add(event, code)
            elif isinstance(code, list) and len(code) == 1 and isinstance(code[0], int):
                self.add(event, code[0])  # YAML support: key: [33]
            else:
                raise ValueError(f"Invalid code for event '{event}': {code}")

    def add_from_yaml(self, yaml_path: str):
        """
        Load event triggers from a YAML file with a `triggers:` block.

        Parameters
        ----------
        yaml_path : str
            Path to the YAML file.
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        triggers = data.get("triggers", {})
        self.add_from_dict(triggers)