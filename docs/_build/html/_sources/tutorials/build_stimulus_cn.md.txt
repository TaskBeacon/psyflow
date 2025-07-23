# StimBank: 灵活的刺激管理

## 概述

`StimBank` 是一个用于 PsychoPy 实验的强大刺激管理系统，解决了几个常见的挑战：

- **集中式刺激管理**：在一个地方定义所有视觉和听觉刺激。
- **多种定义方法**：通过 Python 装饰器或配置文件（YAML/字典）注册刺激。
- **延迟加载**：仅在首次访问时实例化刺激，以减少初始加载时间。
- **动态格式化**：将运行时值插入文本刺激中，而无需重新定义它们。
- **批量操作**：高效地预览、导出、验证和分组刺激。

无论您是运行简单的行为任务还是复杂的多模态协议，`StimBank` 都能帮助您保持与刺激相关的代码和配置的整洁、一致和可维护性。

## 主要功能

| 功能 | 描述 |
| --- | --- |
| 双重注册 | 通过装饰器或声明式地通过 YAML/字典定义刺激 |
| 延迟实例化 | 延迟对象创建直到需要时 |
| 分组 | 按前缀或显式列表检索相关刺激 |
| 文本格式化 | 使用 Python 风格的占位符和 `get_and_format()` |
| 刺激重建 | 使用 `rebuild()` 动态覆盖属性 |
| 预览功能 | 批量视觉检查或播放刺激 |

## 快速参考

| 目的 | 方法 | 示例 |
| --- | --- | --- |
| 初始化 | `StimBank(win)` | `bank = StimBank(win)` |
| 注册（装饰器） | `@bank.define(name)` | `@bank.define("fixation")` |
| 注册（字典/YAML） | `bank.add_from_dict(dict)` | `bank.add_from_dict(config)` |
| 获取刺激 | `bank.get(name)` | `stim = bank.get("target")` |
| 获取多个 | `bank.get_selected(list)` | `stims = bank.get_selected(["fix","cue"])` |
| 按前缀获取 | `bank.get_group(prefix)` | `cues = bank.get_group("cue_")` |
| 格式化文本 | `bank.get_and_format(name, **kw)` | `bank.get_and_format("msg", name="John")` |
| 修改刺激 | `bank.rebuild(name, **kw)` | `bank.rebuild("target", fillColor="blue")` |
| 预览全部 | `bank.preview_all()` | `bank.preview_all()` |
| 导出配置 | `bank.export_to_yaml(file_path)` | `bank.export_to_yaml("stimuli.yaml")` |

## 详细使用指南

### 1. 初始化

使用您的 PsychoPy 窗口创建一个 `StimBank` 实例：

```python
from psychopy.visual import Window
from psyflow import StimBank

win = Window(size=[1024, 768], color="black", units="deg")
stim_bank = StimBank(win)
```

或者，传递一个初始配置字典或从 YAML 加载：

```python
stim_config = {
    "instructions": {
        "type": "text",
        "text": "Press SPACE to begin",
        "height": 0.7,
        "color": "white",
        "pos": [0, 3]
    },
    "left_target": {"type": "circle", "radius": 0.8, "pos": [-5, 0], "fillColor": "blue"},
    "image_stimulus": {"type": "image", "image": "images/stimulus.png", "size": [4, 3]}
}
stim_bank = StimBank(win, config=stim_config)
```

### 2. 支持的刺激

`StimBank` 目前支持以下刺激类型。在字典/YAML 定义中，使用 `type` 字段中的这些键来选择适当的类：

| 键 | 类 | 描述 |
| --- | --- | --- |
| text | TextStim | 单行文本 |
| textbox | TextBox2 | 多行、自动换行的文本框 |
| circle | Circle | 填充或描边的圆形 |
| rect | Rect | 矩形 |
| polygon | Polygon | 由顶点定义的任意多边形 |
| image | ImageStim | 静态位图图像 |
| shape | ShapeStim | 通过顶点列表自定义形状 |
| movie | MovieStim | 视频播放 |
| sound | Sound | 使用 PsychoPy Sound 进行音频播放 |

```{note}
了解刺激参数的好地方是 PsychoPy 视觉 API 页面 (https://www.psychopy.org/api/visual/)。我们将在开发新任务时根据需要添加对其他刺激类型的支持。
```

#### 参数验证

通过 `add_from_dict` 加载定义时，您可以根据构造函数签名验证规范：

```python
# 验证但不引发错误（打印警告）
stim_bank.validate_dict(config, strict=False)

# 验证并在任何问题上引发错误
stim_bank.validate_dict(config, strict=True)
```

这将检查：

- **缺少必需参数**（没有默认值的参数）
- **未知参数**（拼写错误或不支持的字段）

#### 检查可用参数

要确切查看每个刺激类接受哪些关键字参数（及其默认值），请使用：

