# SubInfo: Collecting Participant Information

## Overview

The `SubInfo` class provides a flexible and user-friendly way to collect participant information at the beginning of an experiment. It creates standardized GUI dialogs that can be customized through configuration files, supporting multiple field types and localization for international studies.

`SubInfo` solves several common challenges in participant registration:

- **Standardization**: Create consistent participant information forms across experiments
- **Validation**: Automatically validate input based on field constraints
- **Localization**: Display forms in the participant's language
- **Configuration**: Define forms using YAML or dictionaries for easy modification
- **Integration**: Seamlessly connect with other psyflow components

## Key Features

| Feature | Description |
|---------|-------------|
| Multiple field types | Support for string, integer, and choice (dropdown) fields |
| Input validation | Enforce constraints like min/max values and digit length |
| Localization | Display field labels and messages in any language |
| YAML configuration | Define forms using human-readable configuration files |
| Automatic defaults | Add standard fields like subject_id if not specified |
| Error handling | Clear error messages for invalid input |

## Quick Reference

| Purpose | Method | Example |
|---------|--------|--------|
| Initialize | `SubInfo(config)` | `subinfo = SubInfo(config)` |
| Collect info | `.collect()` | `data = subinfo.collect()` |
| Access data | `.subject_data` | `subject_id = subinfo.subject_data['subject_id']` |
| Validate input | `.validate()` | `is_valid = subinfo.validate()` |

## Detailed Usage Guide

### 1. Configuring the Form

#### Option A: Using a YAML Configuration

YAML provides a clean, readable way to define your form structure:

```yaml
# subinfo_config.yaml
subinfo_fields:
  - name: subject_id
    type: int
    constraints:
      min: 101
      max: 999
      digits: 3

  - name: age
    type: int
    constraints:
      min: 18
      max: 100

  - name: gender
    type: choice
    choices: [Male, Female, Non-binary, Prefer not to say]

  - name: handedness
    type: choice
    choices: [Right, Left, Ambidextrous]

  - name: vision
    type: choice
    choices: [Normal, Corrected-to-normal, Impaired]

# Optional localization mapping
subinfo_mapping:
  subject_id: "Participant ID"
  age: "Age"
  gender: "Gender"
  handedness: "Handedness"
  vision: "Vision"
  Male: "Male"
  Female: "Female"
  Non-binary: "Non-binary"
  Prefer not to say: "Prefer not to say"
  Right: "Right"
  Left: "Left"
  Ambidextrous: "Ambidextrous"
  Normal: "Normal"
  Corrected-to-normal: "Corrected-to-normal"
  Impaired: "Impaired"
  registration_successful: "Registration successful!"
  registration_failed: "Registration cancelled."
  invalid_input: "Invalid input for {field}"
```

#### Option B: Using a Python Dictionary

You can also define the form directly in Python:

```python
config = {
    "subinfo_fields": [
        {
            "name": "subject_id",
            "type": "int",
            "constraints": {"min": 101, "max": 999, "digits": 3}
        },
        {
            "name": "age",
            "type": "int",
            "constraints": {"min": 18, "max": 100}
        },
        {
            "name": "gender",
            "type": "choice",
            "choices": ["Male", "Female", "Non-binary", "Prefer not to say"]
        },
        {
            "name": "handedness",
            "type": "choice",
            "choices": ["Right", "Left", "Ambidextrous"]
        }
    ],
    "subinfo_mapping": {
        "subject_id": "Participant ID",
        "age": "Age",
        "gender": "Gender",
        "handedness": "Handedness"
        # Add more mappings as needed
    }
}
```

### 2. Field Types and Constraints

`SubInfo` supports three field types:

#### String Fields

```yaml
- name: subject_name
  type: string
```

String fields accept any text input without validation.

#### Integer Fields

```yaml
- name: subject_id
  type: int
  constraints:
    min: 101      # Minimum allowed value
    max: 999      # Maximum allowed value
    digits: 3     # Required number of digits
```

Integer fields validate that:
- The input can be converted to an integer
- The value is within the min/max range (if specified)
- The number has exactly the specified number of digits (if specified)

#### Choice Fields (Dropdowns)

```yaml
- name: condition
  type: choice
  choices: [Control, Experimental]
```

Choice fields present a dropdown menu with the specified options.

### 3. Collecting Participant Information

Once you've defined your configuration, collecting information is straightforward:

```python
from psyflow import SubInfo
import yaml

# Load configuration from YAML
with open("subinfo_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create SubInfo instance
subinfo = SubInfo(config)

# Show dialog and collect information
subject_data = subinfo.collect()

# Check if user cancelled
if subject_data is None:
    print("User cancelled the form")
    # Handle cancellation (e.g., exit experiment)
else:
    print("Collected information:", subject_data)
    # Continue with experiment using the collected data
```

### 4. Localization

For international studies, you can localize the form by providing translations in the `subinfo_mapping` section:

```yaml
# Example for Chinese localization
subinfo_mapping:
  subject_id: "参与者编号"
  age: "年龄"
  gender: "性别"
  Male: "男"
  Female: "女"
  Non-binary: "非二元性别"
  Prefer not to say: "不愿透露"
  registration_successful: "注册成功！"
  registration_failed: "注册取消。"
  invalid_input: "无效的输入：{field}"
```

The form will display these translated labels while still using the English keys internally for consistency.

