"use client";

import Link from "next/link";
import { useState } from "react";
import { IconClose, IconGithub, IconMenu } from "@/components/icons";
import { PsyFlowLogo } from "@/components/psyflow-logo";
import { routes } from "@/lib/routes";

const NAV_LINKS = [
  { label: "Home", href: routes.home },
  { label: "Framework", href: routes.framework },
  { label: "Tutorials", href: routes.tutorials },
  { label: "Changelog", href: routes.changelog }
] as const;

function NavLink({
  href,
  label,
  mobile = false,
  onNavigate
}: {
  href: string;
  label: string;
  mobile?: boolean;
  onNavigate?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      className={
        mobile
          ? "pf-focus-ring block w-full rounded-[18px] border-2 border-[#25314d] bg-[#fffdf9] px-4 py-3 text-left text-base font-bold text-[#25314d] shadow-[0_4px_0_#25314d]"
          : "pf-focus-ring rounded-full px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:text-[#25314d]"
      }
    >
      {label}
    </Link>
  );
}

export function SiteHeader() {
  const [open, setOpen] = useState(false);

  return (
    <header className="fixed left-0 right-0 top-0 z-50">
      <div className="mx-auto w-full max-w-7xl px-3 pt-3 sm:px-6 sm:pt-4 lg:px-8">
        <div className="pf-frame bg-[#fffdf9] px-3 py-3 sm:px-4">
          <div className="flex items-center justify-between gap-3">
            <Link href={routes.home} className="pf-focus-ring rounded-xl" onClick={() => setOpen(false)}>
              <PsyFlowLogo markClassName="w-[74px] sm:w-[82px]" wordmarkClassName="text-[1.65rem] sm:text-[1.85rem]" />
            </Link>

            <nav className="hidden items-center gap-1 xl:flex">
              {NAV_LINKS.map((link) => (
                <NavLink key={link.href} {...link} />
              ))}
              <a
                className="pf-focus-ring rounded-full px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:text-[#25314d]"
                href="https://github.com/TaskBeacon/psyflow"
                target="_blank"
                rel="noreferrer"
              >
                GitHub
              </a>
              <Link className="pf-focus-ring pf-button-primary px-5 py-3 text-sm" href={routes.gettingStarted}>
                Get Started
              </Link>
            </nav>

            <button
              type="button"
              className="pf-focus-ring pf-frame-soft shrink-0 p-2 xl:hidden"
              aria-expanded={open}
              aria-label={open ? "Close navigation menu" : "Open navigation menu"}
              onClick={() => setOpen((value) => !value)}
            >
              {open ? <IconClose className="size-5" /> : <IconMenu className="size-5" />}
            </button>
          </div>

          {open ? (
            <div className="mt-4 rounded-[24px] border-2 border-[#25314d] bg-[#fffdf9] p-3 shadow-[0_5px_0_#25314d] xl:hidden">
              <div className="grid gap-2">
                {NAV_LINKS.map((link) => (
                  <NavLink key={link.href} {...link} mobile onNavigate={() => setOpen(false)} />
                ))}
              </div>
              <div className="mt-3 grid gap-2">
                <a
                  className="pf-focus-ring pf-button-secondary w-full text-sm"
                  href="https://github.com/TaskBeacon/psyflow"
                  target="_blank"
                  rel="noreferrer"
                >
                  <IconGithub className="size-4" />
                  GitHub Repo
                </a>
                <Link
                  className="pf-focus-ring pf-button-primary w-full text-sm"
                  href={routes.gettingStarted}
                  onClick={() => setOpen(false)}
                >
                  Get Started
                </Link>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