```python
stim_bank.describe("fixation")
```

示例输出：

```
Description of 'fixation' (TextStim)
  - text: required
  - pos: default=(0, 0)
  - color: default='white'
  - height: default=1.0
  - bold: default=False
  ...
```

这个内置的帮助程序可让您在编写字典/YAML 规范或调用 `rebuild()` 时发现所有支持的参数及其默认值。

### 3. 注册刺激

#### 方法 1：使用装饰器

通过工厂函数装饰器进行编程注册：

```python
from psychopy.visual import TextStim, Circle

@stim_bank.define("fixation")
def make_fixation(win):
    return TextStim(win, text="+", color="white", height=1.0)

@stim_bank.define("target")
def make_target(win):
    return Circle(win, radius=0.5, fillColor="red", lineColor="white", lineWidth=2)
```

您还可以通过组装子元素和覆盖方法来构建复合刺激。

#### 方法 2：使用字典、YAML 或 `load_config`

对于声明式刺激定义，您有两个主要选项：

**1. 手动加载字典/YAML**

使用 Python 的 `yaml` 库或普通字典：

```python
import yaml
# a) 加载 YAML 文件
yaml_config = yaml.safe_load(open("config.yaml"))
# b) 如果存在，则提取嵌套的 'stimuli' 部分
stim_config = yaml_config.get('stimuli', yaml_config)
# c) 注册定义
stim_bank.add_from_dict(stim_config)
```

或在代码中直接使用字典定义：

```python
stim_config = {
    "instructions": {
        "type": "text",
        "text": "Press SPACE to begin",
        "height": 0.7,
        "color": "white",
        "pos": [0, 3]
    },
    "left_target": {"type": "circle", "radius": 0.8, "pos": [-5, 0], "fillColor": "blue"}
}
stim_bank.add_from_dict(stim_config)
```

**2. 使用内置的 `load_config` 帮助程序**

`config.yaml` 通常包含多个部分（例如 `settings`、`triggers`、`stimuli`），`load_config()` 会自动读取 `config.yaml` 并返回一个字典，其中 `stim_config` 键仅包含相关的刺激定义。

```python
from psyflow.config import load_config
# 加载所有配置部分
cfg = load_config()
# 仅提取刺激定义
stim_config = cfg['stim_config']

# 使用预加载的定义初始化 bank 并链接进一步的设置
stim_bank = (
    StimBank(win, stim_config)
    .convert_to_voice('instruction_text')
    .preload_all()
)
```

### 4. 检索和预览刺激

注册刺激后，您可以按需获取和检查它们。

**单个检索**：按名称获取单个刺激（首次使用时实例化）。

  ```python
  fixation = stim_bank.get("fixation")
  ```

**选择性检索**：通过列出名称获取特定的子集。

  ```python
  choices = stim_bank.get_selected(["left_target", "right_target"])
  ```

**分组检索**：获取其键共享公共前缀的所有刺激。

  ```python
  cues = stim_bank.get_group("cue_")
  ```

所有检索方法在创建后都会缓存实例，因此重复调用速度很快。

#### 预览刺激

在将刺激嵌入试验代码之前，通常需要预览其外观或音频以验证位置、颜色、大小或播放行为：

```python
stim_bank.preview_all()                    # 显示或播放每个注册的刺激
stim_bank.preview_selected(["fixation"])   # 仅指定的刺激
stim_bank.preview_group("feedback_")       # 所有带有 "feedback_" 前缀的刺激
```
```{tip}
使用预览及早发现布局或样式问题，而不是在实时试验中。
```

#### 列出和描述刺激

**列出所有键**：查看注册了哪些刺激。
  ```python
  print(stim_bank.keys())
  ```

**检查是否存在**：测试名称是否已注册。
  ```python
  if stim_bank.has("target"):
      # 继续
  ```

**描述参数**：检查任何刺激的构造函数参数和默认值。
  ````python
  stim_bank.describe("fixation")
  # 打印每个关键字参数及其默认值（如果没有则为“必需”）
  ````


### 5. 动态文本格式化

`get_and_format()` 仅支持 `TextStim` 和 `TextBox2` 刺激。它返回一个具有相同属性的新实例，但格式化的 `text` 字段除外。将其应用于其他刺激类型将引发 `TypeError`。

您只需在配置（字典或 YAML）中使用 Python 风格的占位符定义文本，并注入运行时值。

例如，当您需要在每个块后显示一个摘要屏幕，其中包含动态值和用户提示时。以下是如何配置和呈现多行中断消息。

您可以在 YAML 文件中或直接在 Python 中作为字典定义 `block_break` 刺激：

```yaml
# config.yaml
stimuli:
  block_break:
    type: text
    text: |
      {block_num}/{total_blocks} Done
      Score: {score}
      Press Enter to proceed
    color: white
    height: 0.78
```

