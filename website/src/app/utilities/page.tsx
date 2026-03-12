import Link from "next/link";
import { apiInventory } from "@/lib/generated";

const utilityGroup = apiInventory.find((group) => group.module === "psyflow.utils");

function UtilityList({ title, names }: { title: string; names: string[] }) {
  const exports = (utilityGroup?.exports ?? []).filter((item) => names.includes(item.name));
  return (
    <div className="pf-frame-soft h-full bg-[#fffdf9] p-5">
      <div className="rounded-full bg-[#ddd7f4] px-3 py-1 text-xs font-bold text-[#25314d]">{title}</div>
      <div className="mt-5 space-y-4">
        {exports.map((item) => (
          <a
            key={item.name}
            href={item.source_url}
            target="_blank"
            rel="noreferrer"
            className="block rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-4 shadow-[0_4px_0_#25314d]"
          >
            <div className="font-mono text-sm font-semibold text-[#25314d]">{item.name}</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">
              {item.summary || "Public utility export from psyflow.utils."}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

export default function UtilitiesPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_460px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">Utilities</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Reduce Boilerplate,
            <br />
            <span className="text-[#39d95d]">Keep Helpers Reusable,</span>
            <br />
            Stay Close to Runtime Reality.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            The public utility layer now covers config loading, validation, experiment setup,
            countdowns, ports, voice discovery, template generation, and generic trial bookkeeping.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="rounded-[22px] border-2 border-[#25314d] bg-[#eef8ff] p-5 shadow-[0_4px_0_#25314d]">
            <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Current exports</div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm font-semibold text-[#25314d]">
              {(utilityGroup?.exports ?? []).map((item) => (
                <div key={item.name} className="rounded-[14px] border border-slate-200 bg-white px-3 py-2">
                  {item.name}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <UtilityList
          title="Config + init"
          names={["load_config", "validate_config", "initialize_exp", "taps"]}
        />
        <UtilityList title="Runtime helpers" names={["count_down", "show_ports", "list_supported_voices"]} />
        <UtilityList
          title="Trial bookkeeping"
          names={["next_trial_id", "reset_trial_counter", "resolve_deadline", "resolve_trial_id"]}
        />
        <div className="pf-frame-soft h-full bg-[#efffe9] p-5">
          <div className="rounded-full bg-[#fffdf9] px-3 py-1 text-xs font-bold text-[#25314d]">
            Practical guidance
          </div>
          <div className="mt-4 font-heading text-[1.9rem] font-bold leading-tight text-[#25314d]">
            Use utilities when they remove generic work, not to hide task logic.
          </div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Keep participant-facing text in config or stimulus definitions.
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Use generic trial helpers before adding task-specific controller glue.
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Prefer the public exports here over copying helper code into each task.
            </div>
          </div>
          <div className="mt-6">
            <Link className="pf-focus-ring pf-button-secondary" href="/tutorials/utilities/">
              Read utilities tutorial
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
