// Guard against `javascript:`/`data:`/`vbscript:` URIs sneaking into an
// <a href>/file link. Stored field values (e.g. an upload field's value or a
// get_file_url result) are attacker-influenceable, so only http(s) and
// site-relative paths are treated as safe to render as links.

const SAFE_ABSOLUTE = /^https?:\/\//i;

export const isSafeUrl = (value: unknown): value is string => {
  if (typeof value !== "string" || !value) return false;
  const trimmed = value.trim();
  return SAFE_ABSOLUTE.test(trimmed) || trimmed.startsWith("/");
};

// Resolve a stored file value to a safe display URL, prefixing the server
// domain for site-relative paths. Returns undefined when the value is not a
// safe URL, so callers can omit the link entirely.
export const toSafeFileUrl = (value: string, serverDomain: string): string | undefined => {
  if (SAFE_ABSOLUTE.test(value)) return value;
  if (value.startsWith("/")) return `${serverDomain}${value}`;
  return undefined;
};
