# 快速开始：创建本地 PsyFlow 任务

PsyFlow 现在强调的是“本地 canonical task package”。也就是说，框架不只是帮你启动一个 PsychoPy 任务，还希望任务的配置、文档、QA 与仿真入口都保持可审查。

## 安装

建议先创建独立环境，然后安装：

```bash
pip install psyflow
```

如果你需要当前仓库主分支的最新状态：

```bash
pip install https://github.com/TaskBeacon/psyflow.git
```

## 初始化任务

创建一个新任务：

```bash
psyflow init my-task
```

也可以在当前目录就地初始化：

```bash
psyflow init
```

当前模板通常会包含这些关键部分：

```text
my-task/
├─ main.py
├─ README.md
├─ taskbeacon.yaml
├─ assets/
├─ config/
│  ├─ config.yaml
│  ├─ config_qa.yaml
│  ├─ config_scripted_sim.yaml
│  └─ config_sampler_sim.yaml
├─ outputs/
├─ references/
├─ responders/
└─ src/
   └─ run_trial.py
```

这比旧文档里的结构更完整，因为现在 QA、validation、reference artifacts 都已经进入标准流程。

## 当前推荐的配置加载方式

```python
from psyflow import (
    StimBank,
    SubInfo,
    TaskSettings,
    initialize_exp,
    load_config,
)

cfg = load_config("config/config.yaml")

subform = SubInfo(cfg["subform_config"])
subject_data = subform.collect()

settings = TaskSettings.from_dict(cfg["task_config"])
settings.add_subinfo(subject_data)

win, kb = initialize_exp(settings)
stim_bank = StimBank(win, cfg["stim_config"]).preload_all()
```

这里有两个和旧教程不同的点：

- 被试表单使用的是 `subform_config`
- `TaskSettings` 直接吃 `cfg["task_config"]`

## 运行任务

当前推荐优先使用快捷命令：

```bash
psyflow-run .
```

如果你只是临时测试，也可以直接：

```bash
python main.py
```

但在正式工作流里，快捷命令更统一，也更方便切换到 QA 或 sim。

## 输出目录

`TaskSettings` 当前默认把 human 模式输出写到：

```text
./outputs/human
```

不是旧教程中的 `./data`。调用 `settings.add_subinfo(...)` 后会自动生成：

- `log_file`
- `res_file`
- `json_file`

## 下一步

- 看 [命令行入口与运行模式](/zh/tutorials/cli-and-runtime/)
- 看 [TaskSettings、随机种子与条件权重](/zh/tutorials/task-settings/)
- 如果要处理被试表单，看 [采集被试信息并回写输出路径](/zh/tutorials/participant-info/)
