import { cleanup, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { EFieldWidgetType } from "@/interfaces/configuration";
import { FormContainer } from "./index";

const { mockGetWidgetCls, mockSetFieldsValue } = vi.hoisted(() => ({
  mockGetWidgetCls: vi.fn(),
  mockSetFieldsValue: vi.fn(),
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

vi.mock("antd", () => ({
  Form: Object.assign(
    ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    {
      Item: ({
        children,
        name,
        valuePropName,
      }: {
        children: React.ReactNode;
        name?: string;
        valuePropName?: string;
      }) => (
        <div data-testid={name ? `item-${name}` : "item-without-name"}>
          <span>{name || "no-name"}</span>
          <span>{valuePropName || "no-value-prop"}</span>
          {children}
        </div>
      ),
    },
  ),
  Collapse: ({
    activeKey,
    items,
  }: {
    activeKey: string[];
    items: Array<{
      key: string;
      label: React.ReactNode;
      children: React.ReactNode;
    }>;
  }) => (
    <div>
      <div data-testid="collapse-active">{JSON.stringify(activeKey)}</div>
      {items.map((item) => (
        <div key={item.key} data-testid={`collapse-${item.key}`}>
          <div>{item.label}</div>
          {item.children}
        </div>
      ))}
    </div>
  ),
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Divider: () => <hr />,
  Typography: {
    Text: ({ children }: { children: React.ReactNode }) => (
      <span>{children}</span>
    ),
  },
}));

vi.mock("@/helpers/widgets", () => ({
  getWidgetCls: (...args: unknown[]) => mockGetWidgetCls(...args),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromFieldName: (name: string) => `title-${name}`,
  getTitleFromModel: (model: { name: string }) => `model-${model.name}`,
}));

vi.mock("@/helpers/transform", () => ({
  isJson: () => true,
  isSlug: () => true,
}));

vi.mock("@/components/inline-widget", () => ({
  InlineWidget: ({ parentId }: { parentId: string }) => (
    <div data-testid="inline-widget">{parentId}</div>
  ),
}));

describe("FormContainer", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("expands all fieldsets on operation error and sorts fields by fieldset order", () => {
    mockGetWidgetCls.mockReturnValue([
      ({ value }: { value?: string }) => <input value={value || ""} readOnly />,
      {},
    ]);

    const form = { setFieldsValue: mockSetFieldsValue };
    const modelConfiguration: any = {
      name: "test",
      permissions: [],
      actions: [],
      fields: [
        {
          name: "a",
          add_configuration: { form_widget_type: EFieldWidgetType.Input },
        },
        {
          name: "b",
          add_configuration: { form_widget_type: EFieldWidgetType.Input },
        },
      ],
      fieldsets: [
        ["Collapsed", { fields: ["a", "b"], classes: ["collapse"] }],
        ["Open", { fields: ["b", "a"], classes: [] }],
      ],
    };

    const { rerender } = render(
      <FormContainer
        modelConfiguration={modelConfiguration}
        form={form}
        onFinish={() => undefined}
        mode="add"
        hasOperationError={false}
      >
        <div>actions</div>
      </FormContainer>,
    );

    const activeBeforeError = JSON.parse(
      screen.getByTestId("collapse-active").textContent || "[]",
    ) as string[];
    expect(activeBeforeError).toContain(JSON.stringify(["b", "a"]));
    expect(screen.getByTestId('collapse-["b","a"]')).toBeTruthy();
    const openFieldsetItems = screen.getByTestId('collapse-["b","a"]');
    expect(openFieldsetItems.textContent).toContain("b");
    expect(openFieldsetItems.textContent).toContain("a");
    expect(openFieldsetItems.textContent?.indexOf("b")).toBeLessThan(
      openFieldsetItems.textContent?.indexOf("a") || 0,
    );

    rerender(
      <FormContainer
        modelConfiguration={modelConfiguration}
        form={form}
        onFinish={() => undefined}
        mode="add"
        hasOperationError={true}
      >
        <div>actions</div>
      </FormContainer>,
    );

    const activeAfterError = JSON.parse(
      screen.getByTestId("collapse-active").textContent || "[]",
    ) as string[];
    expect(activeAfterError).toContain(JSON.stringify(["a", "b"]));
    expect(activeAfterError).toContain(JSON.stringify(["b", "a"]));
  });

  it("sorts non-fieldset fields by index and renders inline widgets with id", () => {
    mockGetWidgetCls.mockReturnValue([() => <input readOnly />, {}]);

    const form = { setFieldsValue: mockSetFieldsValue };
    render(
      <FormContainer
        modelConfiguration={
          {
            name: "test",
            permissions: [],
            actions: [],
            fields: [
              {
                name: "late",
                change_configuration: {
                  index: 2,
                  form_widget_type: EFieldWidgetType.Input,
                },
              },
              {
                name: "early",
                change_configuration: {
                  index: 1,
                  form_widget_type: EFieldWidgetType.Checkbox,
                },
              },
            ],
            inlines: [{ name: "inlineOne" }],
          } as any
        }
        id="55"
        form={form}
        onFinish={() => undefined}
        mode="change"
        initialValues={{ early: true }}
      >
        <div>actions</div>
      </FormContainer>,
    );

    const allItems = screen
      .getAllByTestId(/item-/)
      .map((x) => x.getAttribute("data-testid"));
    expect(allItems[0]).toBe("item-early");
    expect(allItems[1]).toBe("item-late");
    expect(screen.getByTestId("item-early").textContent).toContain("checked");
    expect(screen.getByTestId("inline-widget").textContent).toBe("55");
    expect(mockSetFieldsValue).toHaveBeenCalledWith({ early: true });
  });

  it("does not render inline widgets when id is missing", () => {
    mockGetWidgetCls.mockReturnValue([() => <input readOnly />, {}]);

    render(
      <FormContainer
        modelConfiguration={
          {
            name: "test",
            permissions: [],
            actions: [],
            fields: [],
            inlines: [{ name: "inlineOne" }],
          } as any
        }
        form={{ setFieldsValue: mockSetFieldsValue }}
        onFinish={() => undefined}
        mode="change"
      >
        <div>actions</div>
      </FormContainer>,
    );

    expect(screen.queryByTestId("inline-widget")).toBeNull();
  });
});
