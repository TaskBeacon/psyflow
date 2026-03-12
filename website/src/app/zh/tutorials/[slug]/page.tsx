import Link from "next/link";
import { notFound } from "next/navigation";
import { Markdown } from "@/components/markdown";
import { getTutorial, getTutorials, loadTutorialMarkdown } from "@/lib/content";

export function generateStaticParams() {
  return getTutorials("zh").map((entry) => ({ slug: entry.slug }));
}

export default async function ChineseTutorialDetailPage({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const tutorial = getTutorial("zh", slug);

  if (!tutorial) {
    notFound();
  }

  let markdown = "";
  try {
    markdown = loadTutorialMarkdown("zh", slug);
  } catch {
    notFound();
  }

  const englishPeer = slug === "participant-info" ? null : getTutorial("en", slug);

  return (
    <div className="space-y-10 pb-8">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start">
        <div>
          <div className="pf-badge">{tutorial.eyebrow}</div>
          <h1 className="mt-5 max-w-4xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            {tutorial.title}
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-700">{tutorial.summary}</p>
        </div>

        <aside className="pf-frame bg-[#fffdf9] p-5">
          <div className="space-y-3 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-3 shadow-[0_4px_0_#25314d]">
              参考源：{tutorial.sourceDocs.join(", ")}
            </div>
            <Link className="pf-focus-ring pf-button-secondary w-full text-sm" href="/zh/tutorials/">
              返回中文教程
            </Link>
            {englishPeer ? (
              <Link className="pf-focus-ring pf-button-ghost w-full text-sm" href={englishPeer.href}>
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
