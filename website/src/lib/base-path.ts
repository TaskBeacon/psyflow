export const SITE_BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/psyflow";

export function withBasePath(path: string): string {
  if (!path) return SITE_BASE_PATH || "/";
  if (/^https?:\/\//i.test(path) || /^data:/i.test(path)) return path;
  if (SITE_BASE_PATH && path.startsWith(SITE_BASE_PATH)) return path;
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${SITE_BASE_PATH}${normalized}`;
}
