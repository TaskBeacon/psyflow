import type { Metadata } from "next";
import "@/app/globals.css";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: {
    default: "PsyFlow",
    template: "%s | PsyFlow"
  },
  description:
    "Canonical local framework for auditable PsychoPy task development, QA, simulation, validation, and trigger I/O.",
  metadataBase: new URL("https://taskbeacon.github.io/psyflow/")
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="pf-grid-bg min-h-screen">
          <SiteHeader />
          <main className="mx-auto w-full max-w-7xl px-4 pb-12 pt-32 sm:px-6 lg:px-8">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
