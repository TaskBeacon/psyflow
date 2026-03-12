import clsx from "@/components/utils/clsx";

export function PsyFlowMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 96 96"
      role="img"
      aria-label="PsyFlow logo"
      className={clsx("size-12", className)}
    >
      <g
        fill="none"
        stroke="#25314d"
        strokeWidth="3.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="14" y="14" width="68" height="68" rx="22" fill="#c6def2" />
        <path d="M26 58c8-14 16-22 26-22 9 0 13 4 18 12" stroke="#ef8b67" strokeWidth="7" />
        <circle cx="28" cy="60" r="8" fill="#fff7ef" />
        <circle cx="51" cy="36" r="8" fill="#fff7ef" />
        <circle cx="71" cy="49" r="8" fill="#fff7ef" />
        <path d="M62 67h10" stroke="#39d95d" strokeWidth="7" />
        <path d="M67 62v10" stroke="#39d95d" strokeWidth="7" />
      </g>
    </svg>
  );
}

export function PsyFlowLogo({
  className,
  markClassName,
  textClassName
}: {
  className?: string;
  markClassName?: string;
  textClassName?: string;
}) {
  return (
    <span className={clsx("inline-flex items-center gap-3", className)}>
      <PsyFlowMark className={markClassName} />
      <span className={clsx("font-heading text-2xl leading-none text-[#25314d]", textClassName)}>
        PsyFlow
      </span>
    </span>
  );
}
