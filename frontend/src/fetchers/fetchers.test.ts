import { beforeEach, describe, expect, it, vi } from "vitest";

const mockGet = vi.fn();
const mockPost = vi.fn();
const mockPatch = vi.fn();
const mockDelete = vi.fn();

vi.mock("axios", () => ({
  default: {
    create: () => ({
      get: mockGet,
      post: mockPost,
      patch: mockPatch,
      delete: mockDelete,
    }),
  },
}));

describe("fetchers", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    mockGet.mockResolvedValue({ data: { ok: true } });
    mockPost.mockResolvedValue({ data: { created: true } });
    mockPatch.mockResolvedValue({ data: { updated: true } });
    mockDelete.mockResolvedValue(undefined);
  });

  it("getFetcher returns data", async () => {
    const { getFetcher } = await import("./fetchers");
    const data = await getFetcher("/api/me");
    expect(mockGet).toHaveBeenCalledWith("/api/me");
    expect(data).toEqual({ ok: true });
  });

  it("postFetcher sends payload and returns data", async () => {
    const { postFetcher } = await import("./fetchers");
    const data = await postFetcher("/api/add/Event", { name: "Test" });
    expect(mockPost).toHaveBeenCalledWith("/api/add/Event", { name: "Test" });
    expect(data).toEqual({ created: true });
  });

  it("patchFetcher sends payload and returns data", async () => {
    const { patchFetcher } = await import("./fetchers");
    const data = await patchFetcher("/api/change/Event/1", { name: "New" });
    expect(mockPatch).toHaveBeenCalledWith("/api/change/Event/1", {
      name: "New",
    });
    expect(data).toEqual({ updated: true });
  });

  it("deleteFetcher calls delete", async () => {
    const { deleteFetcher } = await import("./fetchers");
    await deleteFetcher("/api/delete/Event/1");
    expect(mockDelete).toHaveBeenCalledWith("/api/delete/Event/1");
  });
});
