import { renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, test } from "vitest";

import { usePageMeta } from "./usePageMeta";

const ORIGINAL_TITLE = document.title;

beforeEach(() => {
  document.title = "";
  document.head.innerHTML = "";
});

afterEach(() => {
  document.title = ORIGINAL_TITLE;
  document.head.innerHTML = "";
});

test("creates and updates title, description and favicon tags", () => {
  renderHook(() =>
    usePageMeta({
      title: "Dashboard",
      description: "Dashboard page",
      faviconHref: "/favicon-a.ico",
    }),
  );

  expect(document.title).toBe("Dashboard");
  expect(
    document.querySelector('meta[name="description"]')?.getAttribute("content"),
  ).toBe("Dashboard page");
  expect(document.querySelector('link[rel="icon"]')?.getAttribute("href")).toBe(
    "/favicon-a.ico",
  );
});

test("reuses existing description and favicon tags", () => {
  const descriptionTag = document.createElement("meta");
  descriptionTag.name = "description";
  descriptionTag.setAttribute("content", "old-description");
  document.head.append(descriptionTag);

  const faviconTag = document.createElement("link");
  faviconTag.rel = "icon";
  faviconTag.setAttribute("href", "/old.ico");
  document.head.append(faviconTag);

  renderHook(() =>
    usePageMeta({
      description: "new-description",
      faviconHref: "/new.ico",
    }),
  );

  const descriptionTags = document.querySelectorAll('meta[name="description"]');
  const faviconTags = document.querySelectorAll('link[rel="icon"]');

  expect(descriptionTags).toHaveLength(1);
  expect(faviconTags).toHaveLength(1);
  expect(descriptionTags[0]?.getAttribute("content")).toBe("new-description");
  expect(faviconTags[0]?.getAttribute("href")).toBe("/new.ico");
});

test("does not change title when title is omitted", () => {
  document.title = "Existing Title";

  renderHook(() =>
    usePageMeta({
      description: "Only description",
    }),
  );

  expect(document.title).toBe("Existing Title");
  expect(
    document.querySelector('meta[name="description"]')?.getAttribute("content"),
  ).toBe("Only description");
});
