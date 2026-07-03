import { describe, expect, it } from "vitest";

import { isSafeUrl, toSafeFileUrl } from "@/helpers/url";

describe("isSafeUrl", () => {
  it("accepts http(s) and site-relative URLs", () => {
    expect(isSafeUrl("http://example.com/a.pdf")).toBe(true);
    expect(isSafeUrl("https://example.com/a.pdf")).toBe(true);
    expect(isSafeUrl("/media/a.pdf")).toBe(true);
  });

  it("rejects dangerous and empty values", () => {
    expect(isSafeUrl("javascript:alert(document.cookie)")).toBe(false);
    expect(isSafeUrl("JavaScript:alert(1)")).toBe(false);
    expect(isSafeUrl("data:text/html,<script>alert(1)</script>")).toBe(false);
    expect(isSafeUrl("vbscript:msgbox(1)")).toBe(false);
    expect(isSafeUrl("")).toBe(false);
    expect(isSafeUrl(undefined)).toBe(false);
    expect(isSafeUrl(42)).toBe(false);
  });
});

describe("toSafeFileUrl", () => {
  it("returns absolute http(s) URLs unchanged", () => {
    expect(toSafeFileUrl("https://cdn/a.png", "http://srv")).toBe("https://cdn/a.png");
  });

  it("prefixes the server domain for relative paths", () => {
    expect(toSafeFileUrl("/media/a.png", "http://srv")).toBe("http://srv/media/a.png");
  });

  it("returns undefined for dangerous schemes", () => {
    expect(toSafeFileUrl("javascript:alert(1)", "http://srv")).toBeUndefined();
    expect(toSafeFileUrl("s3://bucket/key", "http://srv")).toBeUndefined();
  });
});
