import Link from "next/link";
import { ResourceCard } from "@/components/resource-card";
import { chineseTutorials } from "@/lib/content";

export default function ChineseTutorialsPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_420px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">中文教程</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            面向本地开发的
            <br />
            <span className="text-[#39d95d]">精选中文指南，</span>
            <br />
            优先覆盖高价值流程。
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            这里保留 v1 需要的中文内容：快速开始、CLI、TaskSettings、被试信息和触发器运行时。
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="space-y-4 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 shadow-[0_4px_0_#25314d]">
              文档内容基于当前主分支，不再沿用旧的 Sphinx 导航结构。
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-4 shadow-[0_4px_0_#25314d]">
              如果你更偏向英文页面，可以回到总教程页查看 English-first 版本。
            </div>
            <Link className="pf-focus-ring pf-button-secondary" href="/tutorials/">
              Back to tutorials
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
