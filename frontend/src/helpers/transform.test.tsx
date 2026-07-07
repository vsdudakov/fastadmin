import dayjs from "dayjs";
import { describe, expect, it } from "vitest";
import { EFieldWidgetType } from "@/interfaces/configuration";
import {
  getChangeWidgetTypes,
  isArray,
  isBoolean,
  isDateTime,
  isJson,
  isNumeric,
  isSlug,
  isString,
  isTime,
  transformColumnValueFromServer,
  transformDataFromServer,
  transformDataToServer,
  transformFiltersToServer,
  transformValueFromServer,
  transformValueToServer,
} from "./transform";

describe("transform", () => {
  describe("isDateTime/isTime", () => {
    it("returns true for ISO date strings", () => {
      expect(isDateTime("2024-01-15")).toBe(true);
      expect(isDateTime("2024-01-15T12:00:00Z")).toBe(true);
      expect(isDateTime("2024-01-15T12:00:00.123456")).toBe(true);
      expect(isDateTime("2024-01-15 12:00")).toBe(true);
      expect(isTime("12:00:00")).toBe(true);
      expect(isTime("12:00")).toBe(true);
    });
    it("returns false for non-dates", () => {
      expect(isDateTime("hello")).toBe(false);
      expect(isDateTime("12")).toBe(false);
      expect(isTime("hello")).toBe(false);
      expect(isTime("12")).toBe(false);
    });
  });

  describe("isNumeric", () => {
    it("returns true for numbers", () => {
      expect(isNumeric("123")).toBe(true);
      expect(isNumeric("1.5")).toBe(true);
      expect(isNumeric("-1")).toBe(true);
    });
    it("returns false for non-numeric", () => {
      expect(isNumeric("abc")).toBe(false);
    });
  });

  describe("isArray", () => {
    it("returns true for arrays", () => {
      expect(isArray([])).toBe(true);
      expect(isArray([1, 2])).toBe(true);
    });
    it("returns false for non-arrays", () => {
      expect(isArray({})).toBe(false);
      expect(isArray("x")).toBe(false);
    });
  });

  describe("isBoolean", () => {
    it("returns true for true/false strings", () => {
      expect(isBoolean("true")).toBe(true);
      expect(isBoolean("false")).toBe(true);
    });
    it("returns false for others", () => {
      expect(isBoolean("1")).toBe(false);
    });
  });

  describe("isString", () => {
    it("returns true for string", () => {
      expect(isString("x")).toBe(true);
      expect(isString(new String("x"))).toBe(true);
    });
    it("returns false for non-string", () => {
      expect(isString(1)).toBe(false);
    });
  });

  describe("isJson", () => {
    it("returns true for valid JSON string", () => {
      expect(isJson('{"a":1}')).toBe(true);
    });
    it("returns false for invalid JSON", () => {
      expect(isJson("not json")).toBe(false);
    });
    it("stringifies object and parses", () => {
      expect(isJson({ a: 1 })).toBe(true);
    });
    it("returns false when JSON.parse throws", () => {
      expect(isJson("")).toBe(false);
    });
    it("returns false when JSON.stringify throws", () => {
      const circular: Record<string, unknown> = {};
      circular.self = circular;
      expect(isJson(circular)).toBe(false);
    });
  });

  describe("isSlug", () => {
    it("returns true when slugify equals value", () => {
      expect(isSlug("hello-world")).toBe(true);
    });
    it("returns false for non-string", () => {
      expect(isSlug(123)).toBe(false);
    });
    it("returns false when slugify throws", () => {
      const badValue = new String("hello-world");
      badValue.toString = () => {
        throw new Error("boom");
      };
      expect(isSlug(badValue)).toBe(false);
    });
  });

  describe("transformValueToServer", () => {
    it("returns value when falsy", () => {
      expect(transformValueToServer(null)).toBe(null);
      expect(transformValueToServer(undefined)).toBe(undefined);
    });
    it("maps over arrays", () => {
      expect(transformValueToServer([1, 2])).toEqual([1, 2]);
    });
    it("formats a real dayjs value", () => {
      const d = dayjs("2024-01-15");
      expect(transformValueToServer(d)).toBe(d.format());
    });
    it("returns non-dayjs value as-is", () => {
      expect(transformValueToServer({ a: 1 })).toEqual({ a: 1 });
      expect(transformValueToServer("hello")).toBe("hello");
    });
    it("does not treat a plain object with a `date` key as dayjs", () => {
      const value = { date: "2024-05-01", amount: 100 };
      expect(transformValueToServer(value)).toEqual(value);
    });
  });

  describe("transformDataToServer", () => {
    it("transforms all values", () => {
      const d = dayjs("2024-01-15");
      expect(transformDataToServer({ created: d })).toEqual({
        created: d.format(),
      });
    });
  });

  describe("transformFiltersToServer", () => {
    it("handles dayjs range", () => {
      const data = { created_at: ["2024-01-01", "2024-01-31"] };
      expect(transformFiltersToServer(data)).toEqual({
        created_at__gte: "2024-01-01",
        created_at__lte: "2024-01-31",
      });
    });
    it("handles __in array", () => {
      expect(transformFiltersToServer({ status: ["a", "b"] })).toEqual({
        status__in: "a,b",
      });
    });
    it("handles dayjs single", () => {
      expect(transformFiltersToServer({ d: "2024-01-15" })).toEqual({
        d: "2024-01-15",
      });
    });
    it("handles numeric", () => {
      expect(transformFiltersToServer({ n: "42" })).toEqual({ n: "42" });
    });
    it("handles boolean", () => {
      expect(transformFiltersToServer({ active: "true" })).toEqual({
        active: "true",
      });
    });
    it("handles other as icontains", () => {
      expect(transformFiltersToServer({ name: "foo" })).toEqual({
        name__icontains: "foo",
      });
    });
    it("handles empty arrays for __in filters", () => {
      expect(transformFiltersToServer({ status: [] })).toEqual({
        status__in: "",
      });
    });
    it("handles empty string values as icontains", () => {
      expect(transformFiltersToServer({ status: "" })).toEqual({
        status__icontains: "",
      });
    });
  });

  describe("transformValueFromServer", () => {
    it("returns null/undefined as-is", () => {
      expect(transformValueFromServer(null)).toBe(null);
      expect(transformValueFromServer(undefined)).toBe(undefined);
    });
    it("maps arrays", () => {
      expect(transformValueFromServer([1, 2])).toEqual([1, 2]);
    });
    it("converts boolean strings", () => {
      expect(transformValueFromServer("true")).toBe(true);
      expect(transformValueFromServer("false")).toBe(false);
    });
    it("converts dayjs strings", () => {
      const r = transformValueFromServer("2024-01-15");
      expect(r).toBeDefined();
      expect(r && typeof (r as any).format === "function").toBe(true);
    });
    it("converts datetime strings without timezone", () => {
      const r = transformValueFromServer("2024-01-15T12:00:00.123456");
      expect(r).toBeDefined();
      expect(r && typeof (r as any).isValid === "function").toBe(true);
    });
    it("converts time strings", () => {
      const r = transformValueFromServer("12:00:00");
      expect(r).toBeDefined();
      expect(r && typeof (r as any).isValid === "function").toBe(true);
      expect(r && (r as any).isValid()).toBe(true);
    });
    it("parses a date string into dayjs for a date widget", () => {
      const r = transformValueFromServer(
        "2024-01-15",
        EFieldWidgetType.DatePicker,
      );
      expect(dayjs.isDayjs(r)).toBe(true);
    });
    it("keeps a date-looking string as-is for a non-date widget", () => {
      expect(
        transformValueFromServer("2024-01-15", EFieldWidgetType.Input),
      ).toBe("2024-01-15");
      expect(transformValueFromServer("12:00:00", EFieldWidgetType.Input)).toBe(
        "12:00:00",
      );
    });
  });

  describe("transformDataFromServer", () => {
    it("transforms all values", () => {
      const r = transformDataFromServer({ d: "2024-01-15" });
      expect(r).toHaveProperty("d");
    });
    it("respects per-field widget types", () => {
      const r = transformDataFromServer(
        { at: "2024-01-15", code: "2024-01-15" },
        { at: EFieldWidgetType.DatePicker, code: EFieldWidgetType.Input },
      );
      expect(dayjs.isDayjs(r.at)).toBe(true);
      expect(r.code).toBe("2024-01-15");
    });
  });

  describe("getChangeWidgetTypes", () => {
    it("maps field names to their change widget type", () => {
      const map = getChangeWidgetTypes({
        fields: [
          {
            name: "at",
            change_configuration: {
              form_widget_type: EFieldWidgetType.DatePicker,
            },
          },
          { name: "code", change_configuration: {} },
        ],
      } as any);
      expect(map).toEqual({ at: EFieldWidgetType.DatePicker, code: undefined });
    });
    it("returns an empty map when configuration is missing", () => {
      expect(getChangeWidgetTypes()).toEqual({});
    });
  });

  describe("transformColumnValueFromServer", () => {
    it("returns emptyValue for null/undefined", () => {
      expect(transformColumnValueFromServer(null)).toBe("-");
      expect(transformColumnValueFromServer(undefined, "N/A")).toBe("N/A");
    });
    it("returns Tags for array", () => {
      const r = transformColumnValueFromServer(["a", "b"]);
      expect(Array.isArray(r)).toBe(true);
    });
    it("returns Checkbox for boolean", () => {
      const r = transformColumnValueFromServer(true);
      expect(r).toBeDefined();
    });
    it("formats dayjs with dateTimeFormat", () => {
      const r = transformColumnValueFromServer(
        "2024-01-15",
        undefined,
        "YYYY-MM-DD",
      );
      expect(r).toMatch(/^2024-01-15/);
    });
    it("keeps time-only strings unchanged", () => {
      expect(transformColumnValueFromServer("12:00:00")).toBe("12:00:00");
    });
    it("formats datetime values with dateTimeFormat", () => {
      const r = transformColumnValueFromServer(
        "2024-01-15T12:34:56",
        undefined,
        "YYYY-MM-DD HH:mm:ss",
      );
      expect(r).toBe("2024-01-15 12:34:56");
    });
    it("returns value as-is for other types", () => {
      expect(transformColumnValueFromServer("hello")).toBe("hello");
      expect(transformColumnValueFromServer(42)).toBe(42);
    });
  });
});
