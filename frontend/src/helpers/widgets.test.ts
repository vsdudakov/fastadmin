import { describe, expect, it } from "vitest";
import { EFieldWidgetType } from "@/interfaces/configuration";
import { getWidgetCls } from "./widgets";

describe("getWidgetCls", () => {
  const _t = (s: string) => s;

  it("returns Input for Input type", () => {
    const [Cls, props] = getWidgetCls(EFieldWidgetType.Input, _t);
    expect(Cls).toBeDefined();
    expect(props).toEqual({});
  });

  it("returns InputNumber with style", () => {
    const [, props] = getWidgetCls(EFieldWidgetType.InputNumber, _t);
    expect(props).toEqual({ style: { width: "100%" } });
  });

  it("returns PasswordInput with parentId when id given", () => {
    const [, props] = getWidgetCls(
      EFieldWidgetType.PasswordInput,
      _t,
      "form-id",
    );
    expect(props).toEqual({ parentId: "form-id" });
  });

  it("returns UploadInput with parentId when id given", () => {
    const [, props] = getWidgetCls(EFieldWidgetType.Upload, _t, "form-id");
    expect(props).toEqual({ parentId: "form-id" });
  });

  it("returns DatePicker.RangePicker with placeholder", () => {
    const [, props] = getWidgetCls(EFieldWidgetType.RangePicker, _t);
    expect((props as any).placeholder).toEqual(["Start", "End"]);
  });

  it("returns default Input for unknown type", () => {
    const [Cls, props] = getWidgetCls("Unknown" as EFieldWidgetType, _t);
    expect(Cls).toBeDefined();
    expect(props).toEqual({});
  });

  const typesToCover = [
    EFieldWidgetType.EmailInput,
    EFieldWidgetType.PhoneInput,
    EFieldWidgetType.SlugInput,
    EFieldWidgetType.UrlInput,
    EFieldWidgetType.TextArea,
    EFieldWidgetType.RichTextArea,
    EFieldWidgetType.JsonTextArea,
    EFieldWidgetType.Select,
    EFieldWidgetType.AsyncSelect,
    EFieldWidgetType.AsyncTransfer,
    EFieldWidgetType.Switch,
    EFieldWidgetType.Checkbox,
    EFieldWidgetType.CheckboxGroup,
    EFieldWidgetType.RadioGroup,
    EFieldWidgetType.DatePicker,
    EFieldWidgetType.TimePicker,
    EFieldWidgetType.DateTimePicker,
  ] as const;

  typesToCover.forEach((widgetType) => {
    it(`returns [Component, props] for ${widgetType}`, () => {
      const [Cls, props] = getWidgetCls(widgetType, _t);
      expect(Cls).toBeDefined();
      expect(props !== undefined).toBe(true);
    });
  });
});
