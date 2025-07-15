## 概述

`psyflow` 中的 `LLMClient` 类提供了一个轻量级、统一的界面，用于与各种大型语言模型（LLM）后端进行交互，包括 Google Gemini、OpenAI、Deepseek 和 Moonshot。我们没有依赖像 LangChain 这样沉重的框架，而是构建了一个最小化的包装器来保持简单：除了提供商的 SDK 之外，没有额外的依赖项，一个干净的 API（例如 `generate()`、`translate()`、`count_tokens()`），以及快速、低开销的执行。

## 支持的提供商

我们的库支持跨多个提供商的灵活、经济高效的访问：

- **Gemini** (Google GenAI)：免费访问强大的模型——非常适合零成本入门。
- **OpenAI**：官方 OpenAI SDK 支持 GPT 系列模型和微调端点。
- **Deepseek**：对于没有 Gemini 访问权限的用户，这是一个通过 OpenAI 兼容 SDK 实现的经济高效的替代方案。
- **Moonshot**：对于没有 Gemini 访问权限的用户，这是一个通过 OpenAI 兼容 SDK 实现的经济高效的替代方案。

## 主要功能

| 功能 | 描述 |
| --- | --- |
| 多提供商支持 | 开箱即用：Gemini、OpenAI、Deepseek、Moonshot |
| 文本生成 | `generate()` 具有采样和确定性选项 |
| 模型发现 | `list_models()` 列出每个提供商的 ID |
| 任务文档 | `task2doc()` 自动创建一个结构化的 `README.md` |
| 翻译 | `translate()` 用于字符串，`translate_config()` 用于 YAML |
| 知识管理 | `add_knowledge()` 和 `save_knowledge()` 管理少样本示例 |
| 错误处理 | 针对失败、模型缺失或令牌溢出引发 `LLMAPIError` |

## 快速参考

| 目的 | 方法 | 示例 |
| --- | --- | --- |
| 初始化客户端 | `LLMClient(provider, api_key, model)` | `client = LLMClient("openai", os.getenv("OPENAI_KEY"), "gpt-4o-mini")` |
| 生成文本 | `generate(prompt, deterministic=False, **kwargs)` | `resp = client.generate("Hello world", temperature=0.5)` |
| 列出模型 | `list_models()` | `models = client.list_models()` |
| 烟雾测试连接 | `test(ping, max_tokens)` | `client.test("Hi", max_tokens=5)` |
| 自动生成 README | `task2doc(logic_paths, config_paths, output_path)` | `client.task2doc(["src/run_trial.py"], ["config/config.yaml"], "./")` |
| 翻译字符串 | `translate(text, target_language)` | `client.translate("Welcome", "Japanese")` |
| 翻译配置 YAML | `translate_config(target_language, config, output_dir)` | `client.translate_config("Spanish", "./config/config.yaml", "./config")` |

## 详细使用指南

### 1. 验证原生 SDK

#### 1.1 Google-GenAI (Gemini)

```python
from google import genai
# 初始化 Gemini 客户端
genai.configure(api_key="…你的 Gemini API 密钥…")
client = genai.Client()

# 列出可用模型
models = client.models.list()
model_ids = [m.name.split('/')[-1] for m in models]
print("可用模型:", model_ids)

# 快速回声测试
resp = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="你好，你好吗？"
)
print(resp.text)
# -> 我很好... 你今天好吗？
```

#### 1.2 OpenAI / Deepseek

```python
from openai import OpenAI
client = OpenAI(api_key="…你的密钥…", base_url="https://api.deepseek.com")

# 从 Deepseek 列出模型
resp = client.models.list()
ids = [m.id for m in resp.data]
print("可用模型:", ids)

# 快速回声测试
echo = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
    stream=False
)
print(echo.choices[0].message.content)
# -> 你好！我今天能帮你什么吗？
```

### 2. 使用 Psyflow `LLMClient` 包装器

```python
from psyflow import LLMClient
import os

# 为每个提供商实例化包装器
gemini = LLMClient("gemini", os.getenv("GEMINI_KEY"), "gemini-2.0-flash")
deep   = LLMClient("deepseek", os.getenv("DEESEEK_KEY"), "deepseek-chat")

# 通过包装器列出模型
print("Gemini 看到:", gemini.list_models())
print("Deepseek 看到:", deep.list_models())

# 通过包装器进行回声测试
gemini_echo = gemini.test(max_tokens=5)
print("Gemini 回声:", gemini_echo)
deepseal_echo = deep.test(max_tokens=5)
print("Deepseek 回声:", deepseal_echo)
```

### 3. LLM 驱动的任务文档

使用 `task2doc()` 为您的 PsyFlow 任务生成一个完整的 `README.md`：

```python
client = LLMClient("gemini", os.getenv("GEMINI_KEY"), "gemini-2.5-flash")
readme = client.task2doc(
    logic_paths=["main.py", "src/run_trial.py"],
    config_paths=["config/config.yaml"],
    output_path="./"
)
print("生成的 README 内容:")
print(readme)
```

这将读取您的代码和配置，将它们发送到 LLM，并编写一个结构化的 markdown 文档，其中包含：

- **元信息**：版本、作者、要求
- **任务概述**和**流程表**
- **配置摘要**：刺激、计时、触发器
- **方法**部分，可用于手稿

### 4. LLM 驱动的本地化

#### 4.1 内存中翻译

```python
client = LLMClient("deepseek", os.getenv("DEESEEK_KEY"), "deepseek-chat")
translated = client.translate_config(
    target_language="Japanese"
)
print(translated)
```

#### 4.2 翻译并保存

```python
translated = client.translate_config(
    target_language="Spanish",
    config="./config/config.yaml",
    output_dir="./config",
    output_name="config.es.yaml"
)
print("保存到 ./config/config.es.yaml")
```

这将更新您的 YAML 字段（标签、刺激文本）并写入一个 `.translated.yaml` 文件。

## 后续步骤

现在您已经了解了如何在 PsyFlow 中使用 LLM，您可能对以下内容感兴趣：

- **入门**：如果您是 PsyFlow 的新手，请查看[入门教程](getting_started.md)。
- **发送触发器**：在[TriggerSender 教程](send_trigger.md)中了解如何发送硬件触发器。
- **构建试验**：在[StimUnit 教程](build_stimunit.md)中了解如何构建复杂的试验。
