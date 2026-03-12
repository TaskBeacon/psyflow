import { apiInventory } from "@/lib/generated";

export default function ApiPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_420px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">API</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Generated Module
            <br />
            <span className="text-[#39d95d]">Inventory,</span>
            <br />
            Not a Frozen Autodoc Snapshot.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            This page is built from the current package exports so the public surface stays aligned
            with the codebase even when the prose pages lag behind for a moment.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="space-y-4 text-sm leading-7 text-slate-700">
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 shadow-[0_4px_0_#25314d]">
              Covers the root package plus psyflow.utils, psyflow.io, psyflow.qa, and psyflow.sim.
            </div>
            <div className="rounded-[18px] border-2 border-[#25314d] bg-[#fff3ed] px-4 py-4 shadow-[0_4px_0_#25314d]">
              Each export links back to the current source file on GitHub.
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-8">
        {apiInventory.map((group) => (
          <div key={group.module} className="pf-frame bg-[#fffdf9] p-6">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="rounded-full bg-[#ddd7f4] px-3 py-1 text-xs font-bold text-[#25314d]">
                  {group.module}
                </div>
                <h2 className="mt-4 font-heading text-3xl font-bold text-[#25314d]">{group.module}</h2>
                <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-700">
                  {group.summary || "Public exports currently exposed by this module group."}
                </p>
              </div>
              <div className="text-sm font-semibold text-slate-600">{group.exports.length} exports</div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {group.exports.map((item) => (
                <a
                  key={`${group.module}:${item.name}`}
                  href={item.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-[20px] border-2 border-[#25314d] bg-white px-4 py-4 shadow-[0_4px_0_#25314d]"
                >
                  <div className="font-mono text-sm font-semibold text-[#25314d]">{item.name}</div>
                  <div className="mt-2 text-xs font-bold uppercase tracking-[0.14em] text-slate-500">
                    {item.source_module}
                  </div>
                  <div className="mt-3 text-sm leading-6 text-slate-700">
                    {item.summary || "No docstring summary was found for this export."}
                  </div>
                </a>
              ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
