# TaskSettings: 配置您的实验

## 概述

`TaskSettings` 类提供了一种集中管理实验配置的方式，包括收集的被试信息、数据路径、计时参数、窗口设置等。它有助于标准化实验设置，并确保在实验的不同部分配置一致。

在底层，`TaskSettings` 在您的代码中随处可见，无论您需要读取还是写入实验参数。例如：
- 在 `run_trial.py` 中，检索特定刺激的持续时间
- 在 `main.py` 中创建块时，确定块和试验的数量，并为条件的随机化提供种子

## 主要功能

| 功能 | 描述 |
|---|---|
| 字典初始化 | 从 Python 字典或 YAML 文件创建设置 |
| 被试整合 | 整合收集的被试信息，用于每个被试的种子、文件名和路径 |
| 路径和目录生成 | 自动创建输出目录并构建带时间戳的日志/CSV/JSON 路径 |
| 种子管理 | 灵活的种子策略（`same_across_sub` 或 `same_within_sub`），并自动生成每个块的种子 |
| 动态扩展 | 通过 `from_dict()` 加载额外的、未知的配置键 |
| JSON 导出 | 将完整的 `TaskSettings` 保存到 JSON（`save_to_json()`）以进行归档或分析 |
| 人类可读的 repr | 清晰的 `__repr__()`，便于检查或记录所有当前设置 |
| 默认值 | 为窗口、计时、块/试验、按键等提供合理的内置默认值 |

## 快速参考

| 目的 | 方法 | 示例 |
|---|---|---|
| 从字典初始化 | `TaskSettings.from_dict(config)` | `settings = TaskSettings.from_dict(config)` |
| 添加被试信息 | `.add_subinfo(subject_data)` | `settings.add_subinfo(subject_data)` |
| 访问设置 | 点表示法 | `settings.size` |
| 获取所有设置 | `.to_dict()` | `all_settings = settings.to_dict()` |

## 详细使用指南

### 1. 创建 TaskSettings

#### 选项 A：从 YAML 文件

1.  在 `config.yaml` 中**定义**单独的部分：
   ```yaml
   window:
     size: [1920, 1080]
     fullscreen: true
     units: "deg"
     bg_color: "gray"

   task:
     task_name: "stroop"
     total_blocks: 2
     total_trials: 40
     conditions: ["congruent","incongruent"]
     key_list: ["space"]
     seed_mode: "same_across_sub"

   timing:
     fixation_duration: [0.5, 0.7]
     cue_duration: 0.3
     stimulus_duration: 1.0
     feedback_duration: 0.5
   ```
2.  **加载**并**扁平化**：
   ```python
   import yaml
   from psyflow import TaskSettings

   with open('config.yaml', 'r') as f:
       cfg = yaml.safe_load(f)

   merged = {**cfg.get('window', {}), **cfg.get('task', {}), **cfg.get('timing', {})}
   settings = TaskSettings.from_dict(merged)
   ```

> **注意：** `window`、`task` 和 `timing` 是 `TaskSettings` 的主要部分。它们必须被扁平化为一个传递给 `from_dict()` 的字典。其他配置（例如 `triggers`、`controllers`）可以作为嵌套属性添加：
>
> ```python
> settings.triggers = cfg['trigger_config']
> ```
>
> `load_config()` 实用程序通常会自动将 `window`、`task` 和 `timing` 扁平化到 `cfg['task_config']` 中，因此您可以直接初始化：
>
> ````python
> cfg = load_config('config.yaml')
> settings = TaskSettings.from_dict(cfg['task_config'])
> ````

#### 选项 B：从字典

您可以通过两种方式直接从 Python 字典初始化 `TaskSettings`：

1.  **扁平字典**：将所有参数（包括自定义字段）合并到一个字典中。
2.  **嵌套部分**：将逻辑子部分（例如 `window`、`task`、`timing`）保留为嵌套字典，然后在调用时扁平化。

**示例 YAML 部分**（作为参考）：

```yaml
window:
  size: [1920, 1080]
  fullscreen: true
  units: "deg"
  bg_color: "gray"

task:
  task_name: "stroop"
  total_blocks: 2
  total_trials: 40
  conditions: ["congruent", "incongruent"]
  key_list: ["space"]
  seed_mode: "same_across_sub"

timing:
  fixation_duration: [0.5, 0.7]
  cue_duration: 0.3
  stimulus_duration: 1.0
  feedback_duration: 0.5
```

##### 1. 扁平字典方法

```python
from psyflow import TaskSettings

# 将所有设置合并到一个字典中
config_flat = {
    # 窗口设置
    'size': [1920, 1080],
    'fullscreen': True,
    'units': 'deg',
    'bg_color': 'gray',

    # 任务设置
    'task_name': 'stroop',
    'total_blocks': 2,
    'total_trials': 40,
    'conditions': ['congruent', 'incongruent'],
    'key_list': ['space'],
    'seed_mode': 'same_across_sub',

    # 计时设置
    'fixation_duration': [0.5, 0.7],
    'cue_duration': 0.3,
    'stimulus_duration': 1.0,
    'feedback_duration': 0.5,

    # 自定义嵌套字段
    'trigger_config': {'onset': 5, 'offset': 6}
}

settings = TaskSettings.from_dict(config_flat)
print(settings)
print('Trigger:', settings.trigger_config)
```