```python
# 在代码中，使用字典
stim_bank.add_from_dict({
    "block_break": {
        "type": "text",
        "text": (
            "{block_num}/{total_blocks} Done
"
            "Score: {score}
"
            "Press Enter to proceed"
        ),
        "color": "white",
        "height": 0.78
    }
})
```

**运行时示例**：

```python
# 在块结束时：
block_trials = block.get_all_data()
score = sum(t.get('cue_delta', 0) for t in block_trials)

# 格式化并显示中断屏幕
StimUnit('block',win,kb).add_stim(stim_bank.get_and_format('block_break', 
                                                                block_num=block_i+1, 
                                                                total_blocks=settings.total_blocks,
                                                                score=score)).wait_and_continue()
```

在此模式中，占位符 `{block_num}`、`{total_blocks}` 和 `{score}` 在运行时被替换，生成的 `TextStim` 被传递给 `StimUnit` 以进行显示和输入处理。

注意：`get_and_format()` 通过手动重建新的文本刺激而不是尝试对原始刺激进行深层复制来工作。在内部，它检查 `TextStim` 或 `TextBox2` 的构造函数签名，从其 `__dict__` 中提取原始实例的所有存储的关键字参数，用您的格式化字符串替换文本字段，然后使用该参数集调用类构造函数。这种方法避免了改变 StimBank 中缓存的版本，但由于 PsychoPy 对象不支持真正的深层复制，一些复杂的属性——尤其是在 TextBox2 中（例如换行行为或锚点）——可能无法与原始版本完全一致。如果您在使用 `TextBox2` 时遇到意外的布局或格式问题，请考虑使用 `TextStim` 类型或使用新的 `text` 覆盖的 `rebuild()`。


### 6. 重建和修改刺激

`StimBank.rebuild()` 允许您动态覆盖刺激参数，而无需改变原始定义。传递与刺激构造函数匹配的关键字参数以创建新实例。如果要覆盖缓存的版本，请使用 `update_cache=True`。

**基本示例**：

```python
# 创建一个蓝色的 "target" 变体，而不改变原始的
blue_target = stim_bank.rebuild("target", fillColor="blue", radius=0.7)
# 原始的保持不变
red_target = stim_bank.get("target")  # 仍然是红色，半径=0.5
```

以下是来自概率逆转学习（PRL）任务的一个实际示例，展示了如何在 `run_trial` 函数中以及何时重建刺激。在每个试验中，两个选择刺激根据 `condition` 和参与者历史交换位置：

```python
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_sender=None):
    """
    单个 PRL 试验序列：
      1. 注视
      2. 提示显示 + 响应收集
      3. 随机反馈
      4. 试验间间隔
    """
    trial_data = {"condition": condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)
    marker_pad = controller.reversal_count * 10

    # 1) 注视
    make_unit(unit_label="fixation") \
        .add_stim(stim_bank.get("fixation")) \
        .show(duration=settings.fixation_duration,
              onset_trigger=settings.triggers.get("fixation_onset") + marker_pad) \
        .to_dict(trial_data)

    # 2) 提示 + 响应收集
    # 根据条件重建左/右刺激位置
    if condition == "AB":
        stima = stim_bank.rebuild("stima", pos=(-4, 0))
        stimb = stim_bank.rebuild("stimb", pos=(4, 0))
    else:  # "BA"
        stimb = stim_bank.rebuild("stimb", pos=(-4, 0))
        stima = stim_bank.rebuild("stima", pos=(4, 0))

    # 确定正确的响应键
    correct_label = controller.current_correct
    correct_side = "left" if correct_label == "stima" else "right"
    correct_key = settings.left_key if correct_side == "left" else settings.right_key

    # 构建并显示提示单元
    cue_unit = make_unit(unit_label="cue")
    cue_unit.add_stim(stima).add_stim(stimb)
    cue_unit.capture_response(
        key_list=[settings.left_key, settings.right_key],
        correct_key=correct_key,
        duration=settings.cue_duration,
        onset_trigger=settings.triggers.get("cue_onset") + marker_pad
    ).to_dict(trial_data)

    # 3) 为简洁起见，省略了反馈和 ITI...

    return trial_data
```
在此示例中，使用 `rebuild()` 使您可以从单个基本定义开始，仅调整需要更改的参数（例如交换左/右位置），而无需创建全新的刺激条目。通过传递构造函数覆盖（例如 `pos`、`fillColor`、`size` 或 `opacity`），您可以保留完全的运行时灵活性，以根据当前条件或参与者数据自定义刺激。因为 `rebuild()` 默认情况下不会覆盖缓存的实例，所以原始定义保持不变；如果您确实希望在后续试验中保留更改，只需包含 `update_cache=True`。此模式可使您的刺激库保持紧凑，并避免为每个可能的变体增生几乎相同的定义。


