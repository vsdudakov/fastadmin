import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useIsMobile } from "./useIsMobile";

describe("useIsMobile", () => {
  it("returns true when width <= 768", () => {
    vi.stubGlobal("innerWidth", 768);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(true);
    vi.unstubAllGlobals();
  });

  it("returns false when width > 768", () => {
    vi.stubGlobal("innerWidth", 1024);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
    vi.unstubAllGlobals();
  });

  it("updates when window is resized", () => {
    let resizeHandler: () => void = () => {};
    const addSpy = vi
      .spyOn(window, "addEventListener")
      .mockImplementation((event, handler) => {
        if (event === "resize") resizeHandler = handler as () => void;
      });
    const removeSpy = vi
      .spyOn(window, "removeEventListener")
      .mockImplementation(() => {});
    Object.defineProperty(window, "innerWidth", {
      value: 1024,
      writable: true,
    });
    const { result, rerender, unmount } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
    (window as any).innerWidth = 500;
    resizeHandler();
    rerender();
    expect(result.current).toBe(true);
    unmount();
    expect(removeSpy).toHaveBeenCalledWith("resize", resizeHandler);
    addSpy.mockRestore();
    removeSpy.mockRestore();
  });
});