##### 2. 嵌套字典方法

```python
from psyflow import TaskSettings

# 为可读性保留嵌套部分
config_nested = {
    'window': {
        'size': [1920, 1080],
        'fullscreen': True,
        'units': 'deg',
        'bg_color': 'gray'
    },
    'task': {
        'task_name': 'stroop',
        'total_blocks': 2,
        'total_trials': 40,
        'conditions': ['congruent', 'incongruent'],
        'key_list': ['space'],
        'seed_mode': 'same_across_sub'
    },
    'timing': {
        'fixation_duration': [0.5, 0.7],
        'cue_duration': 0.3,
        'stimulus_duration': 1.0,
        'feedback_duration': 0.5
    },
    'trigger_config': {
        'onset': 5,
        'offset': 6
    }
}

# 初始化时扁平化嵌套部分
config_flat = {
    **config_nested['window'],
    **config_nested['task'],
    **config_nested['timing'],
    'trigger_config': config_nested['trigger_config']
}

settings = TaskSettings.from_dict(config_flat)
print(settings.conditions)
print(settings.fixation_duration)
print(settings.trigger_config)
```

在这两种情况下，`from_dict()` 都会应用已知字段，并将未知键（如 `trigger_config`）作为 `settings` 对象的属性附加。

### 2. 添加被试信息

提供一个至少包含 `subject_id`（其他可选）的字典，以：

- 验证输入
- 派生特定于被试的种子（在 `same_within_sub` 模式下）
- 创建输出目录
- 构建带时间戳的文件名

```python
subinfo = {'subject_id': 'S01', 'age': 24, 'gender': 'F'}
settings.add_subinfo(subinfo)
```

### 3. 路径管理

在 `add_subinfo()` 之后，将设置以下属性：

| 属性 | 描述 |
|---|---|
| `save_path` | 基本目录（默认为 `./data`） |
| `log_file` | PsychoPy 日志的 `.log` 文件的完整路径 |
| `res_file` | 包含试验级结果的 `.csv` 文件的完整路径 |
| `json_file` | 转储所有设置的 `.json` 文件的完整路径 |

调用 `settings.add_subinfo(subinfo)` 后，您将看到控制台输出和生成的文件路径：

```python
settings.add_subinfo(subinfo)
# [INFO] Created output directory: ./data

print('Log file:', settings.log_file)
# Log file: ./data/sub-S01_task_flanker_20250706_094730.log

print('Results file:', settings.res_file)
# Results file: ./data/sub-S01_task_flanker_20250706_094730.csv

print('Config JSON file:', settings.json_file)
# Config JSON file: ./data/sub-S01_task_flanker_20250706_094730.json
```

**示例目录布局**：

```
./data/
└─ S01/
   ├─ sub-S01_task-stroop_20250706_091500.log
   ├─ sub-S01_task-stroop_20250706_091500.csv
   └─ sub-S01_task-stroop_20250706_091500.json
```

### 4. 种子管理

`TaskSettings` 使用三个相关字段来控制随机化和可复现性：

- `overall_seed`（整数，默认 2025）：用于生成特定于块的种子的基本种子。在您的配置中或在运行时更改此值以改变整体随机化模式。
- `block_seed`（整数列表或 `None`）：每个块一个种子，用于初始化块级随机化（例如，洗牌条件顺序）。如果未设置，则根据 `overall_seed` 和 `seed_mode` 自动生成种子。
- `seed_mode`（`"same_across_sub"` 或 `"same_within_sub"`）：确定块种子是在参与者之间共享还是为每个被试个性化。

#### 控制每个块的条件顺序

`block_seed` 中的每个条目都为该块的随机数生成器（RNG）提供种子。通过为每个块分配一个特定的种子，您可以确保：

1.  **确定性洗牌：** 在块 *n* 中洗牌 `settings.conditions` 的顺序完全由 `block_seed[n]` 决定。
2.  **可复现的块：** 使用相同的种子重新运行实验将重新创建相同的块级条件顺序。

示例：

```python
import random
for i, seed in enumerate(settings.block_seed):
    rng = random.Random(seed)
    block_order = settings.conditions.copy()
    rng.shuffle(block_order)
    print(f"Block {i+1} order:", block_order)
```

#### 如何覆盖种子

- **通过配置**：在初始化之前在您的字典或 YAML 中设置 `overall_seed`：
  ```python
  config = {'overall_seed': 9999, 'seed_mode': 'same_across_sub', ...}
  settings = TaskSettings.from_dict(config)
  ```
