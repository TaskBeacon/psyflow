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
    title: "Getting started",
    summary: "Install PsyFlow, scaffold a task, and run the first canonical local task cleanly.",
    eyebrow: "Start",
    href: "/tutorials/getting-started/",
    sourceDocs: ["docs/tutorials/getting_started.md"]
  },
  {
    slug: "cli-and-runtime",
    locale: "en",
    title: "CLI and runtime modes",
    summary: "Use the maintained launcher commands instead of the removed root qa and sim subcommands.",
    eyebrow: "CLI",
    href: "/tutorials/cli-and-runtime/",
    sourceDocs: ["docs/tutorials/cli_usage.md", "psyflow/task_launcher.py", "pyproject.toml"]
  },
  {
    slug: "task-settings",
    locale: "en",
    title: "TaskSettings and condition weights",
    summary: "Flatten config, attach subject info, and resolve framework-level weights in one place.",
    eyebrow: "Settings",
    href: "/tutorials/task-settings/",
    sourceDocs: ["docs/tutorials/task_settings.md", "psyflow/TaskSettings.py"]
  },
  {
    slug: "trigger-io",
    locale: "en",
    title: "Trigger tutorial",
    summary: "Keep tasks hardware-agnostic while runtimes and drivers own delivery semantics.",
    eyebrow: "Trigger",
    href: "/tutorials/trigger-io/",
    sourceDocs: ["docs/tutorials/send_trigger.md", "psyflow/io/__init__.py"]
  },
  {
    slug: "qa-and-validation",
    locale: "en",
    title: "QA tutorial",
    summary: "Run QA, simulation, and validation as a release gate rather than an afterthought.",
    eyebrow: "QA",
    href: "/tutorials/qa-and-validation/",
    sourceDocs: ["docs/tutorials/qa_runner.md", "psyflow/task_launcher.py", "psyflow/validate.py"]
  }
];

export const chineseTutorials: TutorialEntry[] = [
  {
    slug: "getting-started",
    locale: "zh",
    title: "快速开始",
    summary: "从安装、脚手架到本地运行，先把一套可审查的任务包搭起来。",
    eyebrow: "中文",
    href: "/zh/tutorials/getting-started/",
    sourceDocs: ["docs/tutorials/getting_started_cn.md"]
  },
  {
    slug: "cli-and-runtime",
    locale: "zh",
    title: "命令行与运行模式",
    summary: "用当前维护中的 psyflow-run、psyflow-qa、psyflow-sim、psyflow-validate。",
    eyebrow: "中文",
    href: "/zh/tutorials/cli-and-runtime/",
    sourceDocs: ["docs/tutorials/cli_usage_cn.md", "psyflow/task_launcher.py"]
  },
  {
    slug: "task-settings",
    locale: "zh",
    title: "TaskSettings 与条件权重",
    summary: "理解配置展平、被试信息注入，以及 resolve_condition_weights() 的当前用法。",
    eyebrow: "中文",
    href: "/zh/tutorials/task-settings/",
    sourceDocs: ["docs/tutorials/task_settings_cn.md", "psyflow/TaskSettings.py"]
  },
  {
    slug: "participant-info",
    locale: "zh",
    title: "被试信息与输出路径",
    summary: "把 SubInfo、TaskSettings、输出目录和随机种子串成一条更稳定的本地流程。",
    eyebrow: "中文",
    href: "/zh/tutorials/participant-info/",
    sourceDocs: ["docs/tutorials/get_subinfo_cn.md"]
  },
  {
    slug: "trigger-io",
    locale: "zh",
    title: "Trigger 教程",
    summary: "把语义事件、运行时和硬件驱动拆开，让任务逻辑保持硬件无关。",
    eyebrow: "中文",
    href: "/zh/tutorials/trigger-io/",
    sourceDocs: ["docs/tutorials/send_trigger_cn.md", "psyflow/io/__init__.py"]
  },
  {
    slug: "qa-and-validation",
    locale: "zh",
    title: "QA 教程",
    summary: "梳理 QA、simulation 和 validation 在当前主分支中的职责边界。",
    eyebrow: "中文",
    href: "/zh/tutorials/qa-and-validation/",
    sourceDocs: ["docs/tutorials/qa_runner.md", "psyflow/validate.py"]
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
