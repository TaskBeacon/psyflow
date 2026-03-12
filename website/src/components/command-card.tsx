type Tone = "sky" | "peach" | "mint" | "lavender";

const toneClasses: Record<Tone, string> = {
  sky: "bg-[#eef8ff]",
  peach: "bg-[#fff3ed]",
  mint: "bg-[#efffe9]",
  lavender: "bg-[#f4f0ff]"
};

export function CommandCard({
  title,
  command,
  description,
  note,
  tone = "sky"
}: {
  title: string;
  command: string;
  description: string;
  note?: string;
  tone?: Tone;
}) {
  return (
    <div className={`pf-frame-soft h-full p-5 ${toneClasses[tone]}`}>
      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-500">{title}</div>
      <pre className="mt-3 overflow-x-auto rounded-[18px] border-2 border-[#25314d] bg-[#fffdf9] px-4 py-3 font-mono text-sm font-semibold text-[#25314d] shadow-[0_4px_0_#25314d]">
        <code>{command}</code>
      </pre>
      <p className="mt-4 text-sm leading-6 text-slate-700">{description}</p>
      {note ? <div className="mt-3 text-xs leading-5 text-slate-600">{note}</div> : null}
    </div>
  );
}
