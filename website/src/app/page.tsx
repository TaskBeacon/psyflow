import Link from "next/link";
import { CommandCard } from "@/components/command-card";
import { ResourceCard } from "@/components/resource-card";
import { changelog, cliCommands, siteData } from "@/lib/generated";
import {
  capabilityCards,
  frameworkCards,
  overviewResources,
  tutorialSpotlight,
  utilityHighlights
} from "@/lib/site-content";

const toneClass = {
  sky: "bg-[#eef8ff]",
  peach: "bg-[#fff3ed]",
  mint: "bg-[#efffe9]",
  lavender: "bg-[#f4f0ff]"
} as const;

function RecentReleaseCard({
  version,
  date,
  summary
}: {
  version: string;
  date: string;
  summary: string[];
}) {
  return (
    <div className="pf-frame-soft h-full bg-[#fffdf9] p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="rounded-full bg-[#d9edf6] px-3 py-1 text-xs font-bold text-[#25314d]">
          v{version}
        </div>
        <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">{date}</div>
      </div>
      <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
        {summary.slice(0, 4).map((item) => (
          <div key={item} className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function HomePage() {
  const latestReleases = changelog.slice(0, 3);
  const latestVersion = siteData.latest_release?.version ?? "main";

  return (
    <div className="space-y-20 pb-8">
      <section className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_560px] lg:items-center xl:gap-16">
        <div>
          <div className="pf-badge mx-auto w-fit">New site: docs now track current main branch behavior</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.92] text-[#25314d] sm:text-6xl">
            Build Auditable
            <br />
            <span className="text-[#39d95d]">PsychoPy Tasks,</span>
            <br />
            Validate Before Release.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-700 sm:text-lg">
            PsyFlow is the canonical local framework for task scaffolding, runtime modes,
            validation, QA artifacts, simulation responders, and hardware-aware trigger I/O.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <Link className="pf-focus-ring pf-button-primary" href="/tutorials/getting-started/">
              Get Started
            </Link>
            <a
              className="pf-focus-ring pf-button-secondary"
              href="https://github.com/TaskBeacon/psyflow"
              target="_blank"
              rel="noreferrer"
            >
              Open GitHub
            </a>
          </div>

          <div className="mt-10 grid max-w-xl grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <div className="font-heading text-4xl font-bold text-[#25314d]">5</div>
              <div className="text-sm text-slate-600">CLI entrypoints</div>
            </div>
            <div>
              <div className="font-heading text-4xl font-bold text-[#25314d]">{siteData.module_count}</div>
              <div className="text-sm text-slate-600">Module groups</div>
            </div>
            <div>
              <div className="font-heading text-4xl font-bold text-[#25314d]">{siteData.release_count}</div>
              <div className="text-sm text-slate-600">Tracked releases</div>
            </div>
            <div>
              <div className="font-heading text-4xl font-bold text-[#25314d]">EN + ZH</div>
              <div className="text-sm text-slate-600">Curated tutorials</div>
            </div>
          </div>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="flex h-full flex-col gap-5">
            <div className="flex items-center justify-between gap-3">
              <div className="rounded-full bg-[#f5c1b5] px-3 py-1 text-xs font-bold text-[#25314d]">
                Quick Start
              </div>
              <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                PsyFlow v{latestVersion}
              </div>
            </div>

            <CommandCard
              title="Install"
              command="pip install psyflow"
              description="Install the framework into a local environment before scaffolding or validating tasks."
              tone="mint"
            />

            <div className="grid gap-4 sm:grid-cols-2">
              <CommandCard
                title="Scaffold"
                command={cliCommands.psyflow ? "psyflow init my-task" : "psyflow init my-task"}
                description="Create a canonical task package from the bundled template."
                tone="sky"
              />
              <CommandCard
                title="Run"
                command={
                  cliCommands["psyflow-run"] ? "psyflow-run path/to/task" : "psyflow-run path/to/task"
                }
                description="Launch the task-local main entry in human mode."
                tone="peach"
              />
              <CommandCard
                title="QA"
                command="psyflow-qa path/to/task"
                description="Run QA mode, validate outputs, and optionally promote maturity."
                tone="lavender"
              />
              <CommandCard
                title="Validate"
                command="psyflow-validate path/to/task"
                description="Lint contracts, configs, docs, and reference artifacts without a full runtime launch."
                tone="sky"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip">Overview</div>
          <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
            Start with the parts of PsyFlow that matter most in practice
          </h2>
          <p className="mt-3 text-base text-slate-600">
            This site is organized around the framework as it behaves now, not around the older
            Sphinx structure.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {overviewResources.map((card) => (
            <ResourceCard key={card.title} {...card} />
          ))}
        </div>
      </section>

      <section className="space-y-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="pf-section-chip bg-[#f5c1b5]">Now in PsyFlow</div>
            <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
              Recent framework changes worth caring about
            </h2>
            <p className="mt-3 max-w-3xl text-base leading-8 text-slate-700">
              The homepage summary is generated from the current changelog so utilities and runtime
              behavior do not silently drift away from the codebase.
            </p>
          </div>

          <Link className="pf-focus-ring pf-button-secondary" href="/changelog/">
            See changelog
          </Link>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          {latestReleases.map((release) => (
            <RecentReleaseCard key={release.version} {...release} />
          ))}
        </div>
      </section>

      <section className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip bg-[#ddd7f4]">Capabilities</div>
          <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
            Core workflows that the current framework supports directly
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {capabilityCards.map((card) => (
            <div key={card.title} className={`pf-frame-soft p-6 ${toneClass[card.tone]}`}>
              <div className="font-heading text-[1.9rem] font-bold leading-tight text-[#25314d]">
                {card.title}
              </div>
              <p className="mt-3 text-sm leading-7 text-slate-700">{card.description}</p>
              <div className="mt-5 space-y-3">
                {card.points.map((point) => (
                  <div
                    key={point}
                    className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-3 text-sm text-slate-700 shadow-[0_4px_0_#25314d]"
                  >
                    {point}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="pf-section-chip">Framework + Utilities</div>
            <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
              Keep task code small by leaning on the framework first
            </h2>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link className="pf-focus-ring pf-button-secondary" href="/framework/">
              Open framework
            </Link>
            <Link className="pf-focus-ring pf-button-secondary" href="/utilities/">
              Open utilities
            </Link>
          </div>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {frameworkCards.map((card) => (
            <ResourceCard key={card.title} {...card} />
          ))}
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {utilityHighlights.map((card) => (
            <ResourceCard key={card.title} {...card} />
          ))}
        </div>
      </section>

      <section className="rounded-[40px] bg-[#efe7de] px-6 py-14 sm:px-8">
        <div className="grid gap-8 lg:grid-cols-[0.86fr_1.14fr] lg:items-start">
          <div>
            <div className="pf-section-chip bg-[#b9dceb]">Tutorials</div>
            <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
              Start with the curated docs, then jump to the generated API inventory
            </h2>
            <p className="mt-4 text-base leading-8 text-slate-700">
              The tutorial layer is intentionally curated. The API page is generated from the code
              so utilities, trigger drivers, and QA/sim exports stay aligned with the repository.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Link className="pf-focus-ring pf-button-primary" href="/tutorials/">
                Open tutorials
              </Link>
              <Link className="pf-focus-ring pf-button-secondary" href="/api/">
                Open API
              </Link>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            {tutorialSpotlight.map((card) => (
              <ResourceCard key={card.title} {...card} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
