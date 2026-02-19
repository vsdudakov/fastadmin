import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ROUTES } from "@/constants/routes";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { SignInUserContext } from "@/providers/SignInUserProvider";
import { CrudContainer } from "./index";

const {
  mockNavigate,
  mockUseMutation,
  mockMutateSignOut,
  mockSignedInUserRefetch,
  mockUseIsMobile,
  menuPropsRef,
} = vi.hoisted(() => ({
  mockNavigate: vi.fn(),
  mockUseMutation: vi.fn(),
  mockMutateSignOut: vi.fn(),
  mockSignedInUserRefetch: vi.fn(),
  mockUseIsMobile: vi.fn(),
  menuPropsRef: { current: [] as any[] },
}));

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => mockUseMutation(options),
}));

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom",
    );
  return {
    ...actual,
    Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
      <a href={to}>{children}</a>
    ),
    useNavigate: () => mockNavigate,
    useParams: () => ({ model: "users" }),
  };
});

vi.mock("react-helmet-async", () => ({
  Helmet: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("@/hooks/useIsMobile", () => ({
  useIsMobile: () => mockUseIsMobile(),
}));

vi.mock("@/fetchers/fetchers", () => ({
  postFetcher: vi.fn(),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromModel: (m: { name: string }) => m.name.toUpperCase(),
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
  theme: {
    useToken: () => ({
      token: { colorBgContainer: "#fff", colorPrimary: "#000" },
    }),
  },
  Layout: Object.assign(
    ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    {
      Header: ({ children }: { children: React.ReactNode }) => (
        <header>{children}</header>
      ),
      Sider: ({ children }: { children: React.ReactNode }) => (
        <aside>{children}</aside>
      ),
    },
  ),
  Typography: {
    Title: ({ children }: { children: React.ReactNode }) => <h5>{children}</h5>,
  },
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Image: ({ alt }: { alt: string }) => <img alt={alt} />,
  Input: ({
    onChange,
    value,
  }: {
    onChange?: (e: { target: { value: string } }) => void;
    value?: string;
  }) => (
    <div>
      <span>{value || ""}</span>
      <button
        type="button"
        onClick={() => onChange?.({ target: { value: "use" } })}
      >
        trigger-search-menu
      </button>
    </div>
  ),
  Menu: (props: any) => {
    menuPropsRef.current.push(props);
    return (
      <div>
        {(props.items || []).map((item: any) => (
          <div key={item.key}>
            <button
              type="button"
              onClick={() => props.onClick?.({ key: item.key })}
            >
              menu-{item.key}
            </button>
            {(item.children || []).map((child: any) => (
              <button
                key={child.key}
                type="button"
                onClick={() => props.onClick?.({ key: child.key })}
              >
                menu-{child.key}
              </button>
            ))}
          </div>
        ))}
      </div>
    );
  },
  Card: ({
    title,
    children,
  }: {
    title: React.ReactNode;
    children: React.ReactNode;
  }) => (
    <div>
      <div>{title}</div>
      {children}
    </div>
  ),
  Skeleton: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

const configurationValue: any = {
  configuration: {
    site_name: "FastAdmin",
    site_header_logo: "/logo.png",
    username_field: "username",
    models: [
      { name: "users", permissions: [], actions: [], fields: [] },
      { name: "posts", permissions: [], actions: [], fields: [] },
    ],
    dashboard_widgets: [],
  },
};

const renderCrud = (signedIn: boolean, isMobile: boolean) => {
  mockUseIsMobile.mockReturnValue(isMobile);
  return render(
    <ConfigurationContext.Provider value={configurationValue}>
      <SignInUserContext.Provider
        value={
          {
            signedIn,
            signedInUser: { id: "1", username: "bob" },
            signedInUserRefetch: mockSignedInUserRefetch,
          } as any
        }
      >
        <CrudContainer
          title="Users"
          viewOnSite="https://example.com"
          headerActions={<div>header-actions</div>}
          bottomActions={<div>bottom-actions</div>}
        >
          <div>content</div>
        </CrudContainer>
      </SignInUserContext.Provider>
    </ConfigurationContext.Provider>,
  );
};

describe("CrudContainer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    menuPropsRef.current = [];
    mockUseMutation.mockReturnValue({ mutate: mockMutateSignOut });
  });

  afterEach(() => {
    cleanup();
  });

  it("handles sidebar, right menu actions and search filtering on desktop", () => {
    renderCrud(true, false);

    fireEvent.click(screen.getByRole("button", { name: "menu-dashboard" }));
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.HOME);

    fireEvent.click(screen.getByRole("button", { name: "menu-users" }));
    expect(mockNavigate).toHaveBeenCalledWith("/list/users");

    fireEvent.click(screen.getByRole("button", { name: "menu-sign-out" }));
    expect(mockMutateSignOut).toHaveBeenCalled();

    const mutationOptions = mockUseMutation.mock.calls[0][0] as any;
    mutationOptions.onSuccess();
    expect(mockSignedInUserRefetch).toHaveBeenCalled();

    fireEvent.click(
      screen.getByRole("button", { name: "trigger-search-menu" }),
    );
    expect(screen.queryByRole("button", { name: "menu-posts" })).toBeNull();
    expect(screen.getByText("header-actions")).toBeTruthy();
    expect(screen.getByText("bottom-actions")).toBeTruthy();
    expect(screen.getByText("View on site")).toBeTruthy();
  });

  it("redirects to sign-in when user is not signed in", () => {
    renderCrud(false, false);
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.SIGN_IN);
  });

  it("covers mobile menu and default menu branches", () => {
    renderCrud(true, true);
    const menus = menuPropsRef.current;
    expect(menus.length).toBeGreaterThan(0);
    menus[0].onClick({ key: "users" });
    expect(mockNavigate).toHaveBeenCalledWith("/list/users");
    menus[menus.length - 1].onClick({ key: "unknown" });
    expect(mockMutateSignOut).toHaveBeenCalledTimes(0);
  });
});
