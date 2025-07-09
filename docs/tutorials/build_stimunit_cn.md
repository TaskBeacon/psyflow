# StimUnit：模块化的刺激呈现与反应处理单元

## 概述

`StimUnit` 是一个功能多样、用于 PsychoPy 实验的刺激级别控制器。它将单个试次（trial）所需的一切都捆绑到一个可链式调用的对象中：

- **刺激呈现**：以亚帧级的精度同时绘制多个视觉或听觉刺激。
- **反应收集**：轻松检测键盘事件并记录反应时。
- **时间控制**：根据您的需求，选择基于帧（刷新锁定）或基于时钟的计时方式。
- **状态管理**：将所有与试次相关的数据存储在集中的内部字典中。
- **事件钩子（Event hooks）**：在开始、反应、超时和结束阶段插入自定义回调函数。

通过使用 `StimUnit`，您的试次逻辑（通常在 `src/run_trial.py` 中定义）将变得更加模块化、可读和易于维护。

## 主要特性

| 特性 | 描述 |
| --- | --- |
| **链式 API** | 通过链式调用方法，流畅地构建试次。 |
| **基于帧的计时** | 高精度。 |
| **事件钩子** | 在开始、反应、超时或结束时调用自定义函数。 |
| **灵活的反应** | 指定有效按键和自动反应时处理。 |
| **状态追踪** | 集中存储时间戳、反应和自定义数据。 |
| **反应高亮** | 视觉上突出显示选择（静态或动态）。 |
| **抖动计时** | 支持随机化（最小-最大）的持续时间，以增加不可预测性。 |

## 快速参考

| 用途 | 方法 | 示例 |
| --- | --- | --- |
| 初始化 | `StimUnit(label, win, kb)` | `unit = StimUnit("cue", win, kb)` |
| 添加刺激 | `.add_stim(stim1, stim2, ...)` | `unit.add_stim(fixation, target)` |
| 开始钩子 | `.on_start(fn)` | `@unit.on_start()` |
| 反应钩子 | `.on_response(keys, fn)` | `@unit.on_response(['left','right'])` |
| 超时钩子 | `.on_timeout(sec, fn)` | `@unit.on_timeout(2.0)` |
| 结束钩子 | `.on_end(fn)` | `@unit.on_end()` |
| 简单显示 | `.show(duration)` | `unit.show(1.0)` |
| 捕获反应 | `.capture_response(keys, duration)` | `unit.capture_response(['left','right'], 2.0)` |
| 完整试次控制 | `.run()` | `unit.run()` |
| 暂停与继续 | `.wait_and_continue(keys)` | `unit.wait_and_continue(['space'])` |
| 更新状态 | `.set_state(**kwargs)` | `unit.set_state(correct=True)` |
| 检索状态 | `.get_state()` 或访问 `.state` | `data = unit.get_state(key,default)` |
| 导出状态 | `.to_dict()` | `data = unit.to_dict()` |

## 详细使用指南

### 0. 创建一个 StimBank
```python
from psyflow.stim_bank import StimBank
# 1. 定义一个刺激配置的字典
stim_config = {
    'fixation': {
        'type': 'text',
        'text': '+',
        'color': 'white',
        'height': 1.0
    },
    'target': {
        'type': 'circle',
        'radius': 0.5,
        'fillColor': 'red'
    },
    'feedback': {
        'type': 'text',
        'text': 'Correct!',
        'pos': [0, -2],
        'color': 'green'
    }
}

# 2. 使用窗口和定义创建您的 StimBank
stim_bank = StimBank(win, stim_config)
stim_bank.preload_all()  # 可选
```

### 1. 初始化

首先创建您的 PsychoPy 窗口和键盘，然后用一个描述性的标签来实例化 `StimUnit`。

```python
win = visual.Window([1024,768], color='black')
kb = Keyboard()

# 实例化 StimUnit
fix = StimUnit('fix', win, kb).add_stim(stim_bank.get('fixation'))
tar = StimUnit('tar', win, kb).add_stim(stim_bank.get('target'))
fb = StimUnit('fb', win, kb).add_stim(stim_bank.get('feedback'))
```

