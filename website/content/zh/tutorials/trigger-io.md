# 触发器与 I/O 运行时

当前 PsyFlow 的 trigger 设计已经不是旧教程里那种单一 `TriggerSender` 思路了。

现在的职责拆分更清晰：

- 任务代码负责语义事件
- `TriggerRuntime` 负责时序与日志
- driver 负责具体硬件协议

这样做的好处是，任务逻辑可以保持 hardware-agnostic。

## 初始化入口

```python
from psyflow import initialize_triggers

runtime = initialize_triggers(cfg)
```

它会读取当前配置中的：

- `trigger_driver_config`
- `trigger_policy_config`
- `trigger_timing_config`

## 当前支持的 driver 类型

- `mock`
- `callable`
- `serial_port`
- `serial_url`

另外还有公开导出的 `FanoutDriver`，适合需要把一个事件发往多个下游的场景。

本地开发或 QA 时，优先使用 `mock`。

## TriggerRuntime 的职责

`TriggerRuntime` 现在主要负责：

- `when="now"` 或 `when="flip"` 的时序语义
- planned / executed 日志
- driver capability 检查
- strict 模式下的失败策略

例如：

```python
from psyflow import TriggerEvent

runtime.emit(
    TriggerEvent(code=11, name="cue_onset"),
    when="flip",
    win=win,
)
```

## 为什么比旧模式更好

旧模式常见的问题是把这些东西混在一起：

- 任务阶段语义
- serial 编码
- pulse/reset 规则
- 硬件适配细节

现在把它们拆开后，任务代码更容易读，也更容易迁移到不同实验室硬件。

## strict 模式

如果事件要求的能力当前 driver 不支持，比如：

- `pulse_width_ms`
- `reset_code`

那么：

- strict 模式会直接报错
- 非 strict 模式会记录 capability-missing 日志

这对 QA 非常重要，因为它能更早暴露“任务假设了某种硬件能力”的问题。

## 推荐写法

在任务里尽量写成语义化事件：

```python
from psyflow import TriggerEvent

runtime.emit(TriggerEvent(code=21, name="target_onset"), when="flip", win=win)
```

不要把 serial bytes、端口协议或 reset 逻辑直接塞进 `run_trial.py`。这些都应该留给 runtime 和 driver 层。
