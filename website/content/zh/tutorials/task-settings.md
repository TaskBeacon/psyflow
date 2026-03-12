# TaskSettings、随机种子与条件权重

`TaskSettings` 是 PsyFlow 当前最核心的配置容器之一。它负责集中保存：

- 窗口设置
- 任务结构
- 按键列表
- 随机种子
- 输出路径
- 条件与条件权重
- 被试相关信息

## 基本初始化方式

```python
from psyflow import TaskSettings, load_config

cfg = load_config("config/config.yaml")
settings = TaskSettings.from_dict(cfg["task_config"])
```

推荐直接从 `load_config()` 产出的 `task_config` 初始化，而不是自己手工重复拼装旧教程里的字段。

## 注入被试信息

```python
settings.add_subinfo({"subject_id": "S01", "session_id": "01"})
```

调用后会：

- 把字段挂到 `settings` 上
- 在需要时按 `subject_id` 推导随机种子
- 创建输出目录
- 生成 `log_file`、`res_file`、`json_file`

当前默认输出根目录是：

```text
./outputs/human
```

## 种子策略

相关字段主要有：

- `overall_seed`
- `block_seed`
- `seed_mode`

两种主要模式：

- `same_across_sub`：所有被试共享同一套 block seed
- `same_within_sub`：按 `subject_id` 生成稳定但个体化的 seed

如果没有显式提供 `block_seed`，框架会自动生成。

## 条件权重现在属于 TaskSettings

这是当前版本和旧文档最重要的差异之一。

现在应使用：

```python
weights = settings.resolve_condition_weights()
```

而不是依赖旧的 utility 层函数。

`condition_weights` 可以是：

- `None`
- 与 `conditions` 对齐的列表或元组
- 以条件标签为 key 的字典

框架会检查：

- 长度是否一致
- key 是否完整
- 是否能转换为数字
- 是否为有限值
- 是否都大于 0

## 适合放进 TaskSettings 的内容

- block / trial 数量
- response keys
- 通用 timing 参数
- seed 与 output path
- 条件列表和条件权重

## 不适合放进 TaskSettings 的内容

- 大量 stimulus 定义
- 被试可见文本原文
- 只在某个任务私有模块里才有意义的临时控制状态

## 建议

把 `TaskSettings` 当作“任务级运行配置容器”，而不是“任何东西都往里塞”的万能对象。这样 QA、validation 和后续调试都会更清楚。
