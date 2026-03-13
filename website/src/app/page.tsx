import Link from "next/link";
import Image from "next/image";
import { CommandCard } from "@/components/command-card";
import { ResourceCard } from "@/components/resource-card";
import { changelog } from "@/lib/generated";
import { withBasePath } from "@/lib/base-path";
import { chineseTutorials, englishTutorials, type TutorialEntry } from "@/lib/content";
import { routes } from "@/lib/routes";

function TapsDiagram() {
  return (
    <div className="pf-frame bg-[#fffdf9] p-4 sm:p-5">
      <div className="rounded-[26px] border-2 border-dashed border-[#5cabc0] bg-[#f8fcfe] p-4 sm:p-6">
        <div className="grid gap-3 lg:grid-cols-4">
          <div className="rounded-[20px] border-2 border-[#25314d] bg-[#eef8ff] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">Docs</div>
            <div className="mt-2 font-heading text-xl font-bold text-[#25314d]">README</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              Human-readable task purpose, setup, and review context.
            </div>
          </div>
          <div className="rounded-[20px] border-2 border-[#25314d] bg-[#fff3ed] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">Metadata</div>
            <div className="mt-2 font-heading text-xl font-bold text-[#25314d]">taskbeacon.yaml</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              Machine-readable IDs, maturity, preview links, and release state.
            </div>
          </div>
          <div className="rounded-[20px] border-2 border-[#25314d] bg-[#efffe9] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">Runtime</div>
            <div className="mt-2 font-heading text-xl font-bold text-[#25314d]">config + src + assets</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              Separate task code, participant-facing assets, and local runtime settings.
            </div>
          </div>
          <div className="rounded-[20px] border-2 border-[#25314d] bg-[#f4f0ff] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">Review</div>
            <div className="mt-2 font-heading text-xl font-bold text-[#25314d]">references + outputs</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              Keep QA artifacts, reference files, and release evidence attached to the task.
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-center">
          <div className="h-0.5 w-full max-w-[110px] bg-[#5cabc0]" />
          <div className="mx-3 rounded-full border-2 border-[#25314d] bg-white px-4 py-2 text-xs font-bold uppercase tracking-[0.16em] text-[#25314d] shadow-[0_4px_0_#25314d]">
            One Auditable Task Package
          </div>
          <div className="h-0.5 w-full max-w-[110px] bg-[#5cabc0]" />
        </div>
      </div>
    </div>
  );
}

