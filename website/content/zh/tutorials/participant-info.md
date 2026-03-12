# 采集被试信息并回写输出路径

`SubInfo` 和 `TaskSettings` 的组合，是 PsyFlow 里处理被试信息最稳定的方式。

标准流程通常是：

1. 用 `SubInfo` 从配置生成表单
2. 收集被试信息
3. 把结果注入 `TaskSettings`
4. 让输出路径、文件名和随机种子自动联动

## 用配置定义表单

被试表单应该来自配置，而不是直接在 Python 里硬编码。

例如：

```yaml
subform:
  title: Participant Info
  fields:
    - name: subject_id
      type: text
      required: true
    - name: session_id
      type: text
      required: true
    - name: language
      type: choice
      choices: [en, zh]
```

然后通过 `load_config()` 获取 `subform_config`。

## 基本用法

```python
from psyflow import SubInfo, TaskSettings, load_config

cfg = load_config("config/config.yaml")

subform = SubInfo(cfg["subform_config"])
subject_data = subform.collect()

settings = TaskSettings.from_dict(cfg["task_config"])
settings.add_subinfo(subject_data)
```

## 图示

![SubInfo YAML](/images/tutorials/subinfo_yaml_cn.png)

## `add_subinfo()` 会做什么

调用 `settings.add_subinfo(subject_data)` 之后，框架会：

- 把 `subject_id` 等字段挂到 `settings`
- 在 `same_within_sub` 模式下按被试生成稳定 seed
- 创建输出目录
- 推导：
  - `log_file`
  - `res_file`
  - `json_file`

## 输出路径

当前默认 human 输出目录是：

```text
./outputs/human
```

文件名会结合：

- `subject_id`
- `task_name`
- 当前时间戳

这样后续 QA 或人工核查时，能直接定位对应被试与任务版本。

## 为什么推荐这样做

这套路径有几个优点：

- 表单结构来自配置，更易本地化
- 输出文件命名统一
- seed 与被试信息联动，更利于复现
- 不需要在每个任务里重复写一套 GUI + 文件命名逻辑

## 建议

被试字段定义、标签文案和约束规则都尽量放进配置里。不要在 runtime 代码里硬编码 participant-facing text，这也是当前 validation 更强调的一部分。
