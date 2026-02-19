import { describe, expect, it } from "vitest";
import type { IModel } from "@/interfaces/configuration";
import { getTitleFromFieldName, getTitleFromModel } from "./title";

describe("getTitleFromFieldName", () => {
  it("capitalizes words separated by underscore", () => {
    expect(getTitleFromFieldName("first_name")).toBe("First Name");
  });
});

describe("getTitleFromModel", () => {
  it("returns verbose_name when set", () => {
    const model: IModel = {
      name: "User",
      verbose_name: "User",
      verbose_name_plural: "Users",
      fields: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model)).toBe("User");
    expect(getTitleFromModel(model, true)).toBe("Users");
  });

  it("returns verbose_name_plural when plural=true", () => {
    const model: IModel = {
      name: "Event",
      verbose_name: "Event",
      verbose_name_plural: "Events",
      fields: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model, true)).toBe("Events");
  });

  it("appends s when plural=true and verbose_name_plural is missing", () => {
    const model: IModel = {
      name: "AuditLog",
      verbose_name: "Audit log",
      fields: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model, true)).toBe("Audit logs");
  });

  it("derives title from model name when no verbose_name", () => {
    const model: IModel = {
      name: "BaseEvent",
      fields: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model)).toBe("Base Event");
    expect(getTitleFromModel(model, true)).toBe("Base Events");
  });

  it("falls back to raw model name when regex has no matches", () => {
    const model: IModel = {
      name: "event",
      fields: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model)).toBe("event");
    expect(getTitleFromModel(model, true)).toBe("events");
  });
});
