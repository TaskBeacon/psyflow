# PsyFlow 入门指南

## 什么是 PsyFlow？

PsyFlow 是一个为 PsychoPy 设计的高级包装器，旨在简化认知神经科学实验的开发。它提倡一种**声明式**和**有组织**的工作流程，让您更专注于实验逻辑，而不是样板代码。

主要功能包括：

- **声明式语法**：在易于阅读的 YAML 文件中定义刺激、计时和任务结构。
- **结构化项目布局**：命令行工具 (`psyflow-init`) 为您的项目生成一个标准化的、有组织的文件夹结构。
- **简化的 API**：像 `StimUnit` 和 `BlockUnit` 这样的高级类处理刺激呈现、响应捕获和数据记录的复杂性。
- **可扩展性**：轻松集成硬件触发器（EEG、fMRI）、眼动仪，以用于高级用例。

本指南将引导您从头开始创建一个简单的反应时任务，演示 PsyFlow 的核心概念。

## 安装

您可以使用 `pip` 安装 PsyFlow。
需要 Python >= 3.10。

#### 从 PyPI (推荐)

对于最新的稳定版本，请运行：

```bash
pip install psyflow
```

#### 从 GitHub (开发版本)

要获取最新的功能和更新，您可以直接从 GitHub 存储库安装：

```bash
pip install https://github.com/TaskBeacon/psyflow.git
```

## 第 1 步：创建一个新项目

首先，让我们使用 `psyflow-init` 命令行工具创建一个标准化的项目结构。打开您的终端，导航到您希望项目所在的位置，然后运行：

```bash
psyflow-init my-simple-task
```

此命令会创建一个名为 `my-simple-task` 的新文件夹，其布局如下：

```
my-simple-task/
├── main.py
├── README.md
├── config/
│   └── config.yaml
├── data/
└── src/
    ├── __init__.py
    ├── run_trial.py
    └── utils.py
```

这种结构将您的配置 (`config/`)、核心逻辑 (`src/`) 和数据 (`data/`) 分开，使您的项目保持井然有序。

## 第 2 步：在 `config.yaml` 中定义您的实验

PsyFlow 围绕声明式方法设计：您在 YAML 文件中*定义*实验的组件，而不是在 Python 中硬编码。这使得您的实验更易于阅读、修改和共享。

打开 `config/config.yaml` 并将其内容替换为以下内容：

```yaml
# config/config.yaml

# === 被试信息表单 ===
subinfo_fields:
  - name: subject_id
    type: int
    constraints:
      min: 1
      max: 999
  - name: gender
    type: choice
    choices: [Male, Female]

# === 窗口设置 ===
window:
  size: [1280, 720]
  bg_color: gray
  fullscreen: False

# === 任务级别设置 ===
task:
  task_name: "simple_rt"
  total_blocks: 2
  trial_per_block: 10
  conditions: [go] # 在这个简单的任务中，我们只有一个条件
  key_list: [space]

# === 刺激定义 ===
stimuli:
  instruction:
    type: textbox
    text: |
      欢迎！
      当您看到绿色圆圈时，
      请尽快按下空格键。
      按空格键开始。
    color: white
    font: Arial
    letterHeight: 0.8

  fixation:
    type: text
    text: "+"
    color: white
    height: 2

  target:
    type: circle
    radius: 3
    fillColor: green
    lineColor: black

# === 计时 ===
timing:
  fixation_duration: [0.5, 1.0] # 500ms 到 1000ms 之间的随机持续时间
  response_window: 2.0 # 2 秒响应时间
```

在此文件中，我们定义了：
- 一个简单的被试信息表单。
- 基本的窗口设置。
- 高级任务参数（2 个组块，每个组块 10 个试验）。
- 我们所有的视觉刺激（`instruction`、`fixation`、`target`）。
- 试验的计时参数。

## 第 3 步：编写试验逻辑

现在，让我们定义单个试验中发生的事情。打开 `src/run_trial.py` 并添加以下代码。此函数将为您的实验中的每个试验调用。

```python
# src/run_trial.py

from psyflow import StimUnit
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank):
    """
    运行反应时任务的单个试验。
    """
    # 为此试验创建一个字典来存储数据
    trial_data = {"condition": condition}

    # 使用偏函数预填充常见的 StimUnit 参数
    make_unit = partial(StimUnit, win=win, kb=kb)

    # 1. 显示注视十字
    make_unit(unit_label='fixation') \
        .add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration) \
        .to_dict(trial_data)

    # 2. 显示目标并捕获响应
    make_unit(unit_label='target') \
        .add_stim(stim_bank.get("target")) \
        .capture_response(
            keys=settings.key_list,
            duration=settings.response_window
        ) \
        .to_dict(trial_data)

    return trial_data
```
在这里，我们使用 `StimUnit` 将试验的事件链接在一起：显示一个注视点，然后显示一个目标并等待按键。所有数据（如反应时）都会自动收集并存储在 `trial_data` 中。

## 第 4 步：主脚本

最后，让我们在 `main.py` 中将所有内容整合在一起。此脚本将加载配置、设置实验、运行试验组块并保存数据。

将 `main.py` 的内容替换为：

```python
# main.py

from psyflow import (
    BlockUnit, StimBank, SubInfo, TaskSettings,
    load_config, initialize_exp, count_down
)
import pandas as pd
from psychopy import core
from functools import partial
from src.run_trial import run_trial

# 1. 从 YAML 文件加载所有配置
cfg = load_config()

# 2. 收集被试信息
subform = SubInfo(cfg['subinfo_config'])
subject_data = subform.collect()

# 3. 设置任务设置
settings = TaskSettings.from_dict(cfg['task_config'])
settings.add_subinfo(subject_data)

# 4. 设置窗口和键盘
win, kb = initialize_exp(settings)

# 5. 加载配置中定义的所有刺激
stim_bank = StimBank(win, cfg['stim_config']).preload_all()

# 6. 显示说明并等待开始
StimUnit('instruction', win, kb) \
    .add_stim(stim_bank.get('instruction')) \
    .wait_and_continue()

# 7. 运行所有组块和试验
all_data = []
for block_i in range(settings.total_blocks):
    count_down(win, 3) # 在组块前显示 3 秒倒计时
    block = BlockUnit(
        block_id=f"block_{block_i}",
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions() \
     .run_trial(partial(run_trial, stim_bank=stim_bank)) \
     .to_dict(all_data)

# 8. 保存收集的数据
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)
print(f"数据已保存到 {settings.res_file}")

# 9. 清理并退出
core.quit()
```

## 第 5 步：运行您的实验！

就是这样！您的简单反应时任务已完成。要运行它，请打开终端，导航到 `my-simple-task` 目录，然后执行：

```bash
python main.py
```

PsychoPy 将启动，显示被试信息表单，显示说明，然后运行您的任务。

## 后续步骤

您现在已经使用 PsyFlow 的核心组件构建了一个基本的实验。从这里，您可以探索更高级的功能：

- **定义刺激**：在[StimBank 教程](build_stimulus_cn.md)中学习如何在一个地方定义所有刺激。
- **构建复杂的试验**：在[StimUnit 教程](build_stimunit_cn.md)中学习如何创建具有多种刺激和响应类型的更复杂的试验。
- **组织组块**：请参阅[BlockUnit 教程](build_blocks_cn.md)以了解如何将试验组织成组块。
- **发送硬件触发器**：请参阅[TriggerSender 教程](send_trigger_cn.md)以了解如何集成 EEG、fMRI 或眼动追踪触发器。
