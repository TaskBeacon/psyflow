export type ResourceLink = {
  eyebrow?: string;
  title: string;
  description: string;
  href: string;
  cta: string;
  external?: boolean;
};

export type CapabilityCard = {
  title: string;
  description: string;
  points: string[];
  tone: "sky" | "peach" | "mint" | "lavender";
};

export const overviewResources: ResourceLink[] = [
  {
    eyebrow: "Framework",
    title: "Inspect the core task primitives",
    description: "See how BlockUnit, StimBank, StimUnit, SubInfo, and TaskSettings fit together.",
    href: "/framework/",
    cta: "Open framework"
  },
  {
    eyebrow: "Utilities",
    title: "Use the helpers that remove boilerplate",
    description: "Config loading, experiment initialization, voice listing, and trial helpers in one place.",
    href: "/utilities/",
    cta: "Open utilities"
  },
  {
    eyebrow: "QA & Sim",
    title: "Validate, smoke-test, and simulate tasks",
    description: "Use strict QA gates, responder plugins, and contract validation before release.",
    href: "/qa-sim/",
    cta: "Open QA & Sim"
  },
  {
    eyebrow: "Tutorials",
    title: "Start with the highest-value walkthroughs",
    description: "Use the refreshed English docs first, then selected Chinese guides for local workflows.",
    href: "/tutorials/",
    cta: "Open tutorials"
  }
];

export const frameworkCards: ResourceLink[] = [
  {
    eyebrow: "BlockUnit",
    title: "Blocks own condition flow and result collation",
    description: "Structure trials into reviewable blocks instead of letting logic sprawl across callbacks.",
    href: "/framework/",
    cta: "Read framework"
  },
  {
    eyebrow: "StimBank + StimUnit",
    title: "Build stimuli from definitions, then run one trial cleanly",
    description: "Keep construction and per-trial execution distinct so tasks stay easier to audit.",
    href: "/framework/",
    cta: "Inspect primitives"
  },
  {
    eyebrow: "SubInfo",
    title: "Collect participant info without custom dialog boilerplate",
    description: "Form-driven subject metadata plugs straight into TaskSettings and output paths.",
    href: "/zh/tutorials/participant-info/",
    cta: "See subject info"
  },
  {
    eyebrow: "TaskSettings",
    title: "Centralize config, seeds, paths, and condition weights",
    description: "Flatten runtime settings and keep reproducibility decisions in one container.",
    href: "/tutorials/task-settings/",
    cta: "See TaskSettings"
  }
];

export const capabilityCards: CapabilityCard[] = [
  {
    title: "Runtime modes",
    description: "One task-local main entry can still serve human, QA, and sim mode cleanly.",
    points: [
      "Use psyflow-run for local human runs",
      "Promote maturity after QA pass",
      "Resolve configs by mode instead of hardcoding paths"
    ],
    tone: "sky"
  },
  {
    title: "Validation and contracts",
    description: "Static checks, contract linting, and content guards are built into the framework now.",
    points: [
      "Run psyflow-validate on canonical task packages",
      "Check config schemas and reference artifacts",
      "Catch hardcoded participant-facing text early"
    ],
    tone: "peach"
  },
  {
    title: "Responder-based simulation",
    description: "Simulation is now a small protocol with session, observation, action, and feedback contracts.",
    points: [
      "Use scripted responders for smoke coverage",
      "Attach task-specific responders when needed",
      "Keep simulation independent from PsychoPy imports"
    ],
    tone: "lavender"
  },
  {
    title: "Trigger I/O",
    description: "Tasks emit semantic trigger events while runtimes and drivers own delivery semantics.",
    points: [
      "Initialize mock, callable, or serial drivers",
      "Schedule trigger emission on flip or now",
      "Log QA artifacts and event traces"
    ],
    tone: "mint"
  }
];

export const utilityHighlights: ResourceLink[] = [
  {
    eyebrow: "Config",
    title: "Load and validate config safely",
    description: "Use load_config() and validate_config() before runtime code starts mutating state.",
    href: "/utilities/",
    cta: "See config helpers"
  },
  {
    eyebrow: "Runtime",
    title: "Initialize experiments and countdowns quickly",
    description: "Use initialize_exp() and count_down() for common PsychoPy startup patterns.",
    href: "/utilities/",
    cta: "See runtime helpers"
  },
  {
    eyebrow: "Trial IDs",
    title: "Track global trial IDs and resolve deadlines",
    description: "Use the built-in trial helpers instead of task-specific controller glue for common cases.",
    href: "/utilities/",
    cta: "See trial helpers"
  },
  {
    eyebrow: "Voices",
    title: "List installed text-to-speech voices",
    description: "Use list_supported_voices() when generating localized instruction audio.",
    href: "/tutorials/utilities/",
    cta: "See voice workflow"
  }
];

export const tutorialSpotlight: ResourceLink[] = [
  {
    eyebrow: "English",
    title: "Get started with the current CLI and runtime split",
    description: "Install PsyFlow, scaffold a task, and use the maintained launcher commands.",
    href: "/tutorials/getting-started/",
    cta: "Read getting started"
  },
  {
    eyebrow: "English",
    title: "Use QA and validation before release",
    description: "Understand psyflow-qa, QA artifacts, contract linting, and strict validation policy.",
    href: "/tutorials/qa-and-validation/",
    cta: "Read QA guide"
  },
  {
    eyebrow: "中文",
    title: "本地化被试信息与任务配置",
    description: "从被试表单到输出路径，梳理最常见的本地开发需求。",
    href: "/zh/tutorials/participant-info/",
    cta: "阅读中文教程"
  },
  {
    eyebrow: "中文",
    title: "触发器与 I/O 运行时",
    description: "理解 TriggerRuntime、驱动器与事件日志的职责边界。",
    href: "/zh/tutorials/trigger-io/",
    cta: "阅读中文教程"
  }
];
