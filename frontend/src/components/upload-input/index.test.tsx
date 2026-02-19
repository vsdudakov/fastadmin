import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { UploadInput } from "@/components/upload-input";
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
    beforeUpload,
    defaultFileList,
  }: {
    onChange: (info: unknown) => void;
    onPreview: (file: unknown) => void;
    beforeUpload: () => boolean;
    defaultFileList?: Array<{ url: string }>;
  }) => (
    <div>
      <div data-testid="default-file-list">
        {defaultFileList ? defaultFileList.map((f) => f.url).join(",") : "none"}
      </div>
      <button
        type="button"
        onClick={() =>
          onChange({
            fileList: [
              { originFileObj: { name: "new-file" } },
              { url: "/existing-file" },
            ],
          })
        }
      >
        trigger-upload
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
      <button type="button" onClick={() => beforeUpload()}>
        trigger-before-upload
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

describe("UploadInput", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("handles upload changes for single and multiple modes", async () => {
    const onSingleChange = vi.fn();
    const onMultipleChange = vi.fn();

    const { rerender } = renderWithConfig(
      <UploadInput
        parentId="single"
        onChange={onSingleChange}
        value="/initial"
      />,
    );

    expect(screen.getByTestId("default-file-list").textContent).toBe(
      "/initial",
    );
    fireEvent.click(screen.getByText("trigger-upload"));
    await vi.waitFor(() => {
      expect(onSingleChange).toHaveBeenCalledWith("/existing-file");
    });
    fireEvent.click(screen.getByText("trigger-before-upload"));

    fireEvent.click(screen.getByText("trigger-empty-upload"));
    await vi.waitFor(() => {
      expect(onSingleChange).toHaveBeenCalledWith(null);
    });

    rerender(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
            },
          } as any
        }
      >
        <UploadInput
          parentId="multiple"
          multiple={true}
          onChange={onMultipleChange}
          value={["/v1", "/v2"]}
        />
      </ConfigurationContext.Provider>,
    );

    expect(screen.getByTestId("default-file-list").textContent).toBe("/v1,/v2");
    fireEvent.click(screen.getByText("trigger-upload"));
    await vi.waitFor(() => {
      expect(onMultipleChange).toHaveBeenCalledWith([
        "base64-new-file",
        "/existing-file",
      ]);
    });
  });

  it("previews url and uploaded file", async () => {
    renderWithConfig(<UploadInput parentId="preview" />);

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
      <UploadInput parentId="crop-on" disableCropImage={false} />,
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
        <UploadInput parentId="crop-off-by-config" />
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
        <UploadInput parentId="crop-off-by-prop" disableCropImage={true} />
      </ConfigurationContext.Provider>,
    );
    expect(screen.queryByTestId("img-crop")).toBeNull();
  });

  it("handles upload when onChange is not provided", async () => {
    const { rerender } = renderWithConfig(
      <UploadInput parentId="no-change-single" />,
    );

    fireEvent.click(screen.getByText("trigger-upload"));
    fireEvent.click(screen.getByText("trigger-empty-upload"));

    rerender(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
            },
          } as any
        }
      >
        <UploadInput parentId="no-change-multiple" multiple={true} />
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(screen.getByText("trigger-upload"));
    await vi.waitFor(() => {
      expect(mockFromFile).toHaveBeenCalled();
    });
  });
});