选择描述性的 `unit_label`（例如 `"fix"`, `"tar"`, `"fb"`）。当您调用 `set_state()` 时，这些标签会自动作为前缀添加到您的状态键上，并通过 `get_state()` 访问，确保您的试次数据整洁地命名并且易于查询。

**专业提示：** 当您需要在同一上下文中创建许多相似的试次单元时，使用 Python 的 `functools.partial` 来简化实例化过程：

```python
from functools import partial
# 创建一个带有通用参数的快捷方式
make_unit = partial(StimUnit, win=win, kb=kb)

# --- 提示阶段 ---
fix=make_unit('fix').add_stim(stim_bank.get('fixation'))
tar=make_unit('tar').add_stim(stim_bank.get('target'))
fb=make_unit('fb').add_stim(stim_bank.get('feedback'))
```

### 2. 添加刺激

在呈现一个试次之前，附加您想要显示或播放的刺激——这定义了被试在该单元期间将看到或听到的内容。

`StimUnit` 接受 `visual.BaseVisualStim`（例如 `TextStim`, `Circle`）和 `sound.Sound` 的实例。您可以一次添加单个刺激、多个刺激，或传递一个刺激列表：

```python
# 添加单个刺激
unit.add_stim(stim_bank.get('fixation'))

# 一次添加多个刺激
unit.add_stim(
    stim_bank.get('target'),
    stim_bank.get('feedback')
)

# 添加一个刺激列表
unit.add_stim([
    stim_bank.get('fixation'),
    stim_bank.get('target'),
    stim_bank.get('feedback')
])

# 链式添加
unit.add_stim(stim_bank.get('fixation')) \
    .add_stim(stim_bank.get('target')) \
    .add_stim(stim_bank.get('feedback'))

# 清除所有刺激
unit.clear_stimuli()
```

当您呈现该单元时，所有添加的刺激将一起被绘制或播放。

请注意，`add_stim` 也支持 PsychoPy 风格的刺激定义。例如：
```python
from psychopy.visual import TextStim, Circle
# 示例 1
stim_list = {'fix': TextStim(win, text='+', pos=(0,0)), 
            'tar': Circle(win, radius=0.5, fillColor='red'),
            'fb': TextStim(win, text='Correct!', pos=(0,0))}
unit.add_stim(stim_list['fix']).add_stim(stim_list['tar']).add_stim(stim_list['fb'])

# 示例 2
fixation = visual.TextStim(win, text='+', height=0.8)
unit.add_stim(fixation)
unit.show(duration=(0.5, 1.5))
```
在 `psyflow` 框架中，刺激通常从一个 `stim_bank` 对象中检索。
这让您可以快速地从您的 `stim_bank` 中检索命名好的刺激，并将它们传递给 `StimUnit`，从而简化了 stimunit 的设置。例如：
```python
condition = 'loss'
make_unit(unit_label='cue').add_stim(stim_bank.get(f"{condition}_cue"))
make_unit(unit_label=f"pop")\
    .add_stim(stim_bank.get(f"{condition}_pop"))\
    .add_stim(stim_bank.get("pop_sound"))
```

### 3. 使用 `show()` 显示刺激

`show()` 方法是 `StimUnit` 中的核心显示函数。它在一个调用中处理了精确定时、绘制、可选的音频播放和状态记录。当您想要呈现刺激而不需要反应时，请使用它。

**`show()` 的主要特性**
- **基于帧的计时**：将呈现锁定到显示器刷新，以实现亚帧级精度。
- **自动音频支持**：在第一次翻转时开始播放任何声音刺激。
- **灵活的持续时间**：接受固定的时间、抖动的范围，或自动使用声音的长度。
- **状态记录**：将开始/结束时间戳和持续时间记录到 `unit.state` 中。

当您需要独立的刺激呈现而无需反应处理时，请使用此方法：
- **反馈显示**：在短时间内显示反馈信息或声音（例如，“正确！”，错误音）。
- **被动刺激呈现**：在反应被分开记录的范式中（如静息态 EEG 或 fMRI），呈现视觉或听觉刺激（例如，闪烁、音调）。
- **基线/休息期**：呈现注视十字或空白屏幕，持续时间可抖动，作为试次间间隔或基线。

