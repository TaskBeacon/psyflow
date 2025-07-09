# BlockUnit: 组织和运行试验

## 概述

`BlockUnit` 是 `psyflow` 中用于将单个试验（trials）组织成块（blocks）并以可重复、可随机化的方式运行它们的控制器。它简化了常见的实验设计模式，如试验循环、条件随机化和在块之间传递数据。

使用 `BlockUnit`，您可以：

-   从试验规格列表（例如，从 CSV 文件或 `pandas.DataFrame` 加载）创建一个块。
-   在将试验传递给您的运行函数之前，自动对它们进行随机化（加洗牌）。
-   在块的开始和结束时显示指令或休息屏幕。
-   在块内的所有试验中轻松传递常量参数。
-   将每个试验的数据聚合到一个单一的、有组织的列表中，以便于保存。

## 核心概念

`BlockUnit` 的工作流程围绕以下三个步骤：

1.  **定义试验**: 您创建一个字典列表，其中每个字典代表一个试验并包含该试验所需的所有信息（例如，条件、刺激名称、正确答案）。这通常是通过加载一个 CSV 文件并将其转换为 `pandas.DataFrame` 来完成的。
2.  **初始化 `BlockUnit`**: 您使用您的试验列表、一个运行单个试验的函数以及任何固定的参数来创建一个 `BlockUnit` 实例。
3.  **运行块**: 您调用 `.run()` 方法，该方法会迭代您的试验，根据需要对它们进行随机化，并为每个试验执行您的运行函数。

## 详细使用指南

### 1. 定义您的试验

一个块是由一个试验列表定义的。在 `psyflow` 中，这通常是一个 `pandas.DataFrame`，其中每一行代表一个试验，每一列代表一个参数。

假设您有一个名为 `trials.csv` 的文件，内容如下：

```csv
condition,target_stim,correct_key
win,win_stim_A,f
win,win_stim_B,j
loss,loss_stim_A,f
loss,loss_stim_B,j
```

您可以使用 `pandas` 来加载这个文件：

```python
import pandas as pd

trial_df = pd.read_csv('trials.csv')
```

`BlockUnit` 期望这个 DataFrame 被转换成一个字典列表，其中每个字典代表一行。您可以使用 `.to_dict('records')` 来轻松完成这个转换：

```python
trial_list = trial_df.to_dict('records')
# trial_list 现在是:
# [
#   {'condition': 'win', 'target_stim': 'win_stim_A', 'correct_key': 'f'},
#   {'condition': 'win', 'target_stim': 'win_stim_B', 'correct_key': 'j'},
#   ...
# ]
```

### 2. 创建一个试验运行函数

接下来，您需要一个 Python 函数，它知道如何运行 **单个** 试验。这个函数将接收 `BlockUnit` 中的信息作为参数。

-   它必须接受一个名为 `trial_info` 的参数，这是一个来自您列表的字典（即，一行来自您的 CSV）。
-   它还可以接受您在初始化 `BlockUnit` 时定义的任何其他关键字参数（“固定参数”）。

这是一个典型的试验运行函数的骨架，它位于 `src/run_trial.py` 中：

```python
# In src/run_trial.py

def run_trial(trial_info, win, kb, stim_bank, settings):
    """
    运行一个单独的试验。

    参数:
    - trial_info (dict): 来自试验列表的当前试验的规格。
    - win, kb, stim_bank, settings: 传递给 BlockUnit 的固定参数。
    """
    # 1. 从 trial_info 中解包信息
    condition = trial_info['condition']
    target_name = trial_info['target_stim']
    correct_key = trial_info['correct_key']

    # 2. 使用 stim_bank 检索刺激
    target_stim = stim_bank.get(target_name)

    # 3. 使用 StimUnit 来呈现刺激并捕获反应
    # (这是一个简化的例子)
    unit = StimUnit(f"trial_{trial_info['trial_num']}", win, kb)
    unit.add_stim(target_stim)
    unit.capture_response(keys=['f', 'j'], correct_keys=[correct_key], duration=2.0)

    # 4. 返回试验数据
    return unit.to_dict()
```

