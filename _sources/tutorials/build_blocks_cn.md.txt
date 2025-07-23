# BlockUnit: 管理试验

## 概述

`BlockUnit` 类是在心理学实验中组织试验的强大工具。它提供了一种结构化的方式来管理试验序列、生成平衡的条件、跟踪结果并总结性能指标。本教程将指导您使用 `BlockUnit` 来创建结构良好的实验块。

`BlockUnit` 解决了实验设计中的几个常见挑战：

- **条件平衡：** 生成具有适当随机化和平衡的试验条件
- **试验排序：** 管理一个块内的试验流程
- **数据组织：** 自动跟踪试验级别的数据和块元数据
- **块生命周期：** 在块边界执行设置和清理操作
- **结果总结：** 计算跨试验和条件的性能指标

## 主要功能

| 功能 | 描述 |
| --- | --- |
| 条件生成 | 创建平衡、随机化的试验序列 |
| 块生命周期钩子 | 在块执行之前/之后执行代码 |
| 结果跟踪 | 自动收集和组织试验数据 |
| 总结 | 按条件计算性能指标 |
| 元数据 | 跟踪计时、试验计数和块信息 |
| 集成 | 与其他 psyflow 组件无缝协作 |

## 快速参考

| 目的 | 方法 | 示例 |
| --- | --- |
| 初始化块 | `BlockUnit(block_id, block_idx, ...)` | `block = BlockUnit("block1", 0, settings)` |
| 生成条件 | `.generate_conditions(func, labels)` | `block.generate_conditions(generate_func, ["A","B"])` |
| 手动添加条件 | `.add_condition(condition_list)` | `block.add_condition(["A","B","A"])` |
| 注册开始钩子 | `.on_start(func)` | `@block.on_start()` 或 `block.on_start(func)` |
| 注册结束钩子 | `.on_end(func)` | `@block.on_end()` 或 `block.on_end(func)` |
| 运行所有试验 | `.run_trial(trial_func, **kwargs)` | `block.run_trial(run_trial_function)` |
| 获取结果 | `.to_dict()` | `results = block.to_dict()` |
| 附加结果 | `.to_dict(target_list)` | `block.to_dict(all_results)` |
| 总结结果 | `.summarize()` | `summary = block.summarize()` |
| 自定义总结 | `.summarize(func)` | `summary = block.summarize(custom_func)` |
| 记录块信息 | `.logging_block_info()` | `block.logging_block_info()` |

## 详细使用指南

### 1. 初始化

要创建一个 `BlockUnit`，您需要提供有关块和实验设置的基本信息：

```python
from psyflow import BlockUnit

block = BlockUnit(
    block_id='block1',      # 唯一标识符
    block_idx=0,            # 块索引 (0-based)
    settings=settings,      # TaskSettings 实例
    window=win,             # PsychoPy 窗口
    keyboard=kb             # PsychoPy 键盘
)
```

`settings` 参数应该是一个 `TaskSettings` 对象或类似的对象，其中包括：

- `trials_per_block`: 每个块中的试验次数
- `block_seed`: 用于随机数生成的种子（用于可复现性）
- `condition_list`: 条件列表

### 2. 生成条件

`generate_conditions()` 方法提供了一个内置的、平衡的（或加权的）生成器，以创建一个长度为 `n_trials` 的条件标签序列。关键参数：

- `condition_labels`: 用于此块的标签列表（默认为 `settings.conditions`）。
- `weights`: 每个标签的相对权重（默认为相等权重）。
- `order`: `'random'` 或 `'sequential'`——控制最终序列的排列。
- `seed`: 用于可复现洗牌的随机种子覆盖。

**加权生成算法**

此方法首先计算每个标签的基本计数为 `floor(n_trials * weight / total_weight)`，然后根据给定的权重随机分配任何剩余的试验。最后，它通过按指定顺序交错标签或洗牌完整列表来构建完整序列，具体取决于 `order` 参数。

**设置权重**：

```
# 使 'A' 的可能性是 'B' 的两倍
block.generate_conditions(
    condition_labels=['A', 'B'],
    weights=[2, 1],
    order='random',
    seed=42
)
```

