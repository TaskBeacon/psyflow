import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import rehypeHighlight from "rehype-highlight";
import { withBasePath } from "@/lib/base-path";

function isAbsoluteUrl(url: string) {
  return /^https?:\/\//i.test(url) || /^data:/i.test(url);
}

export function Markdown({ markdown }: { markdown: string }) {
  return (
    <ReactMarkdown
      className="pf-prose"
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[[rehypeHighlight, { ignoreMissing: true }], rehypeSlug]}
      components={{
        a: ({ href, children, ...props }) => {
          const targetHref = href && !isAbsoluteUrl(href) ? withBasePath(href) : href;
          const external = Boolean(targetHref && /^https?:\/\//i.test(targetHref));
          return (
            <a
              href={targetHref}
              target={external ? "_blank" : undefined}
              rel={external ? "noreferrer" : undefined}
              {...props}
            >
              {children}
            </a>
          );
        },
        img: ({ src, alt, ...props }) => {
          const targetSrc =
            src && !isAbsoluteUrl(src) ? withBasePath(src.startsWith("/") ? src : `/images/tutorials/${src}`) : src;
          return <img src={targetSrc} alt={alt ?? ""} loading="lazy" {...props} />;
        },
        pre: ({ children }) => (
          <pre className="not-prose overflow-x-auto rounded-xl border border-slate-200 bg-slate-950 p-4 text-slate-50">
            {children}
          </pre>
        ),
        code: ({ className, children, ...props }) => (
          <code
            className={
              className
                ? className
                : "rounded bg-slate-100 px-1 py-0.5 font-mono text-[0.9em] text-slate-900"
            }
            {...props}
          >
            {children}
          </code>
        )
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
}
