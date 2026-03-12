import { changelog, siteData } from "@/lib/generated";

export default function ChangelogPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_420px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">Changelog</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Read the
            <br />
            <span className="text-[#39d95d]">Meaningful Changes,</span>
            <br />
            Not Just a Version Number.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            The published package version in pyproject is behind the current repository history. This
            site follows the changelog and current main branch behavior instead of treating one stale
            package number as the whole story.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="space-y-4 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 shadow-[0_4px_0_#25314d]">
              pyproject version: {siteData.project.version ?? "unknown"}
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-4 shadow-[0_4px_0_#25314d]">
              latest changelog version: {siteData.latest_release?.version ?? "unknown"}
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        {changelog.map((release) => (
          <div key={release.version} className="pf-frame bg-[#fffdf9] p-6">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="rounded-full bg-[#d9edf6] px-3 py-1 text-xs font-bold text-[#25314d]">
                  Version {release.version}
                </div>
                <h2 className="mt-4 font-heading text-3xl font-bold text-[#25314d]">{release.date}</h2>
              </div>
            </div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {release.summary.map((item) => (
                <div
                  key={`${release.version}:${item}`}
                  className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-4 text-sm leading-6 text-slate-700 shadow-[0_4px_0_#25314d]"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