export default function HomePage() {
  const latest = changelog[0] ?? null;
  const tutorialCards = [
    englishTutorials.find((entry) => entry.slug === "getting-started"),
    englishTutorials.find((entry) => entry.slug === "trigger-io"),
    englishTutorials.find((entry) => entry.slug === "qa-and-validation"),
    chineseTutorials.find((entry) => entry.slug === "getting-started"),
    chineseTutorials.find((entry) => entry.slug === "trigger-io"),
    chineseTutorials.find((entry) => entry.slug === "qa-and-validation")
  ].filter((entry): entry is TutorialEntry => Boolean(entry));

  return (
    <div className="space-y-16 pb-8 sm:space-y-20">
      <section className="space-y-6">
        <div className="mx-auto max-w-3xl text-center">
          <div className="pf-badge mx-auto">Quick Start</div>
          <h1 className="mt-5 font-heading text-4xl font-bold leading-[0.95] text-[#25314d] sm:text-5xl lg:text-6xl">
            Start with the maintained PsyFlow workflow.
          </h1>
          <p className="mt-4 text-base leading-8 text-slate-700 sm:text-lg">
            Install the framework, scaffold a local task package, then run QA and validation before
            release.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-5 sm:p-6">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <p className="max-w-3xl text-sm leading-7 text-slate-700">
                These are the commands that matter most on the current main branch. The site now stays
                aligned with the maintained local runtime instead of the older Sphinx-era flow.
              </p>
              {latest ? (
                <div className="pf-section-chip self-start bg-[#f5c1b5] md:self-auto">
                  Latest {latest.version}
                </div>
              ) : null}
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <CommandCard
                title="Install"
                command="pip install psyflow"
                description="Install the framework first."
                tone="mint"
              />
              <CommandCard
                title="Scaffold"
                command="psyflow init my-task"
                description="Create a canonical task package."
                tone="sky"
              />
              <CommandCard
                title="Run"
                command="psyflow-run task-path"
                description="Launch the task in human mode."
                tone="peach"
              />
              <CommandCard
                title="Validate"
                command="psyflow-validate task-path"
                description="Lint contracts, configs, and references."
                tone="lavender"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <CommandCard
                title="QA"
                command="psyflow-qa task-path --config config/config_qa.yaml"
                description="Smoke-test and validate QA outputs."
                tone="mint"
              />
              <CommandCard
                title="Sim"
                command="psyflow-sim task-path --config config/config_scripted_sim.yaml"
                description="Run a scripted or task-specific simulation profile."
                tone="sky"
              />
            </div>
          </div>
        </div>
      </section>

      <section id="taps" className="space-y-8">
        <div className="mx-auto max-w-4xl text-center">
          <div className="pf-section-chip">TAPS</div>
          <h2 className="mt-5 font-heading text-3xl font-bold text-[#25314d] sm:text-4xl">
            TAPS keeps the full task structure readable.
          </h2>
          <p className="mt-4 text-base leading-8 text-slate-700">
            Instead of scattering docs, config, runtime code, and QA artifacts across unrelated places,
            TAPS keeps them attached to the same task package.
          </p>
        </div>

        <TapsDiagram />

        <div className="grid gap-4 md:grid-cols-3">
          <div className="pf-frame-soft bg-white p-5">
            <div className="font-heading text-[1.5rem] font-bold text-[#25314d]">Readable by humans</div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              README carries the task story, setup notes, and review context without forcing readers into the code.
            </p>
          </div>
          <div className="pf-frame-soft bg-white p-5">
            <div className="font-heading text-[1.5rem] font-bold text-[#25314d]">Readable by tooling</div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              Metadata and config stay structured, so QA, previews, and downstream tooling can reason over the task.
            </p>
          </div>
          <div className="pf-frame-soft bg-white p-5">
            <div className="font-heading text-[1.5rem] font-bold text-[#25314d]">Readable over time</div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              Outputs, references, and release evidence remain beside the source package instead of drifting away.
            </p>
          </div>
        </div>
      </section>

      <section id="framework" className="space-y-8">
        <div className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] xl:items-end">
          <div>
            <div className="pf-section-chip bg-[#f5c1b5]">Framework</div>
            <h2 className="mt-5 font-heading text-3xl font-bold text-[#25314d] sm:text-4xl">
              Keep the framework opinionated where reviewability matters.
            </h2>
            <p className="mt-4 text-base leading-8 text-slate-700">
              PsyFlow is designed around a few stable primitives: `BlockUnit`, `StimBank`, `StimUnit`,
              `SubInfo`, and `TaskSettings`. The goal is not abstraction for its own sake, but a task
              runtime that stays readable when the paradigm grows.
            </p>
          </div>

          <div className="pf-frame-soft bg-[#eef8ff] p-5">
            <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">
              Framework idea
            </div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              Keep generic runtime work inside the framework, but keep paradigm logic close to the task.
              That split is what makes larger tasks easier to test, localize, and review.
            </p>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] xl:items-stretch">
          <div className="pf-frame bg-[#fffdf9] p-4">
            <Image
              src={withBasePath("/images/framework/flowchart.png")}
              alt="PsyFlow framework flowchart"
              width={1600}
              height={1200}
              className="w-full rounded-[24px] border-2 border-[#25314d] bg-white shadow-[0_5px_0_#25314d]"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-2">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 text-sm leading-7 text-slate-700 shadow-[0_4px_0_#25314d]">
              Use config and settings for reusable runtime state.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-4 text-sm leading-7 text-slate-700 shadow-[0_4px_0_#25314d]">
              Keep `main.py` orchestration separate from `run_trial.py`.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#efffe9] px-4 py-4 text-sm leading-7 text-slate-700 shadow-[0_4px_0_#25314d]">
              Let framework helpers absorb generic boilerplate, not paradigm logic.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#f4f0ff] px-4 py-4 text-sm leading-7 text-slate-700 shadow-[0_4px_0_#25314d]">
              Keep outputs and validation artifacts tied to the same local package.
            </div>
          </div>
        </div>
      </section>

      <section id="triggers" className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip bg-[#ddd7f4]">Trigger</div>
          <h2 className="mt-5 font-heading text-3xl font-bold text-[#25314d] sm:text-4xl">
            The task emits semantic events. The runtime and drivers own delivery.
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          <div className="pf-frame-soft bg-[#fffdf9] p-5">
            <div className="font-heading text-[1.6rem] font-bold text-[#25314d] sm:text-[1.8rem]">
              Semantic events
            </div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              Trial code should name cue, target, feedback, or custom events instead of embedding serial logic.
            </p>
          </div>
          <div className="pf-frame-soft bg-[#fffdf9] p-5">
            <div className="font-heading text-[1.6rem] font-bold text-[#25314d] sm:text-[1.8rem]">
              TriggerRuntime
            </div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              The runtime decides `now` versus `flip`, capability checks, and planned or executed logging.
            </p>
          </div>
          <div className="pf-frame-soft bg-[#fffdf9] p-5">
            <div className="font-heading text-[1.6rem] font-bold text-[#25314d] sm:text-[1.8rem]">
              Drivers
            </div>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              Mock, callable, serial, and fanout drivers stay outside task logic so hardware can change cleanly.
            </p>
          </div>
        </div>
      </section>

      <section id="qa-sim" className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip bg-[#b9dceb]">QA &amp; Sim</div>
          <h2 className="mt-5 font-heading text-3xl font-bold text-[#25314d] sm:text-4xl">
            Keep QA simple: run, inspect artifacts, validate, then release.
          </h2>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <CommandCard
            title="QA"
            command="psyflow-qa task-path --config config/config_qa.yaml"
            description="Run smoke QA and inspect qa_report.json, trace, and events."
            tone="mint"
          />
          <CommandCard
            title="Sim"
            command="psyflow-sim task-path --config config/config_scripted_sim.yaml"
            description="Use scripted or task-specific responders without coupling simulation to PsychoPy."
            tone="lavender"
          />
          <CommandCard
            title="Validate"
            command="psyflow-validate task-path"
            description="Check contracts, configs, reference artifacts, and runtime text policy."
            tone="sky"
          />
        </div>
      </section>

      <section className="space-y-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="pf-section-chip">Tutorials</div>
            <h2 className="mt-5 font-heading text-3xl font-bold text-[#25314d] sm:text-4xl">
              Start with the few tutorials that matter most.
            </h2>
            <p className="mt-3 max-w-3xl text-base leading-8 text-slate-700">
              Get started first, then go straight to Trigger and QA if you are building or reviewing a real task.
            </p>
          </div>
          <Link className="pf-focus-ring pf-button-secondary sm:w-auto" href={routes.tutorials}>
            Open tutorials
          </Link>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {tutorialCards.map((entry) => (
            <ResourceCard
              key={`${entry.locale}:${entry.slug}`}
              eyebrow={entry.eyebrow}
              title={entry.title}
              description={entry.summary}
              href={entry.href}
              cta={entry.locale === "zh" ? "阅读教程" : "Open tutorial"}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
