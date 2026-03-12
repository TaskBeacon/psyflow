import Link from "next/link";
import { apiInventory } from "@/lib/generated";

const ioGroup = apiInventory.find((group) => group.module === "psyflow.io");

const layers = [
  {
    step: "1",
    title: "Task code emits semantic trigger events",
    body: "Trial code should name events and codes, not own serial bytes or pulse-reset policy."
  },
  {
    step: "2",
    title: "TriggerRuntime owns timing semantics",
    body: "Emit now or on-flip, log planned and executed records, and enforce strict capability checks when requested."
  },
  {
    step: "3",
    title: "Drivers own hardware protocol",
    body: "Use mock, callable, serial, or fanout drivers depending on environment and delivery needs."
  },
  {
    step: "4",
    title: "QA and logs keep the path auditable",
    body: "Event logs, simulation context, and QA artifacts preserve what happened without binding tasks to one device API."
  }
];

export default function TriggersPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_520px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">Triggers & I/O</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Keep Tasks
            <br />
            <span className="text-[#39d95d]">Hardware-Agnostic,</span>
            <br />
            Still Audit the Signal Path.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            PsyFlow no longer treats trigger sending as a single helper object. The current model
            separates semantic events, runtimes, and drivers so labs can swap hardware without
            rewriting task logic.
          </p>
        </div>

        <div className="pf-frame bg-[#fffdf9] p-6">
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Current init helper</div>
          <pre className="mt-4 overflow-x-auto rounded-[18px] border-2 border-[#25314d] bg-[#eef8ff] px-4 py-4 font-mono text-sm font-semibold text-[#25314d] shadow-[0_4px_0_#25314d]">
            <code>initialize_triggers(cfg, trigger_func=None, mock=None)</code>
          </pre>
          <div className="mt-4 text-sm leading-7 text-slate-700">
            Driver selection currently supports mock, callable, serial_port, and serial_url modes,
            with strict policy and timing config read from task config.
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {layers.map((layer) => (
          <div key={layer.step} className="pf-frame-soft h-full bg-[#fffdf9] p-5">
            <div className="flex items-center gap-3">
              <div className="flex size-11 items-center justify-center rounded-full border-2 border-[#25314d] bg-[#f5c1b5] text-lg font-bold text-[#25314d] shadow-[0_4px_0_#25314d]">
                {layer.step}
              </div>
              <div className="font-heading text-[1.5rem] font-bold leading-tight text-[#25314d]">
                {layer.title}
              </div>
            </div>
            <div className="mt-4 text-sm leading-7 text-slate-700">{layer.body}</div>
          </div>
        ))}
      </section>

      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="pf-frame-soft bg-[#fffdf9] p-5">
          <div className="rounded-full bg-[#d9edf6] px-3 py-1 text-xs font-bold text-[#25314d]">Public I/O exports</div>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {(ioGroup?.exports ?? []).map((item) => (
              <a
                key={item.name}
                href={item.source_url}
                target="_blank"
                rel="noreferrer"
                className="rounded-[18px] border-2 border-[#25314d] bg-white px-4 py-4 shadow-[0_4px_0_#25314d]"
              >
                <div className="font-mono text-sm font-semibold text-[#25314d]">{item.name}</div>
                <div className="mt-2 text-sm leading-6 text-slate-700">
                  {item.summary || "Public export from psyflow.io."}
                </div>
              </a>
            ))}
          </div>
        </div>

        <div className="pf-frame-soft bg-[#efffe9] p-5">
          <div className="font-heading text-[1.9rem] font-bold leading-tight text-[#25314d]">
            Recommended workflow
          </div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Use MockDriver during local development and QA.
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Move protocol details into driver config instead of task code branches.
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              Keep strict mode available when hardware capability mismatches should fail fast.
            </div>
          </div>
          <div className="mt-6">
            <Link className="pf-focus-ring pf-button-secondary" href="/tutorials/trigger-io/">
              Read trigger tutorial
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