- **在运行时**：从新的基础重新生成块种子：
  ```python
  settings.set_block_seed(123456)
  print('New block seeds:', settings.block_seed)
  ```

#### 选择种子模式

- `same_across_sub`（默认）
  所有参与者共享从 `overall_seed` 生成的相同 `block_seed` 列表。当您需要在整个组中进行相同的块随机化时（例如，在队列级别进行平衡），请使用此模式。

- `same_within_sub`
  每个被试都会收到一组从其 `subject_id` 派生的唯一块种子，从而确保可复现但个性化的随机化。此方法：

  - **可复现性：** 允许从任何被试的 ID 精确重建其实验序列。
  - **分布式顺序效应：** 当不需要组级一致性时，在参与者之间改变块顺序。

> **注意：** 最终的 `block_seed` 列表存储在 `settings` 对象中，并包含在 `save_to_json()` 生成的 JSON 文件中。这使得调试和事后分析变得透明，因为您可以确切地看到每个块使用了哪些种子。

### 5. 访问设置

许多 psyflow 实用程序和您的自定义试验函数将直接从 `settings` 对象中读取值。使用 Python 的属性访问（或 `getattr`）来获取显示参数、计时值和自定义触发器，而无需样板代码。

#### 窗口和监视器设置

许多实验使用相同的监视器和窗口设置。以下是从 `settings` 应用这些值的两种方法：

**示例 1：直接点属性访问**

```python
from psychopy import monitors, visual

# 点访问假定属性存在
mon = monitors.Monitor('tempMonitor')
mon.setWidth(settings.monitor_width_cm)
mon.setDistance(settings.monitor_distance_cm)
mon.setSizePix(settings.size)

win = visual.Window(
    size=settings.size,
    fullscr=settings.fullscreen,
    screen=settings.screen,
    monitor=mon,
    units=settings.units,
    color=settings.bg_color,
    gammaErrorPolicy='ignore'
)
```

**示例 2：使用 `getattr` 安全访问**

```python
from psychopy import monitors, visual

# getattr 在字段丢失时提供回退
mon = monitors.Monitor('tempMonitor')
mon.setWidth(getattr(settings, 'monitor_width_cm', 60))
mon.setDistance(getattr(settings, 'monitor_distance_cm', 65))
mon.setSizePix(getattr(settings, 'size', [1024, 768]))

win = visual.Window(
    size=getattr(settings, 'size', [1024, 768]),
    fullscr=getattr(settings, 'fullscreen', False),
    screen=getattr(settings, 'screen', 0),
    monitor=mon,
    units=getattr(settings, 'units', 'pix'),
    color=getattr(settings, 'bg_color', [0, 0, 0]),
    gammaErrorPolicy='ignore'
)
```

> **提示：** 使用 `getattr(settings, 'attr', default)` 允许您在设置可能不存在时指定回退。

#### 在 `run_trial.py` 中访问计时和触发器

以下是一个简洁的代码片段，展示了如何在您的试验代码中从 `settings` 中获取计时值和起始触发器：

```python
# run_trial.py (简洁)
def run_trial(settings, stim_bank, condition):
    # 检索提示持续时间和起始触发器
    duration = settings.cue_duration
    trigger  = settings.triggers.get(f"{condition}_cue_onset")

    # 呈现提示刺激
    cue_stim = stim_bank.get(f"{condition}_cue")
    cue_stim.show(duration=duration, onset_trigger=trigger)

    # ... 其他试验单元类似地跟随 ...
```

## 此类的设计注意事项

TaskSettings 将最重要的实验参数——显示（`window`）、结构（`task`）和计时——分组到顶级属性中，以便直接、可预测地访问和提供合理的默认值。不经常使用的参数（例如 `triggers` 或控制器设置）可以作为嵌套字典提供，并且仅在需要时检索，从而保持核心设置的整洁。特定于刺激的配置（例如图像、声音）由 `StimBank` 单独管理，使设置类能够专注于整体实验流程，而不是单个资产的详细信息。

 `TaskSettings` 旨在实现可扩展性和可复现性。传递给 `from_dict()` 的未知键会成为动态属性，因此您可以在不修改类源代码的情况下定制设置。双重种子模式（`same_across_sub`、`same_within_sub`）让您可以在组级一致性或特定于被试的随机性之间进行选择。最后，简洁的 `__repr__()`、所有设置的 JSON 导出以及内置的目录/文件管理的结合，确保您的实验配置是透明的、易于记录的和直接调试的。

## 后续步骤

现在您已经了解了如何使用 `TaskSettings`，您可以：

- 了解 [SubInfo](get_subinfo_cn.md) 以收集被试信息
- 探索 [StimBank](build_stimulus_cn.md) 以管理刺激
- 查看 [BlockUnit](build_blocks_cn.md) 以将试验组织成块
- 查看 [StimUnit](build_trialunit_cn.md) 以创建单个试验