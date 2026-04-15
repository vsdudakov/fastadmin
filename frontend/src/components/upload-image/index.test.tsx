import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { UploadImage } from "@/components/upload-image";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

const { mockFromFile } = vi.hoisted(() => ({
  mockFromFile: vi.fn(
    async (file: { name?: string }) => `base64-${file?.name || "file"}`,
  ),
}));

vi.mock("getbase64data", () => ({
  default: {
    fromFile: (file: { name?: string }) => mockFromFile(file),
  },
}));

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

vi.mock("antd-img-crop", () => ({
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="img-crop">{children}</div>
  ),
}));

vi.mock("@ant-design/icons", () => ({
  UploadOutlined: () => <span>icon</span>,
}));

vi.mock("antd", () => ({
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Image: ({ src }: { src?: string }) => (
    <img data-testid="preview-image" src={src} alt="Preview" />
  ),
  Modal: ({
    open,
    onCancel,
    children,
  }: {
    open: boolean;
    onCancel: () => void;
    children: React.ReactNode;
  }) => (
    <div>
      <div data-testid="modal-open">{String(open)}</div>
      <button type="button" onClick={onCancel}>
        close-preview
      </button>
      {children}
    </div>
  ),
  Upload: ({
    onChange,
    onPreview,
    defaultFileList,
    action,
  }: {
    onChange: (info: {
      fileList: Array<{ status?: string; response?: unknown; url?: string }>;
    }) => void;
    onPreview: (file: {
      url?: string;
      originFileObj?: { name: string };
    }) => void;
    defaultFileList?: Array<{ url: string }>;
    action?: string;
  }) => (
    <div>
      <div data-testid="upload-action">{action ?? "none"}</div>
      <div data-testid="default-file-list">
        {defaultFileList ? defaultFileList.map((f) => f.url).join(",") : "none"}
      </div>
      <button
        type="button"
        onClick={() =>
          onChange({
            fileList: [{ status: "done", response: "/uploaded-path" }],
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
              { status: "done", response: { url: "/uploaded-via-url" } },
            ],
          })
        }
      >
        trigger-upload-response-url
      </button>
      <button type="button" onClick={() => onChange({ fileList: [] })}>
        trigger-empty-upload
      </button>
      <button type="button" onClick={() => onPreview({ url: "/preview-url" })}>
        trigger-preview-url
      </button>
      <button
        type="button"
        onClick={() => onPreview({ originFileObj: { name: "preview-file" } })}
      >
        trigger-preview-file
      </button>
    </div>
  ),
}));

const renderWithConfig = (
  ui: React.ReactNode,
  disableCropImageInConfig = false,
) =>
  render(
    <ConfigurationContext.Provider
      value={
        {
          configuration: {
            site_name: "Admin",
            username_field: "username",
            models: [],
            dashboard_widgets: [],
            disable_crop_image: disableCropImageInConfig,
          },
        } as any
      }
    >
      {ui}
    </ConfigurationContext.Provider>,
  );

describe("UploadImage", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders defaultFileList from value and calls onChange on upload", async () => {
    const onChange = vi.fn();
    renderWithConfig(
      <UploadImage
        model="test"
        fieldName="image"
        onChange={onChange}
        value="/initial"
      />,
    );

    expect(screen.getByTestId("default-file-list").textContent).toBe(
      "/initial",
    );
    fireEvent.click(screen.getByText("trigger-upload"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith("/uploaded-path");
    });

    fireEvent.click(screen.getByText("trigger-empty-upload"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith(undefined);
    });
  });

  it("previews url and uploaded file", async () => {
    renderWithConfig(<UploadImage model="test" fieldName="image" />);

    expect(screen.getByTestId("modal-open").textContent).toBe("false");
    fireEvent.click(screen.getByText("trigger-preview-url"));
    expect(screen.getByTestId("modal-open").textContent).toBe("true");
    expect(screen.getByTestId("preview-image").getAttribute("src")).toBe(
      "/preview-url",
    );

    fireEvent.click(screen.getByText("close-preview"));
    expect(screen.getByTestId("modal-open").textContent).toBe("false");

    fireEvent.click(screen.getByText("trigger-preview-file"));
    await vi.waitFor(() => {
      expect(screen.getByTestId("preview-image").getAttribute("src")).toBe(
        "base64-preview-file",
      );
    });
  });

  it("toggles crop wrapper by configuration and prop", () => {
    const { rerender } = renderWithConfig(
      <UploadImage model="test" fieldName="image" disableCropImage={false} />,
      false,
    );
    expect(screen.queryByTestId("img-crop")).toBeTruthy();

    rerender(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
              disable_crop_image: true,
            },
          } as any
        }
      >
        <UploadImage model="test" fieldName="image" />
      </ConfigurationContext.Provider>,
    );
    expect(screen.queryByTestId("img-crop")).toBeNull();

    rerender(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
              disable_crop_image: false,
            },
          } as any
        }
      >
        <UploadImage model="test" fieldName="image" disableCropImage={true} />
      </ConfigurationContext.Provider>,
    );
    expect(screen.queryByTestId("img-crop")).toBeNull();
  });

  it("calls onChange with path from response.url object", async () => {
    const onChange = vi.fn();
    renderWithConfig(
      <UploadImage
        model="test"
        fieldName="image"
        onChange={onChange}
        value="/initial"
      />,
    );
    fireEvent.click(screen.getByText("trigger-upload-response-url"));
    await vi.waitFor(() => {
      expect(onChange).toHaveBeenCalledWith("/uploaded-via-url");
    });
  });

  it("renders defaultFileList with full url when value starts with http", () => {
    renderWithConfig(
      <UploadImage
        model="test"
        fieldName="image"
        value="https://example.com/photo.jpg"
      />,
    );
    expect(screen.getByTestId("default-file-list").textContent).toBe(
      "https://example.com/photo.jpg",
    );
  });

  it("handles upload when onChange is not provided", () => {
    renderWithConfig(<UploadImage model="test" fieldName="image" />);
    fireEvent.click(screen.getByText("trigger-upload"));
    fireEvent.click(screen.getByText("trigger-empty-upload"));
  });

  it("uses valueRepr for the display url in defaultFileList when provided", () => {
    renderWithConfig(
      <UploadImage
        model="test"
        fieldName="image"
        value="s3://bucket/photo.jpg"
        valueRepr="https://presigned.s3.amazonaws.com/photo.jpg?sig=abc"
      />,
    );
    expect(screen.getByTestId("default-file-list").textContent).toContain(
      "https://presigned.s3.amazonaws.com/photo.jpg?sig=abc",
    );
  });

  it("falls back to value for the display url when valueRepr is not provided", () => {
    renderWithConfig(
      <UploadImage model="test" fieldName="image" value="/media/photo.jpg" />,
    );
    expect(screen.getByTestId("default-file-list").textContent).toContain(
      "/media/photo.jpg",
    );
  });

  it("appends ?id= query param to action url when id is provided", () => {
    renderWithConfig(<UploadImage model="test" fieldName="image" id="42" />);
    expect(screen.getByTestId("upload-action").textContent).toContain("?id=42");
  });

  it("does not append id query param when id is not provided", () => {
    renderWithConfig(<UploadImage model="test" fieldName="image" />);
    expect(screen.getByTestId("upload-action").textContent).not.toContain(
      "?id=",
    );
  });
});