#### 方法签名

```python
.show(
    duration: float | tuple[float, float] | None = None,
    onset_trigger: int = None,
    offset_trigger: int = None
) -> StimUnit
```

- `duration`:
  - **None**：使用声音刺激中最长的 `getDuration()`（如果没有声音则为 0.0）。
  - **float**：以秒为单位的固定呈现时间。
  - **(min, max)**：在 `min` 和 `max` 之间均匀随机化。

- `onset_trigger` / `offset_trigger`: *（可选）* 用于发送触发器的占位符参数——如果您单独管理触发器，这些参数将被忽略。

#### 行为表

| 输入的持续时间 | 行为 |
| --- | --- |
| `None` | 从音频中自动选择（最大持续时间或 0.0）。 |
| `0.5` | 精确呈现 0.5 秒。 |
| `(0.8, 1.2)` | 在 [0.8, 1.2] 秒内采样。 |
| `1.0` + 2.5 秒的音频 | 屏幕在 1.0 秒时停止；音频可能会被切断。 |
| `None` + 2.5 秒的音频 | 屏幕和音频都持续完整的 2.5 秒。 |

以下示例演示了如何使用 `.show()` 实现固定、抖动和音频驱动的持续时间。假设 `unit` 是一个已初始化的 `StimUnit`，`stim_bank` 包含您的刺激。

```python
# 1. 固定持续时间 – 显示文本恰好 1.0 秒
unit.add_stim(stim_bank.get('fixation'))\
    .show(duration=1.0)

# 2. 抖动持续时间 – 在 1 到 2 秒之间的随机时间内显示文本
unit.add_stim(stim_bank.get('fixation'))\
    .show(duration=(1,2)) # 元组

unit.add_stim(stim_bank.get('fixation'))\
    .show(duration=[1,2]) # 列表

# 3. 从音频自动确定 – 显示视觉并播放音频，持续整个声音的长度
unit.add_stim(stim_bank['pop_sound']).show() # duration=None 是默认值

# 4. 多个刺激
unit.add_stim(stim_bank.get('pop_sound'))\
    .add_stim(stim_bank.get('fixation'))\
    .show(duration=None)
```

### 4. 使用 `wait_and_continue()` 暂停和继续

使用 `.wait_and_continue()` 来显示刺激并等待被试输入后再继续，这对于指导语屏幕、组块间休息和实验结束致谢非常理想。它强制一个最小的显示时间，并可以选择在按键后终止会话。

当您需要被试在继续前确认或知晓，而无需捕获试次反应时，请使用此方法。常见场景包括：
- **指导语屏幕**：例如，在实验组块开始前显示“按空格键开始”。
- **组块间休息**：给被试休息的机会，并在他们准备好时继续。
- **实验结束信息**：显示感谢语或实验说明，直到按键。
- **任何独立的确认**：当您不需要记录反应数据但需要明确的继续操作时。

#### 方法签名

```python
def wait_and_continue(
    keys: list[str] = ["space"],
    min_wait: Optional[float] = None,
    log_message: Optional[str] = None,
    terminate: bool = False
) -> StimUnit
```

- `keys`: 允许继续的按键列表（默认为 `['space']`）。
- `min_wait`: 接受输入前等待的最小秒数。如果为 `None`，并且存在音频刺激，则默认为最长的声音持续时间。如果只有视觉刺激，则默认为无限，直到按下按钮。
- `log_message`: 记录到 PsychoPy 日志的自定义消息（默认为：
  - “Continuing after key 'X'” 或
  - “Experiment ended by key press.” 如果 `terminate=True`）。
- `terminate`: 如果为 `True`，则在输入后关闭 PsychoPy 窗口。

**示例**
```python
# 指导语屏幕：等待至少 2 秒以响应空格键
StimUnit('instruction_text', win, kb)\
    .add_stim(stim_bank.get('instruction_text'))\
    .add_stim(stim_bank.get('instruction_text_voice'))\
    .wait_and_continue()

# 结束屏幕：按键后立即终止
final_score = sum(trial.get("feedback_delta", 0) for trial in all_data)
StimUnit('goodbye',win,kb)\
    .add_stim(stim_bank.get_and_format('good_bye', total_score=final_score))\
    .wait_and_continue(terminate=True)
```

