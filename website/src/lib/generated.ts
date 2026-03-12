import apiInventoryData from "@/data/generated/api-inventory.json";
import changelogData from "@/data/generated/changelog.json";
import cliCommandsData from "@/data/generated/cli-commands.json";
import siteDataJson from "@/data/generated/site-data.json";

export type ApiExport = {
  name: string;
  source_module: string;
  summary: string;
  source_url: string;
};

export type ApiGroup = {
  module: string;
  summary: string;
  exports: ApiExport[];
};

export type ReleaseEntry = {
  version: string;
  date: string;
  summary: string[];
};

export const apiInventory = apiInventoryData as ApiGroup[];
export const changelog = changelogData as ReleaseEntry[];
export const cliCommands = cliCommandsData as Record<string, string>;
export const siteData = siteDataJson as {
  project: {
    name: string;
    version: string | null;
    description: string;
    requires_python: string;
    scripts: Record<string, string>;
  };
  latest_release: ReleaseEntry | null;
  release_count: number;
  module_count: number;
};
