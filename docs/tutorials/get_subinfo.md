## 🧾 SubInfo: Participant Information Collector

`SubInfo` is a flexible and localizable class for collecting subject information using GUI dialogs. It supports field definitions from YAML or Python dictionaries, and is useful for creating standardized subject registration forms.

### 🧵 Summary of Key Methods 

| Purpose                      | Method            |
|--|-|
| Collect participant info    | `.collect()`      |
| Access result               | `.subject_data`   |
| Validate responses          | `.validate()`     |
| Format output               | `._format_output()` |
| Localization helper         | `._local(key)`    |

### 1. Configuration Format (YAML)

Here's an example YAML you might use:

    subinfo_fields:
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

    subinfo_mapping:
      subject_id: "编号"
      subject_name: "姓名"
      gender: "性别"
      Male: "男"
      Female: "女"
      registration_successful: "注册成功！"
      registration_failed: "注册取消。"
      invalid_input: "无效的输入：{field}"



### 2. Collecting Subject Info

    import yaml
    from your_package import SubInfo

    with open("subinfo.yaml", "r") as f:
        config = yaml.safe_load(f)

    collector = SubInfo(config)
    info = collector.collect()

    if info is not None:
        print("Collected Info:", info)
    else:
        print("Registration was cancelled.")

Example output:

    Collected Info: {'subject_id': '103', 'subject_name': 'Li Hua', 'gender': 'Female'}



### 3. How It Works

- Uses `psychopy.gui.Dlg` to build the form.
- Supports text, integer (with min/max/digits), and dropdown fields.
- Automatically adds `subject_id` and `session_name` if missing.
- Displays localized labels and messages using `subinfo_mapping`.



### 4. Validation Behavior

- Integer fields are validated for range and digit length.
- Any failure will prompt an error dialog and restart the input form.
- Successful entries return a clean dictionary with English keys.



### 5. Localization (Optional)

The `subinfo_mapping` block maps internal field names and values to display labels in any language. You can also override default system messages like:

- `"registration_successful"`
- `"registration_failed"`
- `"invalid_input"`


This class helps unify your experimental metadata collection pipeline with minimal boilerplate. You can reuse the same config across experiments and localize it for different participant groups.

### 6. Realistic Example
```python
with open('config/config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 2. collect subject info
subform_config = {
    'subinfo_fields': config.get('subinfo_fields', []),
    'subinfo_mapping': config.get('subinfo_mapping', {})
}

subform = SubInfo(subform_config)
subject_data = subform.collect()
if subject_data is None:
    print("Participant cancelled — aborting experiment.")
    sys.exit(0)
```