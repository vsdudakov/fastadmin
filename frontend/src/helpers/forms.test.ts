import { beforeEach, describe, expect, it, vi } from "vitest";
import { cleanFormErrors, handleError } from "./forms";

const messageError = vi.fn();
vi.mock("antd", () => ({
  message: { error: (...args: any[]) => messageError(...args) },
}));

describe("handleError", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows string detail from response", () => {
    handleError({ response: { data: { detail: "Bad request" } } });
    expect(messageError).toHaveBeenCalledWith("Bad request");
  });

  it("shows description when detail is missing", () => {
    handleError({ response: { data: { description: "Error desc" } } });
    expect(messageError).toHaveBeenCalledWith("Error desc");
  });

  it("shows Server error when detail is not string", () => {
    handleError({ response: { data: { detail: { foo: 1 } } } });
    expect(messageError).toHaveBeenCalledWith("Server error");
  });

  it("sets fields when detail is array and form provided", () => {
    const setFields = vi.fn();
    const getFieldsValue = vi.fn().mockReturnValue({ name: "", email: "x" });
    const form = { setFields, getFieldsValue } as any;
    handleError(
      {
        response: {
          data: {
            detail: [
              { loc: ["body", "name"], msg: "Required" },
              { loc: ["body", "email"], msg: "Invalid" },
            ],
          },
        },
      },
      form,
    );
    expect(setFields).toHaveBeenCalledWith([
      { name: "name", errors: ["Required"] },
      { name: "email", errors: ["Invalid"] },
    ]);
  });

  it("skips items without loc or msg", () => {
    const setFields = vi.fn();
    const getFieldsValue = vi.fn().mockReturnValue({ a: 1 });
    const form = { setFields, getFieldsValue } as any;
    handleError(
      {
        response: {
          data: {
            detail: [
              { loc: ["body", "a"], msg: "Error" },
              { loc: [], msg: "No field" },
              { msg: "No loc" },
            ],
          },
        },
      },
      form,
    );
    expect(setFields).toHaveBeenCalledWith([{ name: "a", errors: ["Error"] }]);
  });

  it("does not set fields when form has no matching field keys", () => {
    const setFields = vi.fn();
    const getFieldsValue = vi.fn().mockReturnValue({ other: 1 });
    const form = { setFields, getFieldsValue } as any;
    handleError(
      {
        response: {
          data: {
            detail: [{ loc: ["body", "name"], msg: "Required" }],
          },
        },
      },
      form,
    );
    expect(setFields).not.toHaveBeenCalled();
  });

  it("does not set fields when errorsFields is empty", () => {
    const setFields = vi.fn();
    const getFieldsValue = vi.fn().mockReturnValue({});
    const form = { setFields, getFieldsValue } as any;
    handleError(
      {
        response: {
          data: {
            detail: [{ loc: ["body", "name"], msg: "Required" }],
          },
        },
      },
      form,
    );
    expect(setFields).not.toHaveBeenCalled();
  });

  it("shows Server error when detail is array but form is not provided", () => {
    handleError({
      response: {
        data: {
          detail: [{ loc: ["body", "name"], msg: "Required" }],
        },
      },
    });
    expect(messageError).toHaveBeenCalledWith("Server error");
  });
});

describe("cleanFormErrors", () => {
  it("clears errors for all form fields", () => {
    const setFields = vi.fn();
    const getFieldsValue = vi.fn().mockReturnValue({ a: 1, b: 2 });
    const form = { setFields, getFieldsValue } as any;
    cleanFormErrors(form);
    expect(setFields).toHaveBeenCalledWith([
      { name: "a", errors: [] },
      { name: "b", errors: [] },
    ]);
  });
});