预期的 A:B 比例约为 2:1，受舍入和余数随机分布的影响。

**顺序模式**：

- **Sequential**: 确保按原始标签顺序交错、循环呈现条件。
  *示例*：在一个有两种条件——`ec`（闭眼）和 `eo`（睁眼）——的静息态实验中，使用 `order='sequential'` 会产生 `['ec','eo','ec','eo']`，可预测地交替块。
- **Random**: 提供一个完全洗牌的序列，同时尊重标签权重。
  *示例*：使用相同的 `ec`/`eo` 设置和 `order='random'`，序列可能是 `['ec','ec','eo','eo']` 或任何其他随机排列。

**示例**：

```python
# 默认：使用 settings.conditions、相等权重、随机顺序
block.generate_conditions()

# 自定义标签和顺序
block.generate_conditions(
    condition_labels=['X', 'Y', 'Z'],
    weights=[1, 1, 2],
    order='sequential'
)
```

**自定义条件生成器**

对于专门的块设计——例如停止信号任务（SST），您需要对停止/执行比率、运行长度和起始试验有特定约束——您可以提供自己的生成器函数。您的函数必须具有以下签名：

```python
def gen_func(n_trials, condition_labels=None, seed=None, **kwargs) -> List[str]:
    ...
```

**示例：SST 条件生成器**

此自定义函数为停止信号任务（SST）生成条件序列，强制执行：

- 固定的停止与执行试验比率（`stop_ratio`）。
- 连续停止试验的最大运行长度（`max_stop_run`）。
- 初始执行试验的最小数量（`min_go_start`）。
- 通过本地 RNG 保护全局随机状态。

```python
import random
from typing import List, Optional

def generate_sst_conditions(
    n_trials: int,
    condition_labels: Optional[List[str]] = None,
    stop_ratio: float = 0.25,
    max_stop_run: int = 4,
    min_go_start: int = 3,
    seed: Optional[int] = None
) -> List[str]:
    """
    在保留全局 RNG 状态的同时生成 SST 序列。
    """
    # 1) 如果没有提供标签，则使用默认标签
    if condition_labels is None:
        condition_labels = ['go_left', 'go_right', 'stop_left', 'stop_right']
    go_labels   = [lbl for lbl in condition_labels if lbl.startswith('go')]
    stop_labels= [lbl for lbl in condition_labels if lbl.startswith('stop')]

    # 2) 计算试验次数
    n_stop = int(round(n_trials * stop_ratio))
    n_go   = n_trials - n_stop
    base_go, rem_go   = divmod(n_go,   len(go_labels))
    base_st, rem_st   = divmod(n_stop, len(stop_labels))

    counts = {}
    for i, lbl in enumerate(go_labels):
        counts[lbl] = base_go + (1 if i < rem_go else 0)
    for i, lbl in enumerate(stop_labels):
        counts[lbl] = base_st + (1 if i < rem_st else 0)

    # 3) 构建并带约束地洗牌
    trial_list = [lbl for lbl, cnt in counts.items() for _ in range(cnt)]
    rng = random.Random(seed)

    while True:
        rng.shuffle(trial_list)
        # a) 前 min_go_start 个试验必须是 'go'
        if any(lbl.startswith('stop') for lbl in trial_list[:min_go_start]):
            continue
        # b) 任何 5 个试验窗口内不超过 max_stop_run 个停止试验
        violation = False
        for i in range(n_trials - 4):
            window = trial_list[i:i+5]
            if sum(lbl.startswith('stop') for lbl in window) > max_stop_run:
                violation = True
                break
        if not violation:
            break

    return trial_list

# 在 BlockUnit 中使用它：
block.generate_conditions(
    func=generate_sst_conditions,
    condition_labels=['go_left','go_right','stop_left','stop_right'],
    seed=123
)
print(block.conditions)
```

通过将自定义生成器作为 `func` 参数传递给 `generate_conditions()` 来应用它。

例如，在构建块时使用 `generate_sst_conditions`：

```python
block = BlockUnit(
    block_id=f"block_{block_i}",
    block_idx=block_i,
    settings=settings,
    window=win,
    keyboard=kb
).generate_conditions(
    func=generate_sst_conditions
)
```

