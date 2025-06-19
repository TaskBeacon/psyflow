from psychopy import gui

class SubInfo:
    """
    GUI-based participant information collector using a YAML-style config.

    This class generates an input dialog based on a configurable field structure
    and provides basic localization and validation for different field types.

    Supported field types:
    - `string` : Free text input
    - `int` : Integer input with optional constraints
    - `choice` : Dropdown with options

    Attributes
    ----------
    subject_data : dict or None
        The result of `.collect()`, formatted with English field keys.
    """

    def __init__(self, config: dict):
        """
        Initialize with a config dictionary containing fields and optional mapping.

        Parameters
        ----------
        config : dict
            Configuration with required keys:
              - 'subinfo_fields': list of field definitions
              - 'subinfo_mapping': optional localization mapping
        """
        self.fields = config['subinfo_fields']
        self.field_map = config.get('subinfo_mapping', {})
        self.subject_data = None

        # Ensure default subject_id field
        if not any(f['name'] == 'subject_id' for f in self.fields):
            print("[SubInfo] WARNING: 'subject_id' field missing. Adding default.")
            self.fields.insert(0, {
                'name': 'subject_id',
                'type': 'int',
                'constraints': {'min': 101, 'max': 999, 'digits': 3}
            })
            self.field_map.setdefault('subject_id', 'Subject ID (3 digits)')

    def _local(self, key: str) -> str:
        """
        Translate a field key to the localized label if available.

        Parameters
        ----------
        key : str
            English identifier of a field or value.

        Returns
        -------
        str
            Localized label.
        """
        return self.field_map.get(key, key)

    def collect(self, exit_on_cancel: bool = True) -> dict:
        """
        Show a dialog to collect participant input. Loops until valid or cancelled.

        Parameters
        ----------
        exit_on_cancel : bool
            If True, exit the program if the user cancels input.

        Returns
        -------
        dict or None
            Cleaned response dictionary with English field keys,
            or None if cancelled and exit_on_cancel is False.

        Examples
        --------
        >>> cfg = {'subinfo_fields': [{'name': 'age', 'type': 'int'}]}
        >>> info = SubInfo(cfg)
        >>> info.collect(exit_on_cancel=False)
        """
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
                status = "success"
                success = True
                break

        if status == "cancelled":
            self.subject_data = None
            infoDlg = gui.Dlg()
            infoDlg.addText(self._local("registration_failed"))
            infoDlg.show()

            if exit_on_cancel:
                print("Participant cancelled — aborting experiment.")
                import sys
                sys.exit(0)
            return None

        if status == "success":
            self.subject_data = self._format_output(responses)
            infoDlg = gui.Dlg()
            infoDlg.addText(self._local("registration_successful"))
            infoDlg.show()
            return self.subject_data

    def validate(self, responses) -> bool:
        """
        Validate responses based on type and constraints.

        Parameters
        ----------
        responses : list
            Raw responses from the dialog.

        Returns
        -------
        bool
            True if all inputs are valid, False otherwise.
        """
        for i, field in enumerate(self.fields):
            val = responses[i]
            if field['type'] == 'string' or field['type'] == 'choice':
                if val is None or str(val).strip() == "":
                    infoDlg = gui.Dlg()
                    infoDlg.addText(
                        self._local("invalid_input").format(field=self._local(field['name'])))
                    infoDlg.show()
                    return False
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
                    infoDlg = gui.Dlg()
                    infoDlg.addText(
                        self._local("invalid_input").format(field=self._local(field['name']))
                    )
                    infoDlg.show()
                    return False
        return True

    def _format_output(self, responses) -> dict:
        """
        Convert localized user responses back to standard format.

        Parameters
        ----------
        responses : list
            Raw responses from the GUI.

        Returns
        -------
        dict
            Dictionary of English field keys and string values.
        """
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
