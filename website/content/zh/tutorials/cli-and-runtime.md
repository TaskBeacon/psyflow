# 命令行入口与运行模式

当前 PsyFlow 的 CLI 结构已经和旧文档不一样了。

## 现在维护的入口

| 命令 | 作用 |
| --- | --- |
| `psyflow` | 根命令，主要负责 `init` |
| `psyflow-run` | human 模式运行任务 |
| `psyflow-qa` | QA 模式运行并校验 QA 产物 |
| `psyflow-sim` | simulation 模式运行 |
| `psyflow-validate` | 静态校验任务包、合同、文档与配置 |

不要再按旧教程理解成根命令下的 `psyflow qa` 或 `psyflow sim`。

## 初始化任务

```bash
psyflow init my-new-task
```

或者在当前目录：

```bash
psyflow init
```

## human 模式

```bash
psyflow-run task-path
```

这会自动解析任务目录或 `main.py`，然后用 human 模式调用任务入口。

## QA 模式

```bash
psyflow-qa task-path --config config/config_qa.yaml
```

QA 模式现在不只是“跑一下看看”。

它还会：

- 校验 QA 产物
- 支持更新 `taskbeacon.yaml` 的 maturity
- 支持刷新 README 里的 maturity badge

例如：

```bash
psyflow-qa . --config config/config_qa.yaml --set-maturity smoke_tested
```

## sim 模式

当前推荐的内置 scripted responder 配置是：

```bash
psyflow-sim . --config config/config_scripted_sim.yaml
```

如果是任务自定义 responder，则改用：

```bash
psyflow-sim . --config config/config_sampler_sim.yaml
```

旧教程里提到的 `config/config_sim.yaml` 不再是当前标准。

## validate

```bash
psyflow-validate task-path
```

这个命令现在会检查：

- 任务包结构
- 合同与 config 规则
- README 与 reference artifacts
- runtime 中是否存在不该硬编码的被试可见文本

## 推荐顺序

```bash
psyflow-run .
psyflow-qa . --config config/config_qa.yaml
psyflow-sim . --config config/config_scripted_sim.yaml
psyflow-validate .
```

这四步基本覆盖了本地开发、烟测、仿真与静态校验。