### 5. Integration with TaskSettings

`SubInfo` works seamlessly with `TaskSettings` for complete experiment configuration:

```python
from psyflow import SubInfo, TaskSettings
import yaml

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create SubInfo and collect participant data
subinfo_config = {
    "subinfo_fields": config.get("subinfo_fields", []),
    "subinfo_mapping": config.get("subinfo_mapping", {})
}
subinfo = SubInfo(subinfo_config)
subject_data = subinfo.collect()

if subject_data is None:
    print("Experiment cancelled")
    import sys
    sys.exit(0)

# Create TaskSettings with the collected subject info
settings = TaskSettings.from_dict(config.get("task", {}))
settings.add_subinfo(subject_data)

# Now you have subject-specific paths and seeds
print(f"Data will be saved to: {settings.res_file}")
print(f"Using block seed: {settings.block_seed}")
```

## Complete Example

Here's a complete example showing how to use `SubInfo` in an experiment:

```python
from psychopy import visual, core
from psyflow import SubInfo, TaskSettings
import yaml
import sys

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Step 1: Collect participant information
subinfo_config = {
    "subinfo_fields": config.get("subinfo_fields", []),
    "subinfo_mapping": config.get("subinfo_mapping", {})
}
subinfo = SubInfo(subinfo_config)
subject_data = subinfo.collect()

if subject_data is None:
    print("Experiment cancelled")
    sys.exit(0)

# Step 2: Configure task settings
task_config = {
    **config.get("window", {}),
    **config.get("task", {}),
    **config.get("timing", {})
}
settings = TaskSettings.from_dict(task_config)
settings.add_subinfo(subject_data)

# Step 3: Create PsychoPy window
win = visual.Window(
    size=settings.window_size,
    fullscr=settings.fullscreen,
    color=settings.bg_color,
    units="deg"
)

# Step 4: Show welcome message with participant info
welcome_text = f"Welcome, Participant {subject_data['subject_id']}!\n\n"
welcome_text += f"Age: {subject_data.get('age', 'N/A')}\n"
welcome_text += f"Gender: {subject_data.get('gender', 'N/A')}\n\n"
welcome_text += "Press any key to begin the experiment."

welcome = visual.TextStim(win, text=welcome_text, height=0.8)
welcome.draw()
win.flip()

# Wait for keypress
from psychopy.event import waitKeys
waitKeys()

# Continue with experiment...
win.close()
core.quit()
```

## Advanced Usage

### Custom Validation

You can extend `SubInfo` with custom validation logic:

```python
class CustomSubInfo(SubInfo):
    def validate(self):
        # First run the standard validation
        if not super().validate():
            return False
            
        # Add custom validation logic
        if 'subject_id' in self.subject_data and 'group' in self.subject_data:
            subject_id = int(self.subject_data['subject_id'])
            group = self.subject_data['group']
            
            # Check if subject_id is valid for the selected group
            if group == 'Control' and not (100 <= subject_id < 200):
                self._show_error("Control group IDs must be between 100-199")
                return False
            elif group == 'Experimental' and not (200 <= subject_id < 300):
                self._show_error("Experimental group IDs must be between 200-299")
                return False
                
        return True
```

### Programmatic Form Creation

You can also create forms programmatically:

```python
def create_dynamic_form(experiment_type):
    """Create a form based on experiment type."""
    base_fields = [
        {"name": "subject_id", "type": "int", "constraints": {"min": 100, "max": 999}}
    ]
    
    if experiment_type == "behavioral":
        base_fields.extend([
            {"name": "age", "type": "int"},
            {"name": "gender", "type": "choice", "choices": ["Male", "Female", "Other"]}
        ])
    elif experiment_type == "eeg":
        base_fields.extend([
            {"name": "cap_size", "type": "choice", "choices": ["Small", "Medium", "Large"]},
            {"name": "impedance_check", "type": "choice", "choices": ["Pass", "Fail"]}
        ])
    
    config = {"subinfo_fields": base_fields}
    return SubInfo(config)

# Usage
form = create_dynamic_form("eeg")
data = form.collect()
```

## Best Practices

1. **Keep forms concise**: Only collect information that's necessary for your experiment.

2. **Use meaningful field names**: Choose descriptive names that match your data analysis variables.

3. **Set appropriate constraints**: Use min/max and digit constraints to prevent data entry errors.

4. **Provide clear labels**: Use the mapping dictionary to make field labels clear and understandable.

5. **Handle cancellation gracefully**: Always check if `collect()` returns `None` and handle it appropriately.

6. **Store configurations externally**: Keep form definitions in YAML files for easy modification without changing code.

7. **Test with different languages**: If using localization, test the form with all supported languages.

## Troubleshooting

- **Form doesn't appear**: Ensure PsychoPy is properly installed and can create GUI elements.

- **Validation errors**: Check that your constraints are reasonable and that field types match expected input.

- **Missing fields**: Verify that your configuration dictionary has the correct structure.

- **Localization issues**: Ensure all keys in `subinfo_mapping` match field names and choice options exactly.

## Next Steps

Now that you understand how to use `SubInfo`, you can:

- Learn about [TaskSettings](task_settings.md) for configuring your experiment
- Explore [StimBank](build_stimulus.md) for managing stimuli
- Check out [BlockUnit](build_blocks.md) for organizing trials into blocks
- See [StimUnit](build_trialunit.md) for creating individual trials