这个单一的调用既创建了块，又根据 SST 约束生成了其试验条件，并将结果序列存储在 `block.conditions` 中。

**手动条件分配**

如果条件的精确序列是预先确定的，则完全绕过生成器：

```python
# 交替 ec/eo 的预定义块序列
manual_seq = ['ec','eo','ec','eo']
block.add_condition(manual_seq)
print(block.conditions)
```

### 3. 钩子：on_start 和 on_end

钩子允许在每个块的开始或结束时注入自定义逻辑，而无需修改核心试验循环。常见用途包括：

- **触发硬件事件**（例如，发送 EEG 或 MRI 触发器）
- **更新 GUI 元素**（例如，显示块进度或说明）
- **记录或分析**（例如，为其他指标添加时间戳）

可以通过两种方式注册钩子：

1. **装饰器风格**：
   ```python
   @block.on_start()
   def before_block(b):
       # 自定义设置
       print(f"开始块 {b.block_id}")

   @block.on_end()
   def after_block(b):
       # 自定义清理
       print(f"结束块 {b.block_id}")
   ```
2. **链式风格**：
   ```python
   block = BlockUnit(...)
   block.on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset")))
        .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))
   ```

**示例：在块边界发送触发器**

```python
block = BlockUnit(
    block_id=f"block_{block_i}",
    block_idx=block_i,
    settings=settings,
    window=win,
    keyboard=kb
).generate_conditions(func=generate_sst_conditions)
  .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset")))
  .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end")))
```

此设置确保在块开始和结束时精确发送触发器或外部事件，并无缝集成到块执行流程中。

### 4. 运行试验

`.run_trials()` 方法通过重复调用用户定义的试验函数来驱动块中每个试验的执行。该函数通常在 TAPS 代码库的 `src/run_trial.py` 中实现，并封装了所有试验级别的逻辑（例如，刺激呈现、响应捕获、触发器）。

**签名：**

```python
block.run_trials(
    trial_func,
    **kwargs
)
```

- `trial_func` (callable, required): 试验级别的函数。必须接受四个强制性参数：
  1. `win` (PsychoPy 窗口)
  2. `kb` (PsychoPy 键盘)
  3. `settings` (TaskSettings)
  4. `condition` (str 或标签) 其他参数（例如 `stim_bank`、`controller`、`trigger_sender`）可以通过 `kwargs` 传递，并且是可选的——仅当您的 `trial_func` 使用它们时才包括它们。

> **注意：** 在调用 `.run_trials()` **之前** 注册所有 `on_start` 和 `on_end` 钩子，因为它们在此方法内部被调用。

**执行流程：**

1. **开始时间戳**：保存 `meta['block_start_time']`。
2. **钩子**：运行块开始回调（例如，触发器）。
3. **每个试验的循环**：
   ```python
   result = trial_func(
       block.win,
       block.kb,
       block.settings,
       condition,
       **kwargs
   )
   ```
4. **钩子**：运行块结束回调。
5. **结束时间戳和持续时间**：设置 `meta['block_end_time']` 和 `meta['duration']`。

#### **静息态示例**

此试验函数显示一个说明屏幕，后跟一个简单的刺激，没有响应收集。

```python
from psyflow import StimUnit
from functools import partial

def run_trials(win, kb, settings, condition, stim_bank, trigger_sender):
    data = {'condition': condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)

    # 仅说明
    make_unit('inst') \
        .add_stim(stim_bank.get(f"{condition}_instruction")) \
        .show() \
        .to_dict(data)

    # 仅刺激
    make_unit('stim') \
        .add_stim(stim_bank.get(f"{condition}_stim")) \
        .show(duration=settings.rest_duration) \
        .to_dict(data)

    return data

block.run_trials(run_trials, stim_bank=stim_bank, trigger_sender=trigger_sender)
```
#### **MID 任务示例**
实现一个多阶段试验（提示 → 预期 → 目标 → 反馈），使用 `controller` 调整持续时间并记录响应。

