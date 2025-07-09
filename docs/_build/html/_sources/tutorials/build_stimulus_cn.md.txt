# StimBank：灵活的刺激管理

## 概述

`StimBank` (刺激银行) 是 `psyflow` 中用于管理、创建和重用 PsychoPy 刺激的中央枢纽。它将您的刺激定义从实验逻辑中分离出来，使您的代码更清晰、更易于维护。

通过 `StimBank`，您可以：

-   在 `config.yaml` 中以声明方式定义所有刺激。
-   按名称动态创建和检索刺激。
-   在运行时格式化刺激文本（例如，插入分数或条件名称）。
-   预加载刺激以确保精确的呈现时间。
-   轻松地在不同的试次（trials）和单元（units）中重用相同的刺激。

## 核心概念

`StimBank` 的工作流程很简单：

1.  **定义**: 您在 `config.yaml` 文件中的 `stimuli` 部分定义所有刺激及其属性。
2.  **初始化**: 您在实验开始时创建一个 `StimBank` 的单一实例。
3.  **检索**: 在您的试次逻辑中，您通过名称从 `StimBank` 中 `.get()` 刺激。

这种方法遵循“关注点分离”的原则，将您的刺激内容（在 YAML 中）与您的实验逻辑（在 Python 中）分开。

## 详细使用指南

### 1. 在 `config.yaml` 中定义刺激

您的所有刺激都定义在 `config/config.yaml` 文件中的 `stimuli` 键下。每个刺激都有一个唯一的名称（例如，`fixation`，`win_feedback`）和一组属性。

-   `type`: 指定要创建的 PsychoPy 对象的类型（例如，`text`，`circle`，`sound`）。
-   其他键: 任何其他键都直接作为关键字参数传递给该 PsychoPy 对象的构造函数。

这是一个示例 `stimuli` 配置：

```yaml
stimuli:
  fixation:
    type: text
    text: '+'
    color: white
    height: 0.8

  win_target:
    type: circle
    radius: 1.5
    fillColor: gold
    lineColor: white

  loss_feedback:
    type: text
    text: "您输了 {last_loss} 分"
    color: red
    pos: [0, 2]

  pop_sound:
    type: sound
    value: 'assets/sounds/pop.wav'
```

在这个例子中：
-   `fixation` 是一个白色的文本刺激。
-   `win_target` 是一个金色的圆形。
-   `loss_feedback` 是一个红色的文本刺激，其中包含一个 f-string 风格的占位符 `{last_loss}`。
-   `pop_sound` 是一个声音刺激。

### 2. 初始化 StimBank

在您的主实验脚本中，在设置好您的 PsychoPy 窗口之后，创建 `StimBank` 的一个实例。

```python
from psychopy import visual
from psyflow.stim_bank import StimBank

# 1. 创建您的 PsychoPy 窗口
win = visual.Window(size=[800, 600], color='black', units='deg')

# 2. 从您的配置文件中加载刺激定义
# (假设 stim_config 是从 config.yaml 加载的字典)
stim_config = {
    'fixation': {'type': 'text', 'text': '+', 'color': 'white'},
    'target': {'type': 'circle', 'radius': 1.0, 'fillColor': 'blue'}
}

# 3. 创建 StimBank 实例
stim_bank = StimBank(win, stim_config)
```

`StimBank` 现在已经准备好按需创建刺激了。

### 3. 检索刺激

使用 `.get()` 方法按名称从 `StimBank` 中检索刺激。

```python
# 检索一个简单的注视十字
fixation_cross = stim_bank.get('fixation')

# 在一个 StimUnit 中使用它
unit = StimUnit('fixation_trial', win, kb)
unit.add_stim(fixation_cross)
unit.show(duration=1.0)
```

`StimBank` 会缓存刺激，所以如果您多次调用 `.get('fixation')`，您将收到对完全相同的 PsychoPy 对象的引用。这对于高效地重用刺激非常有用。

### 4. 动态格式化文本

`StimBank` 最强大的功能之一是能够在检索时动态格式化文本刺激。如果在您的 `config.yaml` 中定义的 `text` 字段包含 f-string 风格的占位符（例如，`{score}`），您可以在调用 `.get()` 时提供值来填充它们。

假设您的 `config.yaml` 中有这个：

```yaml
stimuli:
  score_display:
    type: text
    text: "分数: {current_score}"
    color: white
```

您可以像这样格式化和检索它：

```python
# 在运行时提供 current_score 的值
score_text = stim_bank.get('score_display', current_score=95)

# score_text.text 现在是 "分数: 95"
```

这对于显示动态反馈、分数更新或特定于试次的指令非常有用。

### 5. 预加载刺激

为了确保精确的计时并避免在第一次呈现刺激时出现延迟，您可以预加载部分或全部刺激。这会在它们被需要之前在内存中创建 PsychoPy 对象。

```python
# 预加载所有在 config.yaml 中定义的刺激
stim_bank.preload_all()

# 只预加载特定的刺激
stim_bank.preload(['fixation', 'win_target', 'loss_target'])
```

一个好的做法是在实验开始时，在任何试次开始之前，调用 `stim_bank.preload_all()`。

## 完整的工作流程示例

下面是一个将所有部分组合在一起的简短示例：

```python
from psychopy import visual
from psyflow.stim_bank import StimBank
from psyflow.stim_unit import StimUnit
from psychopy.hardware.keyboard import Keyboard

# 1. 设置
win = visual.Window(size=[800, 600], color='black')
kb = Keyboard()

# 2. 从 YAML 加载的刺激定义
stim_config = {
    'fixation': {'type': 'text', 'text': '+'},
    'feedback': {'type': 'text', 'text': '你得了 {points} 分!'}
}

# 3. 初始化 StimBank 并预加载
stim_bank = StimBank(win, stim_config)
stim_bank.preload_all()

# --- 试次循环 ---
for trial in range(5):
    # 4. 呈现一个注视十字
    fixation_unit = StimUnit('fix', win, kb)
    fixation_unit.add_stim(stim_bank.get('fixation'))
    fixation_unit.show(duration=0.5)

    # (这里是您的核心试次逻辑...)
    points_this_trial = 10  # 假设

    # 5. 呈现动态反馈
    feedback_unit = StimUnit('feedback', win, kb)
    feedback_stim = stim_bank.get('feedback', points=points_this_trial)
    feedback_unit.add_stim(feedback_stim)
    feedback_unit.show(duration=1.0)

win.close()
```

## 后续步骤

现在您已经掌握了 `StimBank`，请继续学习 `StimUnit` 教程，了解如何使用您创建的刺激来构建和运行单个试次。
