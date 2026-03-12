import Link from "next/link";
import { notFound } from "next/navigation";
import { Markdown } from "@/components/markdown";
import { getTutorial, getTutorials, loadTutorialMarkdown } from "@/lib/content";

export function generateStaticParams() {
  return getTutorials("en").map((entry) => ({ slug: entry.slug }));
}

export default function TutorialDetailPage({ params }: { params: { slug: string } }) {
  const tutorial = getTutorial("en", params.slug);
  if (!tutorial) notFound();

  const markdown = loadTutorialMarkdown("en", params.slug);
  const sibling = getTutorial("zh", params.slug);

  return (
    <div className="space-y-12 pb-8">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-start">
        <div>
          <div className="pf-badge">{tutorial.eyebrow}</div>
          <h1 className="mt-6 max-w-4xl font-heading text-5xl font-bold leading-[0.95] text-[#25314d] sm:text-6xl">
            {tutorial.title}
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">{tutorial.summary}</p>
        </div>

        <aside className="pf-frame-soft bg-[#fffdf9] p-5">
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">On this page</div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Refreshed against the current PsyFlow main branch.
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Source refs: {tutorial.sourceDocs.join(", ")}
            </div>
            {sibling ? (
              <Link className="pf-focus-ring pf-button-secondary w-full" href={sibling.href}>
                打开中文版本
              </Link>
            ) : null}
          </div>
        </aside>
      </section>

      <section className="pf-frame bg-[#fffdf9] p-6 sm:p-8">
        <Markdown markdown={markdown} />
      </section>
    </div>
  );
}