### 6. 使用 `capture_response()` 获取反应

`capture_response()` 方法在 `StimUnit` 中将刺激呈现、计时、触发器和反应处理集成到一个单一的、可链式调用的函数中。它非常适合：

- 在预定义的反应窗口内检测和记录被试的反应
- 为性能分析确定正确与不正确的反应
- 通过高亮被试的选择来提供即时的视觉反馈

#### 特性
- 在精确的时间窗口内捕获和记录被试的选择
- 与刺激同步发送和接收硬件触发器（例如，EEG/fMRI）
- 区分正确与不正确的反应以进行性能度量
- 根据按键提供静态和动态的视觉反馈

#### 方法签名

```python
def capture_response(
    keys: list[str],
    duration: float | tuple[float, float],
    onset_trigger: int = None,
    response_trigger: int | dict[str, int] = None,
    timeout_trigger: int = None,
    terminate_on_response: bool = True,
    correct_keys: list[str] | None = None,
    highlight_stim: visual.BaseVisualStim | dict[str, visual.BaseVisualStim] = None,
    dynamic_highlight: bool = False
) -> StimUnit
```

- `key`: 有效的反应按键。
- `duration`: 反应窗口（固定或抖动范围）。
- `terminate_on_response`: 如果为 `True`，在有效反应后停止重绘。
- `correct_keys`: `keys` 的子集，被视为正确反应（用于状态记录）。
- `highlight_stim`: 一个刺激（或将按键映射到刺激的字典），用于在所选选项周围绘制。
- `dynamic_highlight`: 如果为 `True`，高亮会随着每次按键更新，而不仅仅是第一次。

以下是该签名和四个实际场景的说明。

#### 场景 1：简单的预期阶段（检测早期反应而不终止）
在 MID 任务的预期阶段，我们希望监控任何按键，但即使被试提前反应，也要继续呈现注视十字。在窗口结束后，我们记录是否有早期反应。

```python
# --- 预期阶段 ---
anti = make_unit(unit_label='anticipation') \
    .add_stim(stim_bank.get("fixation"))
anti.capture_response(
    keys=settings.key_list,
    duration=settings.anticipation_duration,
    onset_trigger=settings.triggers[f"{condition}_anti_onset"],
    terminate_on_response=False
)

# capture_response 返回后，检查并存储早期反应
early_response = anti.get_state("response", False)
anti.set_state(early_response=early_response)
anti.to_dict(trial_data)
```

- `terminate_on_response=False` 确保注视点在整个预期持续时间内都显示在屏幕上，无论是否有按键。
- 运行后，`anti.get_state("response")` 会告知是否有任何按键被按下。

#### 场景 2：需要反应的目标阶段
在 MID 任务的目标阶段，我们需要一个反应。这里我们使用默认设置，其中 `keys=settings.key_list` 中的按键算作潜在反应，没有定义单独的 `correct_keys`。默认情况下，`correct_keys=None`，因此 `keys=settings.key_list` 中的任何按键都被算作正确反应。

```python
# --- 目标阶段 ---
duration = controller.get_duration(condition)
target = make_unit(unit_label="target") \
    .add_stim(stim_bank.get(f"{condition}_target"))

target.capture_response(
    keys=settings.key_list,
    duration=duration,
    onset_trigger=settings.triggers[f"{condition}_target_onset"],
    response_trigger=settings.triggers[f"{condition}_key_press"],
    timeout_trigger=settings.triggers[f"{condition}_no_response"]
)

target.to_dict(trial_data)
```

- 默认情况下，`correct_keys=None`，因此 `keys` 中的任何按键都会被记录为反应。
- `response_trigger` 和 `timeout_trigger` 发送用于 EEG/行为标记的触发器。

#### 场景 3：检测正确与不正确的反应
在只有一个按键是正确的任务中（例如，左与右的点检测），指定 `correct_keys` 来记录命中与失误。

