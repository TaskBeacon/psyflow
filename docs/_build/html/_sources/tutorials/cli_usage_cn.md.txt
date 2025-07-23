# psyflow-init: 命令行界面

## 概述

`psyflow-init` 是用于使用内置模板搭建新的 PsychoPy 实验的命令行界面 (CLI) 入口点。它在底层使用 Cookiecutter 生成标准化的项目布局，因此您可以专注于任务逻辑而不是样板文件。

主要优点：

- **标准化**：在所有实验中强制执行一致的文件夹结构
- **快速设置**：用一个命令创建一个完整的项目脚手架
- **灵活的模式**：支持新目录和就地初始化

## 快速参考

| 命令 | 目的 | 示例 |
| --- | --- | --- |
| `psyflow-init <name>` | 创建一个名为 `<name>` 的新文件夹，其中包含项目文件 | `psyflow-init my-new-task` |
| `psyflow-init` (无参数) | 就地初始化当前目录 | `cd existing && psyflow-init` |

## 1. 创建一个新项目

要从头开始，请导航到父目录并运行：

```bash
psyflow-init my-new-task
```

这将创建一个新的 `my-new-task/` 文件夹，其中包含所有必需的文件和子目录：

```
my-new-task/
├── main.py
├── README.md
├── assets/
├── config/
│   └── config.yaml
├── data/
└── src/
    ├── __init__.py
    ├── run_trial.py
    └── utils.py
```

## 2. 就地初始化

如果您已经有（或刚刚创建）一个空目录并希望用 `psyflow` 脚手架填充它，请在不带任何参数的情况下运行该命令：

```bash
mkdir my-existing-project
cd my-existing-project
psyflow-init
```

在复制模板文件之前，CLI 会检查是否存在同名的现有文件或文件夹。如果发现任何冲突，系统将提示您：

```
⚠ 检测到现有文件“main.py”。是否覆盖此文件和所有剩余文件？[y/N]:
```

- 输入 `y` 继续并替换所有现有文件。
- 输入 `n`（或按 Enter）跳过该文件并继续处理其他文件。

这种交互式确认可防止在就地初始化期间意外丢失数据。

## 3. 内部工作原理
1. **定位模板**：使用 `importlib.resources` 查找 `psyflow.templates` 包和 `cookiecutter-psyflow` 文件夹。
2. **Cookiecutter 渲染**：
   - **新目录模式**：直接将 Cookiecutter 运行到 `./<project_name>` 中。
   - **就地模式**：渲染到临时目录，然后将文件复制到当前文件夹中。
3. **清理**：就地模式在完成后会删除临时渲染目录。

## 后续步骤

现在您知道如何初始化项目，您已准备好开始构建您的实验：

- **入门**：按照[入门教程](getting_started_cn.md)从头开始构建一个简单的任务。
- **学习核心概念**：深入了解[StimBank](build_stimulus_cn.md)、[StimUnit](build_stimunit_cn.md)和[BlockUnit](build_blocks_cn.md)教程，以了解 PsyFlow 的关键组件。
