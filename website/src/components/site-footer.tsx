import { changelog, siteData } from "@/lib/generated";
import { PsyFlowLogo } from "@/components/psyflow-logo";

export function SiteFooter() {
  const latest = changelog[0] ?? siteData.latest_release;

  return (
    <footer className="mt-20 bg-[#efe7de]">
      <div className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="pf-frame bg-[#fff8f0] px-5 py-7 sm:px-6 sm:py-8">
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-center">
            <div className="text-center lg:text-left">
              <PsyFlowLogo className="mx-auto lg:mx-0" imageClassName="w-[148px] sm:w-[176px]" />
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-700 lg:max-w-xl">
                PsyFlow keeps the local task runtime, trigger model, QA flow, and validation path inside
                one auditable package.
              </p>
              {latest ? (
                <div className="mt-4 text-sm text-slate-600">
                  Latest documented release: {latest.version} · {latest.date}
                </div>
              ) : null}
            </div>

            <div className="lg:justify-self-end">
              <div className="pf-frame-soft flex items-center justify-center bg-[#eef8ff] px-4 py-5 sm:px-6 sm:py-6">
                <PsyFlowLogo imageClassName="w-[194px] sm:w-[228px]" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