```python
# 根据目标位置确定哪个键是正确的
target_stim = stim_bank.get(f"{trial_info['target_position']}_target")
correct_key = (
    settings.left_key
    if trial_info['target_position'] == 'left'
    else settings.right_key
)

target_unit = make_unit(unit_label="target") \
    .add_stim(target_stim)

target_unit.capture_response(
    keys=settings.key_list,
    correct_keys=[correct_key],
    duration=settings.target_duration,
    onset_trigger=settings.triggers[f"{condition}_target_onset"],
    response_trigger=settings.triggers.get("key_press"),
    timeout_trigger=settings.triggers.get("no_response"),
    terminate_on_response=True
)

target_unit.to_dict(trial_data)
```

- `correct_keys` 筛选哪些反应算作命中。布尔值 `hit` 状态会相应设置。
- `terminate_on_response=True` 在第一次有效按键时结束试次。

#### 场景 4：高亮被试的选择
为了提供视觉反馈，传递一个高亮刺激的字典，以在所选选项周围绘制。使用 `dynamic_highlight=True` 允许被试在窗口期间更改他们的选择。

```python
cue = make_unit(unit_label="cue") \
    .add_stim(stim_bank.get('stimA')) \
    .add_stim(stim_bank.get('stimB'))

correct_key = settings.left_key  # 例如

cue.capture_response(
    keys=settings.key_list,
    correct_keys=[correct_key],
    duration=settings.cue_duration,
    onset_trigger=settings.triggers['cue_onset'] + marker_pad,
    response_trigger=settings.triggers['key_press'] + marker_pad,
    timeout_trigger=settings.triggers['no_response'] + marker_pad,
    terminate_on_response=False,
    highlight_stim={
        'f': stim_bank.get('highlight_left'),
        'j': stim_bank.get('highlight_right')
    },
    dynamic_highlight=False
)

cue.to_dict(trial_data)
```

- `highlight_stim` 将每个按键映射到一个视觉提示（例如，一个框或一个点）。
- 如果 `dynamic_highlight=True`，每次新的按键都会更新高亮，直到窗口结束。

```{Tip}
您还可以将一个 `dict` 传递给 `response_trigger`，以便为每个按键发送不同的触发码。
```

### 7. 生命周期钩子

生命周期钩子为您在关键试次事件中定义自定义行为提供了最大的灵活性——补充了像 `.capture_response()` 或 `.show()` 这样的内置方法。您可以精确地选择在 **开始**、**反应**、**超时** 和 **结束** 阶段运行什么代码。

下面是一个完整的示例，演示了每个钩子在实践中如何操作。请注意状态键如何自动以您的 `unit_label`（“demo”）为前缀：

```python
from psychopy import core, visual
from psychopy.hardware.keyboard import Keyboard
from psyflow import StimUnit

# 1. 设置
win = visual.Window([800,600], color='black', units='deg')
kb  = Keyboard()
unit = StimUnit('demo', win, kb)

# 2. 添加一个刺激
fix = visual.TextStim(win, text='+', height=1.0)
unit.add_stim(fix)

# 3. 定义钩子
@unit.on_start()
def start_hook(u):
    # 记录试次开始的时刻
    u.set_state(start_time=u.clock.getTime())
    print(f"[start_hook] prefix key 'demo_start_time' = {u.state['demo_start_time']}")

@unit.on_response(['space'])
def response_hook(u, key, rt):
    # 捕获空格键按键
    u.set_state(response=key, rt=rt)
    print(f"[response_hook] key={key}, rt={rt:.3f}")

@unit.on_timeout(1.0)
def timeout_hook(u):
    # 处理 1 秒内无反应的情况
    u.set_state(timeout=True)
    print("[timeout_hook] no response within 1.0s")

@unit.on_end()
def end_hook(u):
    # 完成并检查完整状态
    data = u.to_dict()
    print("[end_hook] final state:", data)

# 4. 运行试次
unit.run()
```

**解释：**

