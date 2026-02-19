import { describe, expect, it } from "vitest";
import { buildAddPath, buildChangePath, buildListPath, ROUTES } from "./routes";

describe("ROUTES", () => {
  it("has expected path constants", () => {
    expect(ROUTES.HOME).toBe("/");
    expect(ROUTES.SIGN_IN).toBe("/sign-in");
    expect(ROUTES.LIST).toBe("/list/:model");
    expect(ROUTES.ADD).toBe("/add/:model");
    expect(ROUTES.CHANGE).toBe("/change/:model/:id");
  });
});

describe("buildListPath", () => {
  it("returns /list/:model", () => {
    expect(buildListPath("django.Event")).toBe("/list/django.Event");
  });
});

describe("buildAddPath", () => {
  it("returns /add/:model", () => {
    expect(buildAddPath("django.Event")).toBe("/add/django.Event");
  });
});

describe("buildChangePath", () => {
  it("returns /change/:model/:id", () => {
    expect(buildChangePath("django.Event", 1)).toBe("/change/django.Event/1");
    expect(buildChangePath("django.Event", "abc")).toBe(
      "/change/django.Event/abc",
    );
  });
});
