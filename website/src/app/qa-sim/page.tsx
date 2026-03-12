import Link from "next/link";
import { CommandCard } from "@/components/command-card";
import { apiInventory } from "@/lib/generated";

const qaGroup = apiInventory.find((group) => group.module === "psyflow.qa");
const simGroup = apiInventory.find((group) => group.module === "psyflow.sim");

function ExportPanel({
  title,
  exports
}: {
  title: string;
  exports: { name: string; summary: string; source_url: string }[];
}) {
  return (
    <div className="pf-frame-soft h-full bg-[#fffdf9] p-5">
      <div className="rounded-full bg-[#f5c1b5] px-3 py-1 text-xs font-bold text-[#25314d]">{title}</div>
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
              {item.summary || "Public export from this module."}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

export default function QaSimPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_520px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">QA & Sim</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Test Workflows,
            <br />
            <span className="text-[#39d95d]">Not Just Happy Paths,</span>
            <br />
            Before Shipping Tasks.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            QA mode now validates outputs and can promote maturity. Simulation uses a responder
            protocol with observation, action, feedback, and runtime context helpers.
          </p>
        </div>

        <div className="grid gap-4">
          <CommandCard
            title="QA smoke gate"
            command="psyflow-qa path/to/task"
            description="Run task QA mode, inspect generated artifacts, and update taskbeacon.yaml maturity on pass."
            note="Artifacts now include qa_report.json, static_report.json, contract_report.json, qa_trace.csv, and qa_events.jsonl."
            tone="mint"
          />
          <CommandCard
            title="Simulation"
            command="psyflow-sim path/to/task --config config/config_scripted_sim.yaml"
            description="Run deterministic or task-specific responders without bringing PsychoPy into the responder layer."
            tone="lavender"
          />
          <CommandCard
            title="Validation"
            command="psyflow-validate path/to/task"
            description="Lint contracts, README/reference artifacts, config rules, and localization-safe runtime policy."
            tone="sky"
          />
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <div className="pf-frame-soft bg-[#eef8ff] p-5">
          <div className="font-heading text-[1.8rem] font-bold text-[#25314d]">QA artifacts</div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">qa_report.json</div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">static_report.json</div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">contract_report.json</div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">qa_trace.csv + qa_events.jsonl</div>
          </div>
        </div>
        <div className="pf-frame-soft bg-[#fff3ed] p-5">
          <div className="font-heading text-[1.8rem] font-bold text-[#25314d]">Responder protocol</div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">SessionInfo starts the run.</div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">Observation describes the current trial state.</div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">Action returns key + RT.</div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">Feedback closes the loop per trial.</div>
          </div>
        </div>
        <div className="pf-frame-soft bg-[#f4f0ff] p-5">
          <div className="font-heading text-[1.8rem] font-bold text-[#25314d]">Context helpers</div>
          <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              set_trial_context() now resolves sequence deadlines via max() automatically.
            </div>
            <div className="rounded-[16px] border border-slate-200 bg-white px-4 py-3">
              RuntimeContext and context_from_config() keep sim config explicit.
            </div>
          </div>
        </div>
        <div className="pf-frame-soft bg-[#efffe9] p-5">
          <div className="font-heading text-[1.8rem] font-bold text-[#25314d]">Current stance</div>
          <div className="mt-4 text-sm leading-7 text-slate-700">
            Use scripted responders for baseline smoke coverage, then attach task-specific responders
            only when the paradigm genuinely needs custom sampling or state policy.
          </div>
          <div className="mt-6">
            <Link className="pf-focus-ring pf-button-secondary" href="/tutorials/qa-and-validation/">
              Read QA tutorial
            </Link>
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <ExportPanel title="psyflow.qa exports" exports={qaGroup?.exports ?? []} />
        <ExportPanel title="psyflow.sim exports" exports={simGroup?.exports ?? []} />
      </section>
    </div>
  );
}