- **start_hook**：在记录全局开始时间之后、第一次屏幕翻转之前立即触发。
- **response_hook**：在按下 `'space'` 键时执行，提供 `(unit, key, rt)`。
- **timeout_hook**：如果在 1.0 秒内没有发生反应，则触发。
- **end_hook**：在试次结束后、记录之前运行，为您提供最后一次检查或修改数据的机会。

所有对 `u.set_state()` 的调用都会自动在 `unit.state` 中添加像 `demo_start_time`、`demo_response` 和 `demo_timeout` 这样的条目，您可以使用 `unit.to_dict()` 检索或通过 `unit.log_unit()` 在您的 PsychoPy 日志中查看。

除了装饰器，您还可以通过链式调用流畅地注册钩子，以获得简洁的代码：

```python
unit = StimUnit('chain_demo', win, kb)  

# 在一个语句中链式注册并运行
unit.add_stim(fix)  \
    .on_start(lambda u: u.set_state(start=time.time()))  \
    .on_response(['space'], lambda u, k, rt: u.set_state(response=k, rt=rt))  \
    .on_timeout(1.0, lambda u: u.set_state(timeout=True))  \
    .on_end(lambda u: print('Chained final state:', u.to_dict()))  \
    .run()
```
虽然 `.show()` 和 `.capture_response()` 捆绑了常见的模式，但您可以使用生命周期钩子来实现相同的行为，以获得更大的定制性。

#### 使用钩子复制 `show()`

```python
unit = StimUnit('show_demo', win, kb)
unit.add_stim(my_stim)

# 开始：发送 onset 触发器，记录时间
@unit.on_start()
def start_show(u):
    u.win.callOnFlip(u.send_trigger, trigger_onset)
    u.set_state(onset_time=u.clock.getTime())

# 在所需持续时间后超时：发送 offset 触发器，记录关闭时间
@unit.on_timeout(show_duration)
def end_show(u):
    u.send_trigger(trigger_offset)
    u.set_state(close_time=u.clock.getTime())

# 用于任何清理或记录的结束钩子
@unit.on_end()
def finalize_show(u):
    print('Show ended, state:', u.get_dict())

# 运行而不因响应而终止（不监听响应）
unit.run(terminate_on_response=False)
```
- `on_start` 设置了与翻转同步的 onset 触发器和时间戳。
- `on_timeout` 在 `show_duration` 后触发，镜像 `offset_trigger`。
- `on_end` 完成试次。

为了更流畅的风格，您可以链式地注册钩子和配置试次：
```python
make_unit('show_chain', win, kb) \
    .add_stim(my_stim) \
    .on_start(lambda u: (
        u.win.callOnFlip(u.send_trigger, trigger_onset),
        u.set_state(onset_time=u.clock.getTime())
    )) \
    .on_timeout(show_duration, lambda u: (
        u.send_trigger(trigger_offset),
        u.set_state(close_time=u.clock.getTime())
    )) \
    .on_end(lambda u: print('Show ended, state:', u.get_dict())) \
    .run(terminate_on_response=False)
```

#### 使用钩子复制 `.capture_response()`

```python
unit = StimUnit('resp_demo', win, kb)
unit.add_stim(response_stim)

# 开始：绘制刺激，翻转，发送 onset 触发器，重置时钟
@unit.on_start()
def start_resp(u):
    for s in u.stimuli:
        s.draw()
    u.win.callOnFlip(u.send_trigger, onset_trigger)
    u.win.callOnFlip(u.clock.reset)

# 反应：对于每个有效按键，发送触发器并设置状态
@unit.on_response(['f','j'])
def on_resp(u, key, rt):
    code = response_triggers[key]
    u.send_trigger(code)
    u.set_state(response=key, rt=rt, hit=(key in correct_keys))

# 超时：如果在反应窗口内没有反应
@unit.on_timeout(response_duration)
def on_timeout(u):
    u.send_trigger(timeout_trigger)
    u.set_state(response=None, timeout=True)

# 结束：记录和清理
@unit.on_end()
def end_resp(u):
    u.log_unit()

# 运行试次（钩子管理绘制和事件）
unit.run()
```
以链式方式实现：
```python
make_unit('resp_chain', win, kb) \
    .add_stim(response_stim) \
    .on_start(lambda u: (
        [s.draw() for s in u.stimuli],
        u.win.callOnFlip(u.send_trigger, onset_trigger),
        u.win.callOnFlip(u.clock.reset)
    )) \
    .on_response(['f','j'], lambda u, key, rt: (
        u.send_trigger(response_triggers[key]),
        u.set_state(response=key, rt=rt, hit=(key in correct_keys))
    )) \
    .on_timeout(response_duration, lambda u: (
        u.send_trigger(timeout_trigger),
        u.set_state(response=None, timeout=True)
    )) \
    .on_end(lambda u: u.log_unit()) \
    .run()
```
```{Warning}
在大多数情况下，使用 `.show()`、`.capture_response()` 和 `.wait_and_continue()` 涵盖了绝大多数任务需求，并经过了广泛测试。生命周期钩子提供了最大的灵活性，但它们不太常用，并且实际验证较少。我们没有广泛测试它们的用法。只有当您需要超出内置方法的自定义行为时才选择手动钩子——并谨慎行事。
```

