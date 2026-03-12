import Link from "next/link";
import Image from "next/image";
import { ResourceCard } from "@/components/resource-card";
import { withBasePath } from "@/lib/base-path";
import { frameworkCards } from "@/lib/site-content";

function PrimitiveCard({
  name,
  summary,
  details
}: {
  name: string;
  summary: string;
  details: string[];
}) {
  return (
    <div className="pf-frame-soft h-full bg-[#fffdf9] p-5">
      <div className="rounded-full bg-[#e2f3fb] px-3 py-1 text-xs font-bold text-[#25314d]">{name}</div>
      <div className="mt-4 font-heading text-[1.8rem] font-bold leading-tight text-[#25314d]">
        {summary}
      </div>
      <div className="mt-5 space-y-3">
        {details.map((detail) => (
          <div key={detail} className="rounded-[16px] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
            {detail}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function FrameworkPage() {
  return (
    <div className="space-y-16 pb-8">
      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_520px] lg:items-center">
        <div>
          <div className="pf-badge mx-auto w-fit">Framework</div>
          <h1 className="mt-6 max-w-3xl font-heading text-5xl font-bold leading-[0.94] text-[#25314d] sm:text-6xl">
            Author Locally,
            <br />
            <span className="text-[#39d95d]">Keep Logic Auditable,</span>
            <br />
            Export Clean Outputs.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-700">
            PsyFlow is opinionated about task structure because experiments become much easier to
            review when config, participant info, trial flow, and output paths have stable homes.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link className="pf-focus-ring pf-button-primary" href="/tutorials/getting-started/">
              Start from template
            </Link>
            <Link className="pf-focus-ring pf-button-secondary" href="/utilities/">
              See utilities
            </Link>
          </div>
        </div>

        <div className="pf-frame overflow-hidden bg-[#fffdf9] p-4">
          <Image
            src={withBasePath("/images/framework/flowchart.png")}
            alt="PsyFlow framework flowchart"
            width={1600}
            height={1200}
            className="w-full rounded-[24px] border-2 border-[#25314d] bg-white shadow-[0_5px_0_#25314d]"
          />
        </div>
      </section>

      <section className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip">Core Primitives</div>
          <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
            The framework pieces that should appear in most canonical tasks
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <PrimitiveCard
            name="BlockUnit"
            summary="Own block-level condition selection and result collation."
            details={[
              "Use block indices explicitly instead of inferring them from surrounding code.",
              "Keep condition generation reviewable rather than burying it inside callbacks.",
              "Return structured results that survive QA and downstream analysis."
            ]}
          />
          <PrimitiveCard
            name="StimBank"
            summary="Define reusable stimuli separately from per-trial execution."
            details={[
              "Register definitions in Python or YAML-backed patterns.",
              "Format participant-facing text through config-driven values.",
              "Reuse the same source for local runtime and reference documentation."
            ]}
          />
          <PrimitiveCard
            name="StimUnit"
            summary="Run a single trial cleanly with state, timing, and response handling."
            details={[
              "Keep a trial as one inspectable unit rather than scattered imperative code.",
              "Attach runtime state needed by QA or simulation.",
              "Pair naturally with TriggerRuntime and responder-aware context helpers."
            ]}
          />
          <PrimitiveCard
            name="SubInfo"
            summary="Collect participant/session info without custom GUI boilerplate."
            details={[
              "Drive forms from YAML or dict config rather than hardcoded dialog setup.",
              "Feed subject info straight into TaskSettings for output naming and seeds.",
              "Use localized labels and validation rules from config."
            ]}
          />
          <PrimitiveCard
            name="TaskSettings"
            summary="Centralize paths, seeds, task shape, and optional condition weights."
            details={[
              "Use from_dict() to flatten runtime config into one container.",
              "Attach participant info with add_subinfo() before saving outputs.",
              "Resolve condition weights at the framework layer with resolve_condition_weights()."
            ]}
          />
          <PrimitiveCard
            name="TAPS Relationship"
            summary="Use PsyFlow inside a task package that stays reviewable outside Python code."
            details={[
              "PsyFlow handles local runtime behavior and helpers.",
              "TAPS defines the package shape around config, docs, references, and outputs.",
              "Validation and QA work best when the package follows that structure consistently."
            ]}
          />
        </div>
      </section>

      <section className="space-y-8">
        <div className="text-center">
          <div className="pf-section-chip bg-[#f5c1b5]">Overview</div>
          <h2 className="mt-5 font-heading text-4xl font-bold text-[#25314d]">
            Jump from the core primitives to the working guides
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-2">
          {frameworkCards.map((card) => (
            <ResourceCard key={card.title} {...card} />
          ))}
        </div>
      </section>
    </div>
  );
}
