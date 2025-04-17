from psychopy import gui

class SubInfo:
    """
    Collects participant information via GUI based on a YAML config file.
    Supports multilingual labels and flexible field types.

    Supported field types:
        - string: Free text input
        - int: Integer input with optional min/max/digit constraints
        - choice: Dropdown menu with predefined options

    Language localization is supported via the `lang` block in YAML.
    Internal output is always standardized to English values.

    Attributes
    ----------
    subject_data : dict or None
        Stores the result of .collect()

    Example YAML structure:
    ------------------------
    fields:
      - name: subject_id
        type: int
        constraints:
          min: 101
          max: 199
          digits: 3

      - name: subject_name
        type: string

      - name: gender
        type: choice
        choices: [Male, Female]

    lang:
      zh:
        subject_id: "Subject ID"
        subject_name: "Subject Name"
        gender: "Gender"
        Male: "Male"
        Female: "Female"

    Example usage:
    --------------
    >>> with open("subject_fields.yaml") as f:
    ...     config = yaml.safe_load(f)
    >>> collector = ParticipantInfoCollector(config, language='zh')
    >>> subinfo = collector.collect()
    >>> print(subinfo)  # e.g., {'subject_id': '103', 'gender': 'Female'}
    >>> seed = collector.get_seed()  # e.g., 103
    """

    def __init__(self, config: dict):
        self.fields = config['subinfo_fields']
        self.field_map = config.get('subinfo_mapping', {})
        self.subject_data = None

        # --- Enforce subject_id field ---
        if not any(f['name'] == 'subject_id' for f in self.fields):
            print("[ParticipantInfoCollector] WARNING: 'subject_id' field missing in config. Adding default.")
            self.fields.insert(0, {
                'name': 'subject_id',
                'type': 'int',
                'constraints': {'min': 101, 'max': 999, 'digits': 3}
            })
            if 'subject_id' not in self.field_map:
                self.field_map['subject_id'] = 'Subject ID (3 digits)'
        
        

        if not any(f['name'] == 'session_name' for f in self.fields):
            print("[ParticipantInfoCollector] WARNING: 'session_name' field missing in config. Adding default.")
            self.fields.insert(0, {
                'name': 'session_name',
                'type': 'str'  
            })
            if 'session_name' not in self.field_map:
                self.field_map['session_name'] = 'Session Name'
       

    def _local(self, key: str):
        return self.field_map.get(key, key)

    def collect(self) -> dict:
        success = False
        responses = None

        while not success:
            dlg = gui.Dlg(title=self._local("Participant Information"))

            for field in self.fields:
                label = self._local(field['name'])
                if field['type'] == 'choice':
                    choices = [self._local(c) for c in field['choices']]
                    dlg.addField(label, choices=choices)
                else:
                    dlg.addField(label)

            responses = dlg.show()

            if responses is None:
                status = "cancelled"
                break

            if self.validate(responses):
                success = True
                status = "success"
                break

        if status == "cancelled":
            self.subject_data= None
            infoDlg=gui.Dlg()
            infoDlg.addText(self._local("registration_failed"))
            infoDlg.show()
            return self.subject_data

        if status == "success":
            self.subject_data = self._format_output(responses)
            infoDlg=gui.Dlg()
            infoDlg.addText(self._local("registration_successful"))
            infoDlg.show()
            return self.subject_data



    def validate(self, responses) -> bool:
        for i, field in enumerate(self.fields):
            val = responses[i]
            if field['type'] == 'int':
                try:
                    val = int(val)
                    min_val = field['constraints'].get('min')
                    max_val = field['constraints'].get('max')
                    digits = field['constraints'].get('digits')

                    if min_val is not None and val < min_val:
                        raise ValueError
                    if max_val is not None and val > max_val:
                        raise ValueError
                    if digits is not None and len(str(val)) != digits:
                        raise ValueError
                except:
                    erroDlg = gui.Dlg()
                    erroDlg.addText(self._local("invalid_input").format(field=self._local(field['name'])))
                    erroDlg.show()
                    return False
        return True

    def _format_output(self, responses) -> dict:
        result = {}
        for i, field in enumerate(self.fields):
            raw = responses[i]
            if field['type'] == 'choice':
                for original in field['choices']:
                    if self._local(original) == raw:
                        raw = original
                        break
            result[field['name']] = str(raw)
        return result