```python
from psyflow import StimUnit
from functools import partial

def run_trials(win, kb, settings, condition, stim_bank, controller, trigger_sender):
    data = {'condition': condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)

    # 提示阶段
    make_unit('cue') \
        .add_stim(stim_bank.get(f"{condition}_cue")) \
        .show(duration=settings.cue_duration) \
        .to_dict(data)

    # (预期、目标、反馈阶段遵循类似的模式)

    return data

block.run_trials(run_trials, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender)
```

### 5. 访问和筛选数据

要提取和分析块级别的结果，请使用两个核心方法：

1. **使用 `.get_all_data()` 检索所有试验**，它返回块中所有试验字典的有序列表。
2. **使用 `.get_trial_data(key, pattern, match_type, negate)` 筛选特定试验**，选择与给定条件匹配的子集。

#### 示例：使用 `.get_all_data()` 的 MID 块总结

在金钱激励延迟（MID）任务中，您通常会计算一个块中所有试验的总体性能指标：

```python
# 按顺序检索每个试验
block_trials = block.get_all_data()

# 计算命中率：'target_hit' 为 True 的试验比例
total_trials = len(block_trials)
hit_trials = sum(t.get('target_hit', False) for t in block_trials)
hit_rate = hit_trials / total_trials

# 计算试验中的总反馈分数
total_score = sum(t.get('feedback_delta', 0) for t in block_trials)
```

在这里，`.get_all_data()` 提供了完整的试验数据集，简单的列表推导式可以生成块的摘要统计信息。

#### 示例：使用 `.get_trial_data()` 的 SST 块分析

在停止信号任务（SST）中，为不同的性能指标分别处理执行和停止试验：

```python
# 按条件前缀筛选试验
go_trials = block.get_trial_data(
    key='condition',
    pattern='go',
    match_type='startswith'
)
stop_trials = block.get_trial_data(
    key='condition',
    pattern='stop',
    match_type='startswith'
)

# 执行试验命中率
total_go = len(go_trials)
go_hits = sum(t.get('go_hit', False) for t in go_trials)
go_hit_rate = go_hits / total_go if total_go else 0

# 停止试验成功率（无按键）
total_stop = len(stop_trials)
stops_success = sum(
    not t.get('go_ssd_key_press', False) and not t.get('stop_key_press', False)
    for t in stop_trials
)
stop_success_rate = stops_success / total_stop if total_stop else 0
```

`.get_trial_data()` 通过将 `'condition'` 字段与模式匹配来筛选，从而允许对每个试验子集进行下游计算。

### 6. 总结块结果

为了获得完全的灵活性，通常最好使用上面介绍的数据检索方法手动计算块级别的摘要。这可以确保统计数据与您的试验逻辑生成​​的字段完全匹配。两种常见的模式是：

#### 使用 `.get_all_data()` 手动总结（例如，MID 任务）

使用 `.get_all_data()` 按顺序获取每个试验的结果字典，然后应用简单的 Python 表达式来计算块指标。在金钱激励延迟（MID）实验中，您可以如下计算总体命中率和总分：

```python
# 获取所有试验数据
block_trials = block.get_all_data()

# 命中率：目标被命中的试验比例
total_trials = len(block_trials)
hit_count    = sum(trial.get('target_hit', False) for trial in block_trials)
hit_rate     = hit_count / total_trials

# 整个块的总反馈分数（增量）
total_score  = sum(trial.get('feedback_delta', 0) for trial in block_trials)
```

此方法适用于您的 `run_trials` 函数存储的任何字段。只需调整推导式以定位相关键即可。

#### 使用 `.get_trial_data()` 手动总结（例如，SST 任务）

当不同类型的试验需要不同的指标时——如在具有执行与停止试验的停止信号任务（SST）中——使用 `.get_trial_data()` 筛选块的试验，然后总结每个子集：

```python
# 按条件前缀分离执行和停止试验
go_trials   = block.get_trial_data(
    key='condition', pattern='go', match_type='startswith'
)
stop_trials = block.get_trial_data(
    key='condition', pattern='stop', match_type='startswith'
)

# 执行试验命中率
total_go     = len(go_trials)
go_hits      = sum(trial.get('go_hit', False) for trial in go_trials)
go_hit_rate  = go_hits / total_go if total_go else 0

# 停止试验成功率（停止试验无响应）
total_stop        = len(stop_trials)
stop_success_count = sum(
    not trial.get('go_ssd_key_press', False) and not trial.get('stop_key_press', False)
    for trial in stop_trials
)
stop_success_rate = stop_success_count / total_stop if total_stop else 0
```