#### `get_and_format()` 与 `rebuild()`
| 功能 | `get_and_format()` | `rebuild()` |
|---|---|---|
| **目的** | 仅更新 **文本** 内容 | 创建具有任何覆盖属性的新实例 |
| **支持的刺激** | 仅 `TextStim`、`TextBox2` | 通过注册的工厂支持所有刺激类型 |
| **可修改的属性** | 仅文本内容 | 任何构造函数参数（`pos`、`fillColor`、`size` 等） |
| **机制** | 从原始副本中复制存储的 kwargs，替换 `text`，然后调用构造函数 | 使用基本 kwargs + 覆盖调用注册的工厂 |
| **缓存行为** | 从不覆盖缓存 | 默认情况下 **不** 覆盖；使用 `update_cache=True` 替换 |
| **最适合** | 视觉布局保持不变的简单标签或分数更新 | 复杂或多属性覆盖；当 TextBox2 格式不可靠时 |
| **限制** | 无法更改非文本属性；换行/锚定的深层复制问题 | 需要有效的工厂定义；始终实例化一个新对象 |


### 7. 文本到语音转换

`StimBank` 支持 **文本到语音（TTS）** 转换，以增强可访问性并标准化不同语言的指令传递。

**为什么重要**：使用文本到语音可以提高可访问性——特别是对于儿童、老年参与者或识字率低的人。它确保了不同语言版本之间的一致语音传递，并消除了为每次翻译录制人声的需要。通过使用标准化的合成语音，您可以减少由不同实验者引入的可变性，从而在会话和站点之间保持一致性。

**工作原理**：`StimBank` 使用微软的 `edge-tts`，这是一个基于云的 TTS API，可将文本转换为 MP3 音频。生成的文件保存在 `assets/` 文件夹下，如果已存在则跳过（除非 `overwrite=True`），然后自动注册为新的 `Sound` 刺激。

```note
TTS 生成需要互联网连接。离线工具存在，但通常会产生质量较低的音频。
```

#### 将现有文本刺激转换为语音

```python
win, kb = initialize_exp(settings)
# 设置刺激库
stim_bank = StimBank(win,cfg['stim_config'])\
    .convert_to_voice('instruction_text')\
    .preload_all()
```

这会在 `assets/` 中创建 `instruction_text_voice.mp3` 和 `good_bye_voice.mp3`，并注册名为 `instruction_text_voice` 和 `good_bye_voice` 的刺激。

 如果您计划重新生成语音，请先删除 `assets/` 中先前生成的文件。选择与文本语言匹配的 TTS 语音以确保发音自然。默认值为 `zh-CN-XiaoxiaoNeural`。

#### 从自定义文本添加语音

```python
stim_bank.add_voice(
    stim_label="welcome_voice",
    text="ようこそ。タスクを開始します。",
    voice="ja-JP-NanamiNeural"
)
```

注册 `welcome_voice` 并保存 `assets/welcome_voice.mp3` 以供播放。

#### 语音选择

使用帮助程序列出支持的语音：

```python
from psyflow.tts_utils import list_supported_voices

# 所有语音
tsv = list_supported_voices(human_readable=True)
# 按语言代码筛选
ts_jp = list_supported_voices(filter_lang="ja", human_readable=True)
```

示例输出：

| ShortName | Locale | Gender | Personalities | FriendlyName |
| --- | --- | --- | --- | --- |
| af-ZA-AdriNeural | af-ZA | Female | Friendly, Positive | Microsoft Adri Online (Natural) - Afrikaans (South Africa) |
| af-ZA-WillemNeural | af-ZA | Male | Friendly, Positive | Microsoft Willem Online (Natural) - Afrikaans (South Africa) |

或者，在此 [支持的语音 Gist](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462) 中查看完整列表。

#### 提示和注意事项

- **占位符限制**：TTS 不支持动态占位符（例如 `{duration}`）。仅使用静态文本。
- **需要互联网连接**：生成依赖于微软的云服务——确保网络访问。
- **覆盖**：传递 `overwrite=True` 以强制重新生成，但要谨慎使用。
- **语音-语言匹配**：始终将语音区域设置与文本语言匹配以获得自然的输出。
- **预览音频**：在完整实验之前验证 `assets/` 中的 MP3 文件。如果文件为空或损坏，请删除并重新生成。


## 后续步骤

现在您已经了解了如何使用 `StimBank`，您可以：

- **构建试验**：探索 [StimUnit 教程](build_stimunit_cn.md) 以了解如何创建试验序列
- **组织块**：查看 [BlockUnit 教程](build_blocks_cn.md) 以将试验组织成块
- **发送触发器**：了解有关 [触发器发送](send_trigger_cn.md) 的信息以进行 EEG/MEG 实验集成