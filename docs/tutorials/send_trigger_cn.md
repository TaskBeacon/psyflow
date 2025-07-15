# TriggerSender: 发送硬件触发器

## 概述

`TriggerSender` 类提供了一种灵活、独立于设备的方式，用于向外部记录设备（例如 EEG、MEG、眼动仪）发送事件代码（触发器）。通过包装特定于设备的发送功能，它可以保持实验代码的整洁，添加可选的前置和后置钩子，强制执行精确的计时延迟，甚至支持在没有硬件的情况下进行开发的模拟模式。

`TriggerSender` 解决了神经科学实验中几个常见的挑战：

- **硬件抽象**：将您的实验逻辑与特定于设备的 I/O 分离。
- **模拟测试**：在任何机器上进行开发和调试——无需数据采集硬件。
- **精确定时**：在每次发送触发器后自动插入可配置的延迟。
- **自定义钩子**：在每次触发器前后立即运行用户提供的回调。
- **强大的日志记录**：对无效代码发出警告，捕获错误，并在 PsychoPy 的日志中记录触发器事件。

## 主要功能

| 功能 | 描述 |
| --- | --- |
| 设备无关 | 接受任何 Python 函数将整数代码传输到您的设备 |
| 模拟模式 | 打印触发器代码而不是发送，用于开发/测试 |
| 可配置延迟 | 每次发送后等待指定的持续时间（默认为 0.001 秒） |
| 前/后钩子 | 在发送每个触发器之前和/或之后执行用户函数 |
| 错误处理 | 捕获异常，记录错误，并在不崩溃的情况下继续 |
| 日志支持 | 通过 PsychoPy 的日志系统记录警告和触发器事件 |

## 快速参考

| 目的 | 方法 | 示例 |
| --- | --- | --- |
| 在模拟模式下初始化 | `TriggerSender(mock=True)` | `sender = TriggerSender(mock=True)` |
| 为硬件初始化 | `TriggerSender(trigger_func=your_send_function)` | `sender = TriggerSender(trigger_func=send_code)` |
| 发送触发器 | `sender.send(code)` | `sender.send(32)` |

## 详细使用指南

### 1. 入门：用于开发的模拟模式

使用模拟模式在没有任何硬件的情况下构建和测试您的实验逻辑：

```python
from psyflow import TriggerSender

# 在模拟模式下初始化
trigger_sender = TriggerSender(mock=True)

# 控制台输出：“[MockTrigger] Sent code: 1”
trigger_sender.send(1)

# 控制台输出：“[MockTrigger] Sent code: 255”
trigger_sender.send(255)
```

### 2. 连接到真实硬件

```{Warning}
在以下示例中，只有串行 (UART) 端口示例经过作者测试。EGI、Neuroscan、Brain Products (RDA) 和其他设备的代码片段是从在线资源收集的，尚未在实际硬件上进行验证。如果您测试这些或为其他设备（例如眼动仪）实现触发器，请分享您的代码，以便我们保持本文档的最新状态。
```

当您的设备准备就绪时，提供一个函数以通过 `trigger_func` 参数将整数代码发送到您的设备。您可以为串行端口、USB 接口、LabJack 设备或任何其他硬件调整此模式：只需提供一个接受整数并将其传输的函数即可。

#### 示例：串行 (UART) 端口（已测试）

```python
from psyflow import TriggerSender
import serial
#ser = serial.serial_for_url("loop://", baudrate=115200, timeout=1)
ser = serial.Serial("COM3", baudrate=115200, timeout=1)
if not ser.is_open:
    ser.open()

# 创建 TriggerSender
trigger_sender = TriggerSender(
    trigger_func=lambda code: ser.write(bytes([1, 225, 1, 0, code])),
    post_delay=0.005
)

# 使用 psyflow BlockUnit 回调的示例用法

trigger_sender.send(settings.triggers.get("exp_onset"))

block = BlockUnit(
    block_id=f"block_{block_i}",
    block_idx=block_i,
    settings=settings,
    window=win,
    keyboard=kb
).generate_conditions() \
    .on_start(lambda b: trigger_sender.send(settings.triggers.get("block_onset"))) \
    .on_end(lambda b: trigger_sender.send(settings.triggers.get("block_end"))) \
    .run_trial(partial(run_trial, stim_bank=stim_bank, controller=controller, trigger_sender=trigger_sender)) \
    .to_dict(all_data)

ser.close()
```