### 8. 状态和数据管理

`StimUnit` 将所有与单元相关的值保存在其内部的 `unit.state` 字典中。使用以下方法可以使您的 StimUnit 数据井然有序、易于检索，并为分析或导出做好准备。

#### 使用 `set_state()` 记录或更新值

使用 `set_state()` 将键值数据记录到单元的状态中。

**示例**
```python
    # --- 反馈 ---
if early_response:
    delta = settings.delta * -1
    hit=False
else:
    hit = target.get_state("hit", False)
    if condition == "win":
        delta = settings.delta if hit else 0
    elif condition == "lose":
        delta = 0 if hit else settings.delta * -1
    else:
        delta = 0

hit_type = "hit" if hit else "miss"
fb_stim = stim_bank.get(f"{condition}_{hit_type}_feedback")
fb = make_unit(unit_label="feedback") \
    .add_stim(fb_stim) \
    .show(duration=settings.feedback_duration, onset_trigger=settings.triggers.get(f"{condition}_{hit_type}_fb_onset"))
fb.set_state(hit=hit, delta=delta).to_dict(trial_data)
```
在这个片段中，我们：

1. **创建并显示** 一个标记为“feedback”的反馈 `StimUnit`，带有正确的刺激和触发器。
2. **计算** 试次是否命中（`True`/`False`）并确定 `delta` 值（+Δ, –Δ, 或 0）。
3. **记录** 这些值到单元的内部状态中，使用 `set_state()`（默认情况下会添加前缀）。
4. **导出** 所有存储的状态条目到您的 `trial_data` 字典中，用于记录或进一步分析。

注意：`set_state()` 使用 **前缀** 来控制键的存储方式。

**默认** (单元标签): 键存储为 `<unit_label>_<key>`

```python
fb.set_state(hit=True, delta=0.5)
# 存储 'feedback_hit' 和 'feedback_delta'
```
 
**原始** (`prefix=''`)：键按原样存储

```python
fb.set_state(prefix='', hit=True, delta=0.5)
# 存储 'hit' 和 'delta'
```
**自定义** (`prefix='special'`)：键以 'special_' 为前缀

```python
fb.set_state(prefix='special', hit=True)
# 存储 'special_hit'
```

**前缀行为总结**
| 模式 | 前缀 | 存储的键 |
| --- | --- | --- |
| 默认 | (单元标签) | feedback_hit, feedback_delta |
| 原始 | '' | hit, delta |
| 自定义 | 'special' | special_hit |

```{Tip}
`set_state` 是 **可链式调用的**：它返回同一个 `StimUnit`，所以您可以链式调用：`unit.set_state(block=2, trial=5).set_state(condition='win')`
```

**自动状态条目总结**

一些 `StimUnit` 方法会在没有显式调用 `set_state()` 的情况下填充内部状态。这里是一个快速参考：

