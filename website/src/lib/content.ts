import fs from "node:fs";
import path from "node:path";

export type TutorialEntry = {
  slug: string;
  locale: "en" | "zh";
  title: string;
  summary: string;
  eyebrow: string;
  href: string;
  sourceDocs: string[];
};

export const englishTutorials: TutorialEntry[] = [
  {
    slug: "getting-started",
    locale: "en",
    title: "Getting started with a canonical local task",
    summary: "Install PsyFlow, scaffold a task, and understand the current local runtime layout.",
    eyebrow: "Getting Started",
    href: "/tutorials/getting-started/",
    sourceDocs: ["docs/tutorials/getting_started.md"]
  },
  {
    slug: "cli-and-runtime",
    locale: "en",
    title: "CLI shortcuts and runtime modes",
    summary: "Use the maintained launcher commands instead of the removed root qa and sim subcommands.",
    eyebrow: "CLI",
    href: "/tutorials/cli-and-runtime/",
    sourceDocs: ["docs/tutorials/cli_usage.md", "psyflow/task_launcher.py", "pyproject.toml"]
  },
  {
    slug: "task-settings",
    locale: "en",
    title: "TaskSettings, seeds, and condition weights",
    summary: "Flatten config, attach subject info, and resolve framework-level weights cleanly.",
    eyebrow: "Task Settings",
    href: "/tutorials/task-settings/",
    sourceDocs: ["docs/tutorials/task_settings.md", "psyflow/TaskSettings.py"]
  },
  {
    slug: "utilities",
    locale: "en",
    title: "Utilities for config, runtime, trial IDs, and voices",
    summary: "Surface the helpers that reduce boilerplate in real tasks.",
    eyebrow: "Utilities",
    href: "/tutorials/utilities/",
    sourceDocs: ["docs/tutorials/utilities.md", "psyflow/utils/__init__.py"]
  },
  {
    slug: "trigger-io",
    locale: "en",
    title: "Trigger runtime and hardware I/O",
    summary: "Keep tasks hardware-agnostic while drivers own delivery semantics and audit logging.",
    eyebrow: "Trigger / I/O",
    href: "/tutorials/trigger-io/",
    sourceDocs: ["docs/tutorials/send_trigger.md", "psyflow/io/__init__.py"]
  },
  {
    slug: "qa-and-validation",
    locale: "en",
    title: "QA, validation, and simulation gates",
    summary: "Understand the strict QA gate, contract validation, and responder-based simulation flow.",
    eyebrow: "QA / Validate",
    href: "/tutorials/qa-and-validation/",
    sourceDocs: ["docs/tutorials/qa_runner.md", "psyflow/task_launcher.py", "psyflow/validate.py"]
  }
];

export const chineseTutorials: TutorialEntry[] = [
  {
    slug: "getting-started",
    locale: "zh",
    title: "快速开始：创建本地 PsyFlow 任务",
    summary: "从安装、脚手架到本地运行，建立一套可审查的任务目录。",
    eyebrow: "中文",
    href: "/zh/tutorials/getting-started/",
    sourceDocs: ["docs/tutorials/getting_started_cn.md"]
  },
  {
    slug: "cli-and-runtime",
    locale: "zh",
    title: "命令行入口与运行模式",
    summary: "使用当前的 psyflow-run、psyflow-qa、psyflow-sim、psyflow-validate。",
    eyebrow: "中文",
    href: "/zh/tutorials/cli-and-runtime/",
    sourceDocs: ["docs/tutorials/cli_usage_cn.md", "psyflow/task_launcher.py"]
  },
  {
    slug: "task-settings",
    locale: "zh",
    title: "TaskSettings、随机种子与条件权重",
    summary: "理解配置展平、被试信息注入与 resolve_condition_weights() 的用法。",
    eyebrow: "中文",
    href: "/zh/tutorials/task-settings/",
    sourceDocs: ["docs/tutorials/task_settings_cn.md", "psyflow/TaskSettings.py"]
  },
  {
    slug: "participant-info",
    locale: "zh",
    title: "采集被试信息并回写输出路径",
    summary: "用 SubInfo 与 TaskSettings 串起表单、日志路径与可复现随机种子。",
    eyebrow: "中文",
    href: "/zh/tutorials/participant-info/",
    sourceDocs: ["docs/tutorials/get_subinfo_cn.md"]
  },
  {
    slug: "trigger-io",
    locale: "zh",
    title: "触发器与 I/O 运行时",
    summary: "将语义事件、驱动器与日志拆开，让任务与硬件适配解耦。",
    eyebrow: "中文",
    href: "/zh/tutorials/trigger-io/",
    sourceDocs: ["docs/tutorials/send_trigger_cn.md", "psyflow/io/__init__.py"]
  }
];

const tutorialIndex = new Map<string, TutorialEntry>(
  [...englishTutorials, ...chineseTutorials].map((entry) => [`${entry.locale}:${entry.slug}`, entry])
);

export function getTutorials(locale: "en" | "zh") {
  return locale === "en" ? englishTutorials : chineseTutorials;
}

export function getTutorial(locale: "en" | "zh", slug: string) {
  return tutorialIndex.get(`${locale}:${slug}`) ?? null;
}

export function loadTutorialMarkdown(locale: "en" | "zh", slug: string) {
  const file = path.join(process.cwd(), "content", locale, "tutorials", `${slug}.md`);
  return fs.readFileSync(file, "utf8");
}
