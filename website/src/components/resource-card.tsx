import Link from "next/link";
import { IconArrowRight } from "@/components/icons";

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
  const body = (
    <div className="flex h-full flex-col justify-between gap-4">
      <div>
        <span className="inline-flex rounded-full bg-[#e2f3fb] px-3 py-1 text-xs font-bold text-[#25314d]">
          {eyebrow}
        </span>
        <div className="mt-4 font-heading text-[1.55rem] font-bold leading-tight text-[#25314d]">
          {title}
        </div>
        <div className="mt-3 max-w-[38ch] text-sm leading-7 text-slate-700">{description}</div>
      </div>
      <div className="inline-flex items-center gap-2 text-sm font-bold text-[#25314d]">
        {cta}
        <IconArrowRight className="size-4" />
      </div>
    </div>
  );

  const className = "pf-frame-soft h-full min-h-[180px] p-5";

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
