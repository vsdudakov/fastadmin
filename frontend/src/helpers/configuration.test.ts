import { describe, expect, it } from "vitest";
import type { IConfiguration, IModel } from "@/interfaces/configuration";
import { getConfigurationModel } from "./configuration";

describe("getConfigurationModel", () => {
  const baseModel: IModel = {
    name: "User",
    verbose_name: "User",
    verbose_name_plural: "Users",
    fields: [],
    search_fields: [],
    actions: [],
    permissions: [],
  };

  it("returns model when found by name", () => {
    const config: IConfiguration = {
      models: [baseModel],
      dashboard_widgets: [],
      primary_color: "#000",
      site_name: "Admin",
      username_field: "username",
      site_favicon: "",
    };
    expect(getConfigurationModel(config, "User")).toEqual(baseModel);
  });

  it("returns undefined when model not found", () => {
    const config: IConfiguration = {
      models: [baseModel],
      dashboard_widgets: [],
      primary_color: "#000",
      site_name: "Admin",
      username_field: "username",
      site_favicon: "",
    };
    expect(getConfigurationModel(config, "Missing")).toBeUndefined();
  });

  it("returns inline model when found in inlines", () => {
    const inlineModel = {
      ...baseModel,
      name: "InlineModel",
      fk_name: "parent_id",
    };
    const config: IConfiguration = {
      models: [
        {
          ...baseModel,
          inlines: [inlineModel],
        },
      ],
      dashboard_widgets: [],
      primary_color: "#000",
      site_name: "Admin",
      username_field: "username",
      site_favicon: "",
    };
    expect(getConfigurationModel(config, "InlineModel")).toEqual(inlineModel);
  });
});
