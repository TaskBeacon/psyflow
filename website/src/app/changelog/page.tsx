import { changelog, siteData } from "@/lib/generated";

export default function ChangelogPage() {
  return (
    <div className="space-y-12 pb-8">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-end">
        <div>
          <div className="pf-badge">Changelog</div>
          <h1 className="mt-5 max-w-4xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Read releases as one clear update at a time.
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-8 text-slate-700">
            This page follows the current repository history instead of over-indexing on one stale package
            version. Each release is shown as one readable block.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-5">
          <div className="space-y-3 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-3 shadow-[0_4px_0_#25314d]">
              Latest changelog release: {siteData.latest_release?.version ?? "unknown"}
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-3 shadow-[0_4px_0_#25314d]">
              Package metadata version: {siteData.project.version ?? "unknown"}
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-5">
        {changelog.map((release) => (
          <article key={release.version} className="pf-frame bg-[#fffdf9] p-6 sm:p-7">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="pf-section-chip bg-[#ddd7f4]">Version {release.version}</div>
                <h2 className="mt-4 font-heading text-3xl font-bold text-[#25314d]">{release.date}</h2>
              </div>
            </div>
            <ul className="mt-6 space-y-3 text-sm leading-7 text-slate-700">
              {release.summary.map((item) => (
                <li
                  key={`${release.version}:${item}`}
                  className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-3 shadow-[0_4px_0_#25314d]"
                >
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </div>
  );
}