| 方法 | 在 `.state` 中设置的键 | 注意 |
|---|---|---|
| `run()` | `global_time` | 开始前的实验范围时间戳 |
| | `onset_time`, `onset_time_global`, `flip_time` | 在第一次 `win.flip()` 时记录 |
| | `close_time`, `close_time_global` | 在试次结束时（反应或超时） |
| | `timeout_triggered`, `duration` | 如果发生超时 |
| `show()` | `duration` | 最终选择的持续时间 |
| | `onset_time`, `onset_time_global`, `onset_trigger` | 在刺激开始时 |
| | `flip_time` | 开始后翻转的时间 |
| | `close_time`, `close_time_global`, `offset_trigger` | 在呈现结束时 |
| `capture_response()` | `duration`, `onset_time`, `onset_time_global`, `flip_time` | 反应窗口设置 |
| | `hit`, `correct_keys`, `response`, `key_press`, `rt` | 在反应时 |
| | `response_trigger`, `close_time`, `close_time_global` | 反应触发器和结束时间 |
| | `timeout_trigger`, `hit=False`, `response=None`, `rt=None` | 在超时时 |
| `wait_and_continue()` | `wait_keys`, `onset_time`, `onset_time_global`, `flip_time` | 在显示开始时 |
| | `response`, `response_time`, `close_time`, `close_time_global` | 当按下继续键时 |

使用此表可以快速查看哪些状态值是自动填充的，这样您就知道可能还需要哪些额外的 `set_state()` 调用。

```{Note}
对于 `capture_response()`，`hit` 表示反应是正确的按键。
```

#### 使用 `get_state()` 检索值
当您调用 `get_state()` 时，它首先查找确切的键，然后查找带前缀的形式（使用您的 unit_label 或提供的
前缀），如果两者都找不到，则返回默认值。

  ```python
  # 如果 unit_label 是 'cue'，则读取 'response' 或 'cue_response'
  resp = unit.get_state('response', default=None)
  # 强制使用不同的前缀查找，它会读取 'custom_response'
  resp = unit.get_state('response', default=0, prefix='custom')
  ```

#### 使用 `.to_dict()` 导出所有状态

**`to_dict(target=None)`**
  - 如果没有给出 `target`，则返回 `StimUnit` 实例（用于链式调用），并让您检查 `unit.state`。
  - 如果您传入一个字典，它会将 `unit.state` 合并到该字典中并返回 `StimUnit`。
  
  ```python
    # 在一个预期阶段之后：
    anti = make_unit('anticipation')\
        .add_stim(stim_bank.get('fixation'))\
        .capture_response(keys=settings.keys, duration=settings.anticipation_duration)
    # 检查被试是否提前反应
    early = anti.get_state('response', default=None)
    # 记录这个自定义标志并合并到主 trial_data 中
    anti.set_state(early_response=early)\
        .to_dict(trial_data)

    # 在目标阶段：
    target = make_unit('target')\
        .add_stim(stim_bank.get(f"{condition}_target"))\
        .capture_response(keys=settings.keys, duration=duration)
    # 导出结果
    target.to_dict(trial_data)
  ```

#### 使用 `.log_unit()` 在内部记录状态

`log_unit()` 将 `unit.state` 中的每个键值对写入 `data/*.log` 中的日志分数。它使用 PsychoPy 的 `logging.data()`，默认情况下，它会将带时间戳的条目附加到实验日志文件或控制台。它在 `StimUnit` 类中自动调用，所以您通常不需要手动调用它。

**记录什么？** `unit.state` 中当前的所有条目，包括：

| 状态键示例 | 描述 |
|---|---|
| `trial_block`, `trial_trial` | 试次前标识符 |
| `onset_time`, `flip_time` | 来自 `.show()` 或 `.run()` 的时间戳 |
| `hit`, `response`, `rt` | 来自 `capture_response()` 的反应指标 |
| `feedback_hit`, `feedback_delta` | 来自您的 `set_state()` 调用的自定义值 |

如果您需要在其他点进行调试的单独日志，您可以手动调用 `unit.log_unit()` 来快照当前状态。

## 后续步骤

现在您已经了解了如何使用 `StimUnit`，您可以：

- 探索 [BlockUnit 教程](build_blocks.md) 来将试次组织成组块
- 了解 [StimBank](build_stimulus.md) 以进行灵活的刺激管理
- 查看 [发送触发器](send_trigger.md) 以用于 EEG/MEG 实验
