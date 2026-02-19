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
      list_display: [],
      list_filter: [],
      sortable_by: [],
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
      list_display: [],
      list_filter: [],
      sortable_by: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model, true)).toBe("Events");
  });

  it("derives title from model name when no verbose_name", () => {
    const model: IModel = {
      name: "BaseEvent",
      fields: [],
      list_display: [],
      list_filter: [],
      sortable_by: [],
      search_fields: [],
      actions: [],
      permissions: [],
    };
    expect(getTitleFromModel(model)).toBe("Base Event");
    expect(getTitleFromModel(model, true)).toBe("Base Events");
  });
});