### 3. 初始化 `BlockUnit`

现在您已经有了您的试验列表和您的 `run_trial` 函数，您可以初始化 `BlockUnit`。

```python
from psyflow.block_unit import BlockUnit
from src.run_trial import run_trial # 导入您的函数

# 试验列表 (来自上面的 .csv)
trial_list = pd.read_csv('trials.csv').to_dict('records')

# 固定的参数，将传递给每个 run_trial 调用
fixed_params = {
    'win': my_psychopy_window,
    'kb': my_keyboard,
    'stim_bank': my_stim_bank,
    'settings': my_experiment_settings
}

# 创建 BlockUnit 实例
block = BlockUnit(
    trial_list=trial_list,
    run_func=run_trial,
    fixed_params=fixed_params,
    shuffle=True  # 在运行前对试验列表进行随机化
)
```

-   `trial_list`: 您的试验规格列表。
-   `run_func`: 您为运行单个试验而创建的函数。
-   `fixed_params`: 一个字典，包含将作为关键字参数传递给您的 `run_func` 的对象。这对于传递像 `win`、`kb` 和 `stim_bank` 这样的全局对象非常有用。
-   `shuffle`: 一个布尔值，指示是否在运行前对 `trial_list` 进行随机化。默认为 `False`。

### 4. 运行块

最后，调用 `.run()` 方法来执行块。这将迭代（可能是随机化后的）`trial_list`，并为每个条目调用您的 `run_trial` 函数。

```python
# 在块开始前显示指令
show_instructions(win, "准备好开始第一个块！")

# 运行块并收集数据
block_data = block.run()

# 在块结束后显示休息屏幕
show_break_screen(win, "休息一下！")

# block_data 现在是一个列表，其中包含了每个试验返回的字典
# [{'condition': 'win', 'response': 'f', ...}, {'condition': 'loss', ...}]
```

`.run()` 方法会自动将 `trial_info` 和 `fixed_params` 传递给您的 `run_trial` 函数。它收集从每个 `run_trial` 调用返回的字典，并将它们聚合到一个列表中。

### 5. 添加开始和结束屏幕

`BlockUnit` 使得在块的开始和结束时显示屏幕变得容易，使用 `.on_start()` 和 `.on_end()` 方法。这些方法接受一个函数，该函数将被调用。

```python
def show_start_screen(block_info):
    """在块开始时显示。"""
    # block_info 是一个包含块信息的字典
    msg = f"即将开始块 {block_info['block_num']}"
    instruction_unit = StimUnit('instructions', win, kb)
    instruction_unit.add_stim(visual.TextStim(win, text=msg))
    instruction_unit.wait_and_continue()

def show_end_screen(block_info, block_data):
    """在块结束时显示。"""
    # block_data 是从块收集的数据
    accuracy = calculate_accuracy(block_data)
    msg = f"块完成！您的准确率是: {accuracy:.2f}%"
    feedback_unit = StimUnit('feedback', win, kb)
    feedback_unit.add_stim(visual.TextStim(win, text=msg))
    feedback_unit.wait_and_continue()

# 将钩子附加到您的块
block.on_start(show_start_screen)
block.on_end(show_end_screen)

# 现在，当您调用 .run() 时，这些函数将被自动执行
block_data = block.run()
```

-   传递给 `.on_start()` 的函数接收一个包含关于块的信息的字典（例如，`block_num`）。
-   传递给 `.on_end()` 的函数接收该信息字典 **和** 从块中收集的 `block_data`。

## 后续步骤

通过 `BlockUnit`，您现在拥有了在 `psyflow` 中构建功能齐全的实验的所有构建块。您可以：

-   回顾 `StimUnit` 教程以获取有关构建单个试验的更多详细信息。
-   学习 `TaskSettings` 以了解如何管理整个实验的设置。
