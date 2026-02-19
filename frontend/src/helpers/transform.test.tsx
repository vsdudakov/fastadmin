import { describe, expect, it } from "vitest";
import {
  isArray,
  isBoolean,
  isDayJs,
  isJson,
  isNumeric,
  isSlug,
  isString,
  transformColumnValueFromServer,
  transformDataFromServer,
  transformDataToServer,
  transformFiltersToServer,
  transformValueFromServer,
  transformValueToServer,
} from "./transform";

describe("transform", () => {
  describe("isDayJs", () => {
    it("returns true for ISO date strings", () => {
      expect(isDayJs("2024-01-15")).toBe(true);
      expect(isDayJs("2024-01-15T12:00:00Z")).toBe(true);
    });
    it("returns false for non-dates", () => {
      expect(isDayJs("hello")).toBe(false);
      expect(isDayJs("12")).toBe(false);
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
    it("formats dayjs-like value", () => {
      const d = { date: true, format: () => "2024-01-15" };
      expect(transformValueToServer(d)).toBe("2024-01-15");
    });
    it("returns non-dayjs value as-is", () => {
      expect(transformValueToServer({ a: 1 })).toEqual({ a: 1 });
      expect(transformValueToServer("hello")).toBe("hello");
    });
  });

  describe("transformDataToServer", () => {
    it("transforms all values", () => {
      const d = {
        date: { date: true, format: () => "2024-01-15" },
      };
      expect(transformDataToServer(d)).toEqual({ date: "2024-01-15" });
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
  });

  describe("transformDataFromServer", () => {
    it("transforms all values", () => {
      const r = transformDataFromServer({ d: "2024-01-15" });
      expect(r).toHaveProperty("d");
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
    it("returns value as-is for other types", () => {
      expect(transformColumnValueFromServer("hello")).toBe("hello");
      expect(transformColumnValueFromServer(42)).toBe(42);
    });
  });
});
