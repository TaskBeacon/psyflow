import { changelog } from "@/lib/generated";

const releaseBackgrounds = [
  "bg-[#fffdf9]",
  "bg-[#eef8ff]",
  "bg-[#fff3ed]",
  "bg-[#efffe9]",
  "bg-[#f4f0ff]"
] as const;

const releaseChipBackgrounds = [
  "bg-[#d9edf6]",
  "bg-[#f8d8cf]",
  "bg-[#dff2d7]",
  "bg-[#ddd7f4]",
  "bg-[#f3e2d5]"
] as const;

export default function ChangelogPage() {
  return (
    <div className="space-y-8 pb-8 pt-2 sm:space-y-10 sm:pt-4">
      <section>
        <h1 className="font-heading text-4xl font-bold leading-[0.95] text-[#25314d] sm:text-5xl lg:text-6xl">
          Changes
        </h1>
      </section>

      <section className="space-y-5">
        {changelog.map((release, index) => (
          <article
            key={release.version}
            className={`pf-frame p-5 sm:p-6 ${releaseBackgrounds[index % releaseBackgrounds.length]}`}
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-3">
                <span
                  className={`inline-flex rounded-full border-2 border-[#25314d] px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-[#25314d] shadow-[0_3px_0_#25314d] ${releaseChipBackgrounds[index % releaseChipBackgrounds.length]}`}
                >
                  Version {release.version}
                </span>
                <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">
                  Release Notes
                </span>
              </div>
              <div className="text-sm font-medium text-slate-600">{release.date}</div>
            </div>

            <div className="mt-5 space-y-3 text-sm leading-7 text-slate-700">
              {release.summary.map((item) => (
                <p key={`${release.version}:${item}`}>{item}</p>
              ))}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
