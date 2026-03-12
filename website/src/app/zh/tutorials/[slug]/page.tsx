import Link from "next/link";
import { notFound } from "next/navigation";
import { Markdown } from "@/components/markdown";
import { getTutorial, getTutorials, loadTutorialMarkdown } from "@/lib/content";

export function generateStaticParams() {
  return getTutorials("zh").map((entry) => ({ slug: entry.slug }));
}

export default function ChineseTutorialDetailPage({ params }: { params: { slug: string } }) {
  const tutorial = getTutorial("zh", params.slug);
  if (!tutorial) notFound();

  const markdown = loadTutorialMarkdown("zh", params.slug);
  const englishPeer =
    params.slug === "participant-info" ? null : getTutorial("en", params.slug === "trigger-io" ? "trigger-io" : params.slug);

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
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">说明</div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              内容已经按当前 PsyFlow 主分支刷新。
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              参考源：{tutorial.sourceDocs.join(", ")}
            </div>
            {englishPeer ? (
              <Link className="pf-focus-ring pf-button-secondary w-full" href={englishPeer.href}>
                Open English version
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
