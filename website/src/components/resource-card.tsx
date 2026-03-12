import Link from "next/link";
import { IconArrowRight } from "@/components/icons";

const TONES = [
  { bg: "bg-[#f5c1b5]", pill: "bg-[#ffe2d8]" },
  { bg: "bg-[#b9dceb]", pill: "bg-[#e2f3fb]" },
  { bg: "bg-[#c9f7b9]", pill: "bg-[#ecffe5]" },
  { bg: "bg-[#ddd7f4]", pill: "bg-[#f1eeff]" }
];

export function ResourceCard({
  eyebrow = "Resource",
  title,
  description,
  href,
  cta,
  external = false
}: {
  eyebrow?: string;
  title: string;
  description: string;
  href: string;
  cta: string;
  external?: boolean;
}) {
  const tone = TONES[title.length % TONES.length];

  const body = (
    <>
      <div className="flex items-start gap-4">
        <span
          className={`mt-1 block size-14 shrink-0 rounded-[18px] border-2 border-[#25314d] ${tone.bg} shadow-[0_4px_0_#25314d]`}
          aria-hidden="true"
        />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <span className={`rounded-full px-3 py-1 text-xs font-bold text-[#25314d] ${tone.pill}`}>
              {eyebrow}
            </span>
            <span className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
              Resource
            </span>
          </div>
          <div className="mt-3 font-heading text-[1.65rem] font-bold leading-tight text-[#25314d]">
            {title}
          </div>
          <div className="mt-2 max-w-[34ch] text-sm leading-6 text-slate-700">{description}</div>
          <div className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-[#25314d]">
            {cta}
            <IconArrowRight className="size-4" />
          </div>
        </div>
      </div>
    </>
  );

  const className = "pf-frame-soft flex h-full min-h-[206px] flex-col justify-between p-5";

  if (external) {
    return (
      <a className={className} href={href} target="_blank" rel="noreferrer">
        {body}
      </a>
    );
  }

  return (
    <Link className={className} href={href}>
      {body}
    </Link>
  );
}