#### 内置 `.summarize()` 实用程序

`BlockUnit` 还提供了一个默认的总结器，可以计算每个条件的命中率和平均反应时间：

```python
summary = block.summarize()
# 示例输出：
# {
#   'A': {'hit_rate': 0.75, 'avg_rt': 0.48},
#   'B': {'hit_rate': 0.62, 'avg_rt': 0.55}
# }
```

要覆盖此行为，请提供一个接受 `BlockUnit` 并返回摘要指标字典的自定义函数。以下是为 SST 块量身定制的示例：

```python
import numpy as np

def sst_summary(bu):
    """计算 SST 块的执行命中率和停止成功率。"""
    # 检索所有试验
    trials = bu.get_all_data()
    # 分离执行和停止试验
    go_trials = bu.get_trial_data('condition', 'go', match_type='startswith')
    stop_trials = bu.get_trial_data('condition', 'stop', match_type='startswith')

    # 执行试验命中率
    total_go = len(go_trials)
    go_hits = sum(t.get('go_hit', False) for t in go_trials)
    go_hit_rate = go_hits / total_go if total_go else 0

    # 停止试验成功率（无响应）
    total_stop = len(stop_trials)
    stop_success = sum(
        (not t.get('go_ssd_key_press', False)) and not t.get('stop_key_press', False)
        for t in stop_trials
    )
    stop_success_rate = stop_success / total_stop if total_stop else 0

    return {
        'go_hit_rate': go_hit_rate,
        'stop_success_rate': stop_success_rate
    }

# 使用自定义总结器
summary = block.summarize(summary_func=sst_summary)
```

### 7. 存储块级别的数据

每个块完成后，其试验结果（存储在 `block.results` 中）可以使用 `.to_dict()` 方法合并到整个实验的主列表中。此方法支持两种模式：

- **链式模式**：不带参数调用 `.to_dict()` 只返回 `BlockUnit` 实例，允许您链接其他调用。
- **附加模式**：将列表传递给 `.to_dict(target_list)` 会将该列表扩展为块的试验字典。

```python
# 初始化一个空列表以收集所有试验
all_data = []

for block_i in range(settings.total_blocks):
    # 准备并运行块，然后附加其结果
    BlockUnit(
        block_id=f"block_{block_i}",
        block_idx=block_i,
        settings=settings,
        window=win,
        keyboard=kb
    ).generate_conditions() \
     .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset"))) \
     .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end"))) \
     .run_trials(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender) \
     .to_dict(all_data)

# 此时，all_data 包含所有块的所有试验字典

# 转换为 DataFrame 并保存到 CSV
import pandas as pd
df = pd.DataFrame(all_data)
df.to_csv(settings.res_file, index=False)
```

> **替代方法：** 您可以在运行块后调用 `block.get_all_data()` 并手动扩展您的列表：
>
> ```python
> block.run_trials(...)
> block_data = block.get_all_data()
> all_data.extend(block_data)
> ```

### 8. 记录块信息

`BlockUnit` 会在开始和结束时自动记录元数据：

```
[BlockUnit] Blockid: block1
[BlockUnit] Blockidx: 0
[BlockUnit] Blockseed: 12345
[BlockUnit] Blocktrial-N: 40
[BlockUnit] Blockdist: {'A':20,'B':20}
[BlockUnit] Blockconditions: ['A','B',...]
```

## 后续步骤

现在您已经了解了如何使用 `BlockUnit`，您可以：

- **构建试验**：了解 [StimUnit](build_stimunit_cn.md) 以更好地控制单个试验
- **管理刺激**：探索 [StimBank](build_stimulus_cn.md) 以进行高效的刺激管理
- **发送触发器**：查看 [TriggerSender](send_trigger_cn.md) 以进行 EEG/MEG 实验集成