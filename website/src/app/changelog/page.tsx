import { changelog } from "@/lib/generated";

const releaseBackgrounds = [
  "bg-[#fffdf9]",
  "bg-[#eef8ff]",
  "bg-[#fff3ed]",
  "bg-[#efffe9]",
  "bg-[#f4f0ff]"
] as const;

export default function ChangelogPage() {
  return (
    <div className="space-y-8 pb-8">
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
            <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between">
              <div className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                Version {release.version}
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
