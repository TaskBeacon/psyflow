import clsx from "@/components/utils/clsx";

export function PsyFlowMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 120 96"
      role="img"
      aria-label="PsyFlow logo"
      className={clsx("h-auto w-[120px]", className)}
    >
      <g fill="none" stroke="#25314d" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="8" y="10" width="44" height="34" rx="10" fill="#48b6b2" />
        <rect x="38" y="18" width="44" height="34" rx="10" fill="#2d7eaa" />
        <rect x="68" y="10" width="44" height="34" rx="10" fill="#48b6b2" />
        <path d="M18 60h78" />
        <path d="M84 52l14 8-14 8" />
        <path d="M26 23v8" />
        <path d="M22 27h8" />
        <path d="M90 23v8" />
        <path d="M86 27h8" />
        <path d="M58 22v12" />
        <path d="M52 24c0-4 12-4 12 0" stroke="#65d7b9" />
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
        psyflow
      </span>
    </span>
  );
}
