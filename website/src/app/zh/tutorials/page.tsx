import Link from "next/link";
import { ResourceCard } from "@/components/resource-card";
import { chineseTutorials } from "@/lib/content";

export default function ChineseTutorialsPage() {
  return (
    <div className="space-y-14 pb-8">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
        <div>
          <div className="pf-badge">中文教程</div>
          <h1 className="mt-5 max-w-4xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            保留最常用、最值得维护的中文教程。
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-700">
            这里优先覆盖本地安装、命令行入口、TaskSettings、被试信息、Trigger 和 QA。
            内容已经按当前 PsyFlow 主分支重写，不再沿用旧的 Sphinx 结构。
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-5">
          <div className="space-y-3 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-3 shadow-[0_4px_0_#25314d]">
              先看 <strong>快速开始</strong>，再看 <strong>Trigger</strong> 和 <strong>QA</strong>。
            </div>
            <Link className="pf-focus-ring pf-button-secondary w-full text-sm" href="/tutorials/">
              English tutorials
            </Link>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
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
      </section>
    </div>
  );
}
