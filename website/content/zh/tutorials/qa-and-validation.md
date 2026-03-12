# QA、Validation 与 Simulation

PsyFlow 现在不再把 “能跑一次” 当成发布标准。当前维护中的流程把 QA、simulation 和 validation 看成三种互补的检查。

- `psyflow-qa`：做一次真实的 smoke run，并生成可审查的产物
- `psyflow-sim`：用 responder 做可重复的行为仿真
- `psyflow-validate`：不启动任务，也能检查任务包结构、合同、配置和说明文件

## QA

先用 QA 跑一遍任务：

```bash
psyflow-qa path/to/task --config config/config_qa.yaml
```

默认会在 `outputs/qa/` 下面留下结构化产物，例如：

- `qa_report.json`
- `static_report.json`
- `contract_report.json`
- `qa_trace.csv`
- `qa_events.jsonl`

这些文件不是临时调试垃圾，而是任务评审和发布前检查的一部分。

## Validation

如果你只想先检查任务包，不想真正启动 PsychoPy，可以直接运行：

```bash
psyflow-validate path/to/task
```

当前 validator 会覆盖：

- 配置文件和 profile 结构
- contract manifest
- reference artifacts
- README 结构
- 面向被试文本的运行时策略

最后这一点很重要。PsyFlow 现在会更主动地阻止把被试可见文本硬编码进运行时代码。

## Simulation

如果你需要无被试的重复性测试，可以用 simulation：

```bash
psyflow-sim path/to/task --config config/config_scripted_sim.yaml
```

如果任务需要自己的 responder：

```bash
psyflow-sim path/to/task --config config/config_sampler_sim.yaml
```

## 推荐顺序

一个准备发布的任务，推荐至少走一遍下面这组命令：

```bash
psyflow-run .
psyflow-qa . --config config/config_qa.yaml
psyflow-sim . --config config/config_scripted_sim.yaml
psyflow-validate .
```

这样你可以分别得到：

- 人工快速检查
- QA 产物
- responder 驱动的覆盖测试
- 静态结构与 contract 检查

## 下一步

- 看 [Trigger 教程](/zh/tutorials/trigger-io/)
- 看 [命令行与运行模式](/zh/tutorials/cli-and-runtime/)
- 回到 [中文教程首页](/zh/tutorials/)
