import clsx from "@/components/utils/clsx";

export function PsyFlowMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 126 86"
      role="img"
      aria-label="PsyFlow mark"
      className={clsx("h-auto w-[92px] sm:w-[104px]", className)}
    >
      <g fill="none" stroke="#0f2d57" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round">
        <rect x="6" y="13" width="44" height="36" rx="10" fill="#44b7b2" />
        <rect x="35" y="7" width="52" height="40" rx="12" fill="#1f7398" />
        <rect x="72" y="17" width="44" height="36" rx="10" fill="#44b7b2" />
        <path d="M14 61l92 12" />
        <path d="M95 64l15 10-18 3" />
        <path d="M24 26v10" />
        <path d="M19 31h10" />
        <path d="M93 30v10" />
        <path d="M88 35h10" />
        <path d="M58 21v15" stroke="#69d7c0" />
        <path d="M50 23c0-5 16-5 16 0" stroke="#69d7c0" />
      </g>
    </svg>
  );
}

export function PsyFlowLogo({
  className,
  markClassName,
  wordmarkClassName,
  showWordmark = true
}: {
  className?: string;
  markClassName?: string;
  wordmarkClassName?: string;
  showWordmark?: boolean;
}) {
  return (
    <span className={clsx("inline-flex items-center gap-3", className)}>
      <PsyFlowMark className={markClassName} />
      {showWordmark ? (
        <span
          className={clsx(
            "font-heading text-[1.9rem] leading-none text-[#25314d] sm:text-[2.2rem]",
            wordmarkClassName
          )}
        >
          PsyFlow
        </span>
      ) : null}
    </span>
  );
}
