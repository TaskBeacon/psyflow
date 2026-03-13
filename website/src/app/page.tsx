import Link from "next/link";
import Image from "next/image";
import { CommandCard } from "@/components/command-card";
import { ResourceCard } from "@/components/resource-card";
import { changelog, siteData } from "@/lib/generated";
import { withBasePath } from "@/lib/base-path";
import { chineseTutorials, englishTutorials, type TutorialEntry } from "@/lib/content";
import { routes } from "@/lib/routes";

function TapsDiagram() {
  return (
    <div className="pf-frame bg-[#fffdf9] p-4 sm:p-5">
      <div className="grid gap-3">
        <div className="grid gap-3 sm:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[22px] border-2 border-[#25314d] bg-[#eef8ff] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">
              Entry layer
            </div>
            <div className="mt-2 font-heading text-2xl font-bold text-[#25314d]">
              README + taskbeacon.yaml
            </div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              Public description plus machine-readable metadata.
            </div>
          </div>
          <div className="rounded-[22px] border-2 border-[#25314d] bg-[#fff3ed] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">
              Runtime layer
            </div>
            <div className="mt-2 font-heading text-2xl font-bold text-[#25314d]">
              config + src + assets
            </div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              Keep config, task code, and participant-facing assets separate.
            </div>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-[0.92fr_1.08fr]">
          <div className="rounded-[22px] border-2 border-[#25314d] bg-[#efffe9] p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">
              Review layer
            </div>
            <div className="mt-2 font-heading text-2xl font-bold text-[#25314d]">
              references + outputs
            </div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              QA artifacts, references, and logs remain attached to the same package.
            </div>
          </div>
          <div className="rounded-[22px] border-2 border-[#25314d] bg-white p-4 shadow-[0_4px_0_#25314d]">
            <div className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">
              TAPS result
            </div>
            <div className="mt-2 font-heading text-2xl font-bold text-[#25314d]">
              One task package that stays readable across runtime, docs, and QA.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HomePage() {
  const latest = changelog[0] ?? siteData.latest_release;
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

      <section id="taps" className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
        <div>
          <div className="pf-section-chip">TAPS</div>
          <h2 className="mt-5 font-heading text-3xl font-bold text-[#25314d] sm:text-4xl">
            A task package structure, not just another label.
          </h2>
          <p className="mt-4 text-base leading-8 text-slate-700">
            TAPS keeps the local runtime, config, metadata, references, and outputs inside one package
            that stays easier to review across development, QA, and release.
          </p>
          <div className="mt-5 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-3 shadow-[0_4px_0_#25314d]">
              PsyFlow handles the local runtime inside the package.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-3 shadow-[0_4px_0_#25314d]">
              taskbeacon metadata and README describe the task from outside the code.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-3 shadow-[0_4px_0_#25314d]">
              QA outputs and references stay attached to the same source of truth.
            </div>
          </div>
        </div>

        <TapsDiagram />
      </section>

      <section id="framework" className="grid gap-8 lg:grid-cols-[minmax(0,520px)_minmax(0,1fr)] lg:items-center">
        <div className="pf-frame bg-[#fffdf9] p-4">
          <Image
            src={withBasePath("/images/framework/flowchart.png")}
            alt="PsyFlow framework flowchart"
            width={1600}
            height={1200}
            className="w-full rounded-[24px] border-2 border-[#25314d] bg-white shadow-[0_5px_0_#25314d]"
          />
        </div>

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
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 text-sm leading-6 text-slate-700 shadow-[0_4px_0_#25314d]">
              Use config and settings for reusable runtime state.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-4 text-sm leading-6 text-slate-700 shadow-[0_4px_0_#25314d]">
              Keep `main.py` orchestration separate from `run_trial.py`.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#efffe9] px-4 py-4 text-sm leading-6 text-slate-700 shadow-[0_4px_0_#25314d]">
              Let framework helpers absorb generic boilerplate, not paradigm logic.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#f4f0ff] px-4 py-4 text-sm leading-6 text-slate-700 shadow-[0_4px_0_#25314d]">
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