#### 示例：并行 (LPT) 端口（尚未测试）

```python
from psychopy import parallel, logging, core
from psyflow import TriggerSender

try:
    # 根据您的系统调整地址（例如，Windows 上的“0x0378”）
    port = parallel.ParallelPort(address='/dev/parport0')
    send_code = lambda c: port.setData(c)

    trigger_sender = TriggerSender(trigger_func=send_code)
    trigger_sender.send(128)  # 将 128 发送到并行端口

except Exception as e:
    print(f"无法初始化并行端口：{e}\n回退到模拟模式。")
    trigger_sender = TriggerSender(mock=True)
    trigger_sender.send(128)  # 打印到控制台
```

#### 示例：EGI NetStation（尚未测试）

```python
from egi_pynetstation.NetStation import NetStation
from psyflow import TriggerSender

# 为您的 NetStation 和放大器配置 IP 和端口
IP_ns = '10.10.10.42'      # NetStation 主机 IP
IP_amp = '10.10.10.51'     # 放大器 NTP 服务器 IP（适用于 400 系列放大器）
port_ns = 55513            # 默认 ECI 端口

# 初始化 EGI NetStation 客户端
eci_client = NetStation(IP_ns, port_ns)
eci_client.connect(ntp_ip=IP_amp)
eci_client.begin_rec()

# 在 TriggerSender 中包装 NetStation send_event
egi_sender = TriggerSender(
    trigger_func=lambda code: eci_client.send_event(
        event_type=str(code)[:4],  # event_type 最大长度为 4 个字符
        start=0.0,                  # 相对时间戳
        label=str(code)
    ),
    post_delay=0.001
)

# 发送触发码 100
egi_sender.send(100)

# 实验结束时，停止记录并断开连接
eci_client.end_rec()
eci_client.disconnect()
```

#### 示例：通过并行端口的 Neuroscan（尚未测试）

```python
from psychopy import parallel
from psyflow import TriggerSender

# 初始化并行端口（地址可能因系统而异）
port = parallel.ParallelPort(address=0x0378)

# 在 TriggerSender 中包装并行端口 setData
neuroscan_sender = TriggerSender(
    trigger_func=lambda code: [port.setData(code), port.setData(0)],  # 发送后重置为 0
    post_delay=0.001
)

# 向 Neuroscan 系统发送代码 50
neuroscan_sender.send(50)
```

#### 示例：通过 RDA 服务器 (TCP) 的 Brain Products（尚未测试）

```python
import socket
from psyflow import TriggerSender

# 连接到 BrainVision Recorder 的 RDA 接口
HOST, PORT = 'localhost', 51244
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# 在 TriggerSender 中包装套接字发送
gp_sender = TriggerSender(
    trigger_func=lambda code: sock.sendall(f'{code}\n'.encode()),
    post_delay=0.001
)

# 向 Brain Products 发送标记 128
gp_sender.send(128)

# 完成后关闭套接字
sock.close()
```

### 3. 高级：计时和钩子

为了进行更精细的控制，`TriggerSender` 允许您：

- `post_delay`：在每次发送后插入一个暂停（以秒为单位）（默认为 `0.001`）。
- `on_trigger_start`：在发送开始前调用一个函数。
- `on_trigger_end`：在后延迟后调用一个函数。

```python
from psyflow import TriggerSender

def before_hook():
    t0 = core.getTime()
    logging.data(f"触发器开始于 {t0:.4f}s")

def after_hook():
    t1 = core.getTime()
    logging.data(f"触发器结束于 {t1:.4f}s")

trigger_sender = TriggerSender(
    trigger_func=send_code,
    post_delay=0.01,
    on_trigger_start=before_hook,
    on_trigger_end=after_hook
)

trigger_sender.send(42)
```

使用钩子为事件添加时间戳，与其他系统同步，或在每个触发器周围运行自定义诊断。

---

## 5. 与 `StimUnit` 集成

`TriggerSender` 可以传递到 `StimUnit` 中，以最少的代码自动在试验的关键点发送触发器。

1. **初始化和注入**：

   ```python
   from psyflow import TriggerSender, StimUnit

   sender = TriggerSender(trigger_func=your_send_func)
   unit = StimUnit(
       unit_label='trial1',
       win=win,
       kb=kb,
       triggersender=sender
   )
   ```

