import { changelog, siteData } from "@/lib/generated";
import { PsyFlowLogo, PsyFlowMark } from "@/components/psyflow-logo";

export function SiteFooter() {
  const latest = changelog[0] ?? siteData.latest_release;

  return (
    <footer className="mt-20 bg-[#efe7de]">
      <div className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="pf-frame bg-[#fff8f0] px-6 py-8">
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-center">
            <div>
              <PsyFlowLogo markClassName="size-11" textClassName="text-3xl" />
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-700">
                Canonical local framework for auditable PsychoPy task development, QA, simulation,
                validation, and hardware-aware runtime workflows.
              </p>
              <div className="mt-6 flex flex-wrap gap-6 text-sm text-slate-700">
                <div>{siteData.module_count} public module groups</div>
                <div>{siteData.release_count} documented releases</div>
                <div>Docs track current main branch behavior</div>
              </div>
              {latest ? (
                <div className="mt-4 text-xs text-slate-600">
                  Latest curated release: {latest.version} on {latest.date}
                </div>
              ) : null}
            </div>

            <div className="lg:justify-self-end">
              <div className="pf-frame-soft flex items-center justify-center bg-[#eef8ff] px-6 py-8">
                <div className="flex items-center gap-4">
                  <PsyFlowMark className="size-20" />
                  <div>
                    <div className="font-heading text-[2.2rem] leading-none text-[#25314d]">
                      PsyFlow
                    </div>
                    <div className="mt-2 text-sm font-bold uppercase tracking-[0.16em] text-slate-500">
                      Local Task Runtime
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
