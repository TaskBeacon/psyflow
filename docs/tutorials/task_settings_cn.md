# TaskSettings: 管理实验配置

## 概述

`TaskSettings` 是 `psyflow` 中的一个实用类，旨在简化对实验设置的管理。它将一个字典（通常是从 `config.yaml` 加载的）转换为一个 Python 对象，其属性可以通过点符号（.）轻松访问，从而使您的代码更具可读性和更不易出错。

使用 `TaskSettings`，您可以：

-   将嵌套的配置字典转换为易于使用的对象。
-   使用点符号（例如 `settings.screen_width`）而不是字典语法（`settings['screen_width']`）来访问设置。
-   为不存在的设置提供默认值，以避免 `KeyError`。
-   在运行时动态更新或添加新设置。

## 核心概念

`TaskSettings` 的主要思想是将字典键转换为对象属性。

您给它一个字典：
```python
config_dict = {
    'window': {
        'size': [1920, 1080],
        'fullscreen': True
    },
    'timing': {
        'fixation_duration': 0.5
    }
}
```

它会给您一个可以这样使用的对象：
```python
settings = TaskSettings(config_dict)

# 使用点符号访问设置
win_size = settings.size  # -> [1920, 1080]
is_fullscreen = settings.fullscreen  # -> True
fix_time = settings.fixation_duration  # -> 0.5
```

注意 `TaskSettings` 如何自动“扁平化”嵌套的字典（`window` 和 `timing`），使得所有设置都可以直接在顶层访问。

## 详细使用指南

### 1. 初始化 `TaskSettings`

`TaskSettings` 通常在您的主实验脚本的开头，在您加载了您的 `config.yaml` 文件之后被初始化。`psyflow` 的 `load_config` 函数与 `TaskSettings` 配合得很好。

```python
from psyflow.utils import load_config
from psyflow.task_settings import TaskSettings

# 1. 使用 psyflow 的辅助函数加载您的 YAML 配置
config = load_config('config/config.yaml')

# config['task_config'] 包含所有与任务相关的设置
# (例如，来自 'window' 和 'timing' 部分)
# {'size': [800, 600], 'fullscreen': False, 'fixation_duration': 0.5, ...}

# 2. 从任务配置字典创建 TaskSettings 对象
settings = TaskSettings(config['task_config'])

# 现在您可以使用点符号访问了
print(f"窗口大小: {settings.size}")
print(f"全屏模式: {settings.fullscreen}")
```

### 2. 访问设置

您可以使用标准的 Python 点符号来访问任何设置。

```python
# 获取背景颜色
bg_color = settings.bg_color

# 在创建 PsychoPy 窗口时使用它
win = visual.Window(
    size=settings.size,
    fullscr=settings.fullscreen,
    color=settings.bg_color
)
```

### 3. 提供默认值

如果您尝试访问一个不存在的属性，`TaskSettings` 将返回 `None` 而不是引发 `AttributeError` 或 `KeyError`。这使得处理可选设置更加安全。

```python
# 假设 'response_keys' 没有在您的 config.yaml 中定义
keys = settings.response_keys

print(keys)  # -> None
```

您可以使用标准的 Python 技术来提供您自己的默认值：

```python
# 如果 settings.response_keys 是 None，则使用 ['f', 'j']
valid_keys = settings.response_keys or ['f', 'j']
```

### 4. 更新和添加设置

您可以在运行时像对待任何常规 Python 对象一样更新现有设置或添加新设置。

```python
# 更新一个现有的设置
settings.fullscreen = False

# 添加一个在实验期间计算出的新设置
# (例如，基于显示器规格的每帧时间)
settings.frame_duration_ms = win.getMsPerFrame()[0]
```

这对于存储在实验过程中确定或计算的值非常有用。

### 5. 转换为字典

如果您需要将设置转换回字典（例如，用于保存或记录），您可以使用 `to_dict()` 方法。

```python
# 获取包含所有当前设置的字典
settings_dict = settings.to_dict()

# 保存到 JSON 文件
import json
with open('used_settings.json', 'w') as f:
    json.dump(settings_dict, f, indent=2)
```

## 推荐的工作流程

在 `psyflow` 项目中，推荐的工作流程如下：

1.  在您的 `config/config.yaml` 文件中定义所有静态实验参数。
2.  在您的 `main.py` 脚本的开头，使用 `load_config()` 来加载这个文件。
3.  立即从加载的配置中创建一个 `TaskSettings` 实例。
4.  将这个 `settings` 对象传递给需要访问配置参数的任何函数（例如 `run_trial`）和 `BlockUnit`。

**`main.py` 示例:**
```python
from psyflow.utils import load_config, initialize_exp
from psyflow.task_settings import TaskSettings
from psyflow.block_unit import BlockUnit
from src.run_trial import run_trial
import pandas as pd

def main():
    # 1. 加载配置
    config = load_config('config/config.yaml')
    
    # 2. 创建 TaskSettings
    settings = TaskSettings(config['task_config'])

    # 3. 初始化 PsychoPy
    win, kb = initialize_exp(settings)

    # 4. 加载试验
    trial_list = pd.read_csv('trials.csv').to_dict('records')

    # 5. 将 settings 对象传递给 BlockUnit
    block = BlockUnit(
        trial_list=trial_list,
        run_func=run_trial,
        fixed_params={
            'win': win,
            'kb': kb,
            'settings': settings # 在这里传递
        }
    )

    # 6. 运行实验
    block.run()

if __name__ == '__main__':
    main()
```

通过遵循这种模式，您可以确保在整个项目中对设置进行一致、可读和健壮的管理。
