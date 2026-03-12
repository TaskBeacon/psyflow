import { ResourceCard } from "@/components/resource-card";
import { englishTutorials, chineseTutorials } from "@/lib/content";

export default function TutorialsPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_420px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">Tutorials</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Learn the
            <br />
            <span className="text-[#39d95d]">Current Workflow,</span>
            <br />
            Skip the Stale Docs.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            These pages are the curated learning layer for PsyFlow. They focus on the commands and
            runtime patterns that still exist on main, not the removed Sphinx-era entrypoints.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="space-y-4">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 shadow-[0_4px_0_#25314d]">
              English-first pages for framework usage, runtime modes, utilities, triggers, and QA.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-4 shadow-[0_4px_0_#25314d]">
              Selected Chinese guides for local setup, CLI, participant info, and trigger runtime.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#efffe9] px-4 py-4 shadow-[0_4px_0_#25314d]">
              Markdown content is site-owned now, so updates no longer depend on Sphinx build flow.
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip">English</div>
          <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
            Start here if you are learning the maintained runtime
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {englishTutorials.map((entry) => (
            <ResourceCard
              key={entry.slug}
              eyebrow={entry.eyebrow}
              title={entry.title}
              description={entry.summary}
              href={entry.href}
              cta="Open tutorial"
            />
          ))}
        </div>
      </section>

      <section className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip bg-[#ddd7f4]">中文</div>
          <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
            Selected Chinese guides for local workflows
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {chineseTutorials.map((entry) => (
            <ResourceCard
              key={entry.slug}
              eyebrow={entry.eyebrow}
              title={entry.title}
              description={entry.summary}
              href={entry.href}
              cta="阅读教程"
            />
          ))}
        </div>
      </section>
    </div>
  );
}
