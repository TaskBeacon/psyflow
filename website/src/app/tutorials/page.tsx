import Link from "next/link";
import { ResourceCard } from "@/components/resource-card";
import { chineseTutorials, englishTutorials } from "@/lib/content";

const featuredEnglish = englishTutorials.filter((entry) =>
  ["getting-started", "trigger-io", "qa-and-validation"].includes(entry.slug)
);

export default function TutorialsPage() {
  return (
    <div className="space-y-14 pb-8">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
        <div>
          <div className="pf-badge">Tutorials</div>
          <h1 className="mt-5 max-w-4xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Learn the few PsyFlow workflows that matter most.
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-700">
            Start with local setup, then move straight into Trigger and QA when the task is no longer
            a toy prototype. These pages only describe the maintained runtime on the current main branch.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-5">
          <div className="space-y-3 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-3 shadow-[0_4px_0_#25314d]">
              Start with <strong>Getting started</strong>.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-3 shadow-[0_4px_0_#25314d]">
              Then read <strong>Trigger</strong> and <strong>QA</strong>.
            </div>
            <Link className="pf-focus-ring pf-button-secondary w-full text-sm" href="/zh/tutorials/">
              中文教程
            </Link>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div>
          <div className="pf-section-chip">English</div>
          <h2 className="mt-4 font-heading text-4xl font-bold text-[#25314d]">
            Core tutorials for the maintained runtime
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

      <section className="space-y-6">
        <div>
          <div className="pf-section-chip bg-[#ddd7f4]">Start here</div>
          <h2 className="mt-4 font-heading text-4xl font-bold text-[#25314d]">
            If you only open three pages, open these.
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {featuredEnglish.map((entry) => (
            <ResourceCard
              key={`featured:${entry.slug}`}
              eyebrow={entry.eyebrow}
              title={entry.title}
              description={entry.summary}
              href={entry.href}
              cta="Open tutorial"
            />
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <div>
          <div className="pf-section-chip bg-[#f5c1b5]">Chinese</div>
          <h2 className="mt-4 font-heading text-4xl font-bold text-[#25314d]">
            Selected Chinese guides
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
