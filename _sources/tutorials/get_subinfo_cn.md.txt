# SubInfo: 收集被试信息

## 概述

`SubInfo` 是 `psyflow` 中用于在实验开始前通过一个简单的图形用户界面（GUI）表单收集被试信息的模块。它被设计用来：

-   动态地从 `config.yaml` 文件生成一个输入表单。
-   支持多种语言的标签和字段。
-   验证输入以确保数据完整性。
-   将收集到的信息作为字典返回，以便于保存和使用。

这个模块取代了 PsychoPy 内置的 `gui.DlgFromDict`，提供了一个更现代化、更灵活且与 `psyflow` 生态系统完全集成的解决方案。

## 核心概念

`SubInfo` 的工作流程很简单：

1.  **配置**: 您在 `config.yaml` 中定义表单的字段和它们在不同语言中的标签。
2.  **调用**: 您调用 `SubInfo.get()` 函数，它会显示 GUI 表单。
3.  **收集**: 被试填写表单并点击“确定”。
4.  **返回**: 函数返回一个包含被试信息的字典。如果被试点击“取消”，实验将优雅地退出。

## 详细使用指南

### 1. 在 `config.yaml` 中配置表单

GUI 表单是在您的 `config/config.yaml` 文件中定义的。您需要指定两个部分：`subinfo_fields` 和 `subinfo_mapping`。

-   `subinfo_fields`: 一个您想要在表单中包含的字段名称的列表。
-   `subinfo_mapping`: 一个字典，将这些字段名称映射到您想要为每种支持的语言显示的标签。

**示例 `config.yaml`:**
```yaml
# ---------------------------------------------------------------------------- #
#                              被试信息表单配置                              #
# ---------------------------------------------------------------------------- #
subinfo_fields:
  - id
  - age
  - gender
  - session
  - language

subinfo_mapping:
  # 英语标签
  en:
    id: "Participant ID"
    age: "Age"
    gender: "Gender"
    session: "Session"
    language: "Language"
  # 中文标签
  cn:
    id: "被试ID"
    age: "年龄"
    gender: "性别"
    session: "阶段"
    language: "语言"
  # 韩语标签
  kr:
    id: "참가자 ID"
    age: "나이"
    gender: "성별"
    session: "세션"
    language: "언어"
```

在这个例子中，表单将有五个字段。根据选择的语言，标签将相应地改变。

### 2. 调用 `SubInfo.get()`

在您的主实验脚本中，在任何其他操作之前调用 `SubInfo.get()`。

```python
from psyflow.subinfo import SubInfo
import yaml

# 通常，您会从您的 config.yaml 加载这些
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

fields = config['subinfo_fields']
mapping = config['subinfo_mapping']

# 调用 get() 来显示表单
# 它会首先询问语言
sub_info = SubInfo.get(fields, mapping)

# 如果被试点击“取消”，sub_info 将是 None，程序将退出。
# 否则，它是一个包含他们输入的字典。
# {'id': '001', 'age': '25', 'gender': 'Female', 'session': '1', 'language': 'en'}
```

### 3. 语言选择

`SubInfo.get()` 的一个关键特性是它内置的语言选择。

1.  当您调用 `SubInfo.get()` 时，它首先会显示一个语言选择对话框。这个对话框的选项是根据您在 `subinfo_mapping` 中定义的语言（`en`, `cn`, `kr` 等）自动生成的。

    ![语言选择对话框](https://raw.githubusercontent.com/Xh-Hypnos/psyflow/main/docs/tutorials/figures/subinfo_yaml.png)

2.  一旦被试选择了一种语言并点击“确定”，`SubInfo` 就会使用该语言的相应标签来呈现主输入表单。

    ![英文表单](https://raw.githubusercontent.com/Xh-Hypnos/psyflow/main/docs/tutorials/figures/subinfo_yaml.png)
    ![中文表单](https://raw.githubusercontent.com/Xh-Hypnos/psyflow/main/docs/tutorials/figures/subinfo_yaml_cn.png)

### 4. 输入验证

`SubInfo` 会执行基本的输入验证。在上面的例子中，`id` 和 `session` 字段是必需的。如果被试将它们留空并尝试点击“确定”，这些字段将以红色高亮显示，提示他们需要填写这些字段。

![验证失败](https://raw.githubusercontent.com/Xh-Hypnos/psyflow/main/docs/tutorials/figures/subinfo_failed.png)

验证是基于字段名称的：
-   如果一个字段的名称包含 `id` 或 `session`，它被认为是必需的。
-   所有其他字段都是可选的。

### 5. 使用返回的数据

`SubInfo.get()` 返回一个字典，其中键是 `subinfo_fields` 中的字段名称，值是被试的输入。您可以使用这个字典来：

-   为您的数据文件创建一个唯一的、信息丰富的文件名。
-   在您的实验中存储被试的人口统计信息。
-   根据会话编号或语言改变实验逻辑。

**示例用法:**
```python
# 从 SubInfo 获取被试信息
sub_info = SubInfo.get(fields, mapping)

# 如果用户点击了取消，则 sub_info 将为 None
if sub_info is None:
    print("实验被用户取消。")
    # core.quit() 会被自动调用

# 创建一个文件名
output_filename = f"sub-{sub_info['id']}_ses-{sub_info['session']}_task-stroop_data.csv"

# 将被试信息添加到您的数据记录中
trial_data['participant_id'] = sub_info['id']
trial_data['age'] = sub_info['age']

print(f"数据将保存到: {output_filename}")
```

通过使用 `SubInfo`，您可以确保在实验开始时以一种用户友好和健壮的方式收集到干净、结构化的被试信息。
