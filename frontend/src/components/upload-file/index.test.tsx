import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { UploadFile } from "@/components/upload-file";

vi.mock("react-i18next", async () => {
  const actual =
    await vi.importActual<typeof import("react-i18next")>("react-i18next");
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string) => key,
      i18n: { changeLanguage: vi.fn() },
    }),
  };
});

vi.mock("@ant-design/icons", () => ({
  UploadOutlined: () => <span>icon</span>,
}));

vi.mock("antd", () => ({
  Button: ({ children }: { children: React.ReactNode }) => (
    <button type="button">{children}</button>
  ),
  Upload: ({
    onChange,
    defaultFileList,
    action,
  }: {
    onChange: (info: {
      fileList: Array<{ status?: string; response?: unknown; url?: string }>;
    }) => void;
    defaultFileList?: Array<{ url?: string; name?: string }>;
    action?: string;
  }) => (
    <div>
      <div data-testid="upload-action">{action ?? "none"}</div>
      <div data-testid="default-file-list">
        {defaultFileList
          ? defaultFileList.map((f) => f.url ?? "").join(",")
          : "none"}
      </div>
      <button
        type="button"
        onClick={() =>
          onChange({
            fileList: [{ status: "done", response: "/uploaded-file-path" }],
          })
        }
      >
        trigger-upload
      </button>
      <button
        type="button"
        onClick={() =>
          onChange({
            fileList: [
              { status: "done", response: { url: "/from-response-url" } },
            ],
          })
        }
      >
        trigger-upload-response-url
      </button>
      <button
        type="button"
        onClick={() =>
          onChange({
            fileList: [{ status: "done", url: "/fallback-url" }],
          })
        }
      >
        trigger-upload-fallback-url
      </button>
      <button type="button" onClick={() => onChange({ fileList: [] })}>
        trigger-empty-upload
      </button>
    </div>
  ),
}));

describe("UploadFile", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders defaultFileList from value", () => {
    render(
      <UploadFile model="test" fieldName="file" value="/existing/file.pdf" />,
    );
    expect(screen.getByTestId("default-file-list").textContent).toContain(
      "/existing/file.pdf",
    );
  });

  it("renders empty list when value is undefined", () => {
    render(<UploadFile model="test" fieldName="file" />);
    expect(screen.getByTestId("default-file-list").textContent).toBe("none");
  });

  it("calls onChange with path when upload succeeds", async () => {
    const onChange = vi.fn();
    render(
      <UploadFile
        model="test"
        fieldName="file"
        value="/initial"
        onChange={onChange}
      />,
    );

    fireEvent.click(screen.getByText("trigger-upload"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith("/uploaded-file-path");
    });
  });

  it("calls onChange with undefined when fileList is empty", async () => {
    const onChange = vi.fn();
    render(
      <UploadFile
        model="test"
        fieldName="file"
        value="/initial"
        onChange={onChange}
      />,
    );

    fireEvent.click(screen.getByText("trigger-empty-upload"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith(undefined);
    });
  });

  it("calls onChange with path from response.url object", async () => {
    const onChange = vi.fn();
    render(
      <UploadFile
        model="test"
        fieldName="file"
        value="/initial"
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByText("trigger-upload-response-url"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith("/from-response-url");
    });
  });

  it("calls onChange with path from file.url when response has no path", async () => {
    const onChange = vi.fn();
    render(
      <UploadFile
        model="test"
        fieldName="file"
        value="/initial"
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByText("trigger-upload-fallback-url"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith("/fallback-url");
    });
  });

  it("does not throw when onChange is not provided", () => {
    render(<UploadFile model="test" fieldName="file" />);
    fireEvent.click(screen.getByText("trigger-upload"));
    fireEvent.click(screen.getByText("trigger-empty-upload"));
  });

  it("appends ?id= query param to action url when id is provided", () => {
    render(<UploadFile model="test" fieldName="file" id="42" />);
    expect(screen.getByTestId("upload-action").textContent).toContain(
      "/upload-file/test/file?id=42",
    );
  });

  it("does not append id query param when id is not provided", () => {
    render(<UploadFile model="test" fieldName="file" />);
    expect(screen.getByTestId("upload-action").textContent).not.toContain(
      "?id=",
    );
  });

  it("uses valueRepr for the display url in defaultFileList when provided", () => {
    render(
      <UploadFile
        model="test"
        fieldName="file"
        value="s3://bucket/key.pdf"
        valueRepr="https://presigned.s3.amazonaws.com/key.pdf?sig=abc"
      />,
    );
    expect(screen.getByTestId("default-file-list").textContent).toContain(
      "https://presigned.s3.amazonaws.com/key.pdf?sig=abc",
    );
    expect(screen.getByTestId("default-file-list").textContent).not.toContain(
      "s3://bucket/key.pdf",
    );
  });

  it("falls back to value for the display url when valueRepr is not provided", () => {
    render(
      <UploadFile model="test" fieldName="file" value="/media/file.pdf" />,
    );
    expect(screen.getByTestId("default-file-list").textContent).toContain(
      "/media/file.pdf",
    );
  });
});