2. **方法内部的自动调用**：

   - 在 `.show()` 中，`StimUnit` 在第一帧（通过 `win.callOnFlip`）调用 `sender.send(onset_trigger)`，在视觉呈现后调用 `sender.send(offset_trigger)`。
   - 在 `.capture_response()` 中，它会查找按键的代码，并在注册响应时立即调用 `sender.send(code)`。

3. **通过字典配置触发器代码**：

   ```python
   settings.triggers = {
       'onset': 1,
       'offset': 2,
       'response': {'left': 10, 'right': 20}
   }

   unit.show(
       duration=1.0,
       onset_trigger=settings.triggers['onset'],
       offset_trigger=settings.triggers['offset']
   )
   unit.capture_response(
       keys=['left','right'],
       duration=2.0,
       response_trigger=settings.triggers['response']
   )
   ```

如果您省略 `triggersender` 或使用 `mock=True`，`StimUnit` 仍将运行其所有钩子和日志记录，从而允许您在没有硬件的情况下开发和测试行为任务。

4. **示例：MID 任务集成**：

下面是一个来自货币激励延迟 (MID) 任务的真实示例，展示了如何将 `TriggerSender` 和 `StimUnit` 一起使用。`make_unit` 辅助函数简化了将同一个 `trigger_sender` 传递给每个试验阶段的过程。

```python
from psyflow import StimUnit
from functools import partial

def run_trial(win, kb, settings, condition, stim_bank, controller, trigger_sender):
    """
    运行单个 MID 试验序列（注视 → 提示 → 预期 → 目标 → 反馈）。
    """
    trial_data = {"condition": condition}
    make_unit = partial(StimUnit, win=win, kb=kb, triggersender=trigger_sender)

    # --- 提示阶段 ---
    make_unit(unit_label='cue')\
        .add_stim(stim_bank.get(f"{condition}_cue")) \
        .show(
            duration=settings.cue_duration,
            onset_trigger=settings.triggers.get(f"{condition}_cue_onset")
        ) \
        .to_dict(trial_data)

    # --- 预期阶段 ---
    anti = make_unit(unit_label='anticipation')\
        .add_stim(stim_bank.get("fixation"))
    anti.capture_response(
        keys=settings.key_list,
        duration=settings.anticipation_duration,
        onset_trigger=settings.triggers.get(f"{condition}_anti_onset"),
        terminate_on_response=False
    )
    early_resp = anti.get_state("response", default=None)
    anti.set_state(early_response=bool(early_resp)).to_dict(trial_data)

    # --- 目标阶段 ---
    duration = controller.get_duration(condition)
    tgt = make_unit(unit_label='target')\
        .add_stim(stim_bank.get(f"{condition}_target"))
    tgt.capture_response(
        keys=settings.key_list,
        duration=duration,
        onset_trigger=settings.triggers.get(f"{condition}_target_onset"),
        response_trigger=settings.triggers.get(f"{condition}_key_press"),
        timeout_trigger=settings.triggers.get(f"{condition}_no_response")
    )\
        .to_dict(trial_data)

    # --- 反馈阶段 ---
    feedback_code = settings.triggers.get(
        f"{condition}_{'hit' if tgt.get_state('hit', False) else 'miss'}_fb_onset"
    )
    make_unit(unit_label='feedback')\
        .add_stim(stim_bank.get(f"{condition}_{'hit' if tgt.get_state('hit') else 'miss'}_feedback"))\
        .show(
            duration=settings.feedback_duration,
            onset_trigger=feedback_code
        )\
        .set_state(hit=tgt.get_state('hit', False))\
        .to_dict(trial_data)

    return trial_data
```
此示例演示了：

- 创建一个部分构造函数 (`make_unit`)，它会自动将 `trigger_sender` 注入到每个 `StimUnit` 中。
- 以最少的样板代码为每个阶段安排起始和偏移触发器。
- 通过 `settings.triggers` 无缝捕获响应并将其映射到触发器代码。

如果您选择不传递 `triggersender`，完全相同的代码将作为纯行为任务运行，发出日志但没有硬件触发器。

## 后续步骤

现在您知道如何发送触发器，您可以探索 PsyFlow 的其他部分：

- **入门**：如果您是 PsyFlow 的新手，请查看[入门教程](getting_started.md)。
- **构建试验**：在[StimUnit 教程](build_stimunit.md)中了解如何构建复杂的试验。
- **组织模块**：在[BlockUnit 教程](build_blocks.md)中了解如何将试验组织成模块。
