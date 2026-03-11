import {
  BarsOutlined,
  LinkOutlined,
  LogoutOutlined,
  MoonOutlined,
  SearchOutlined,
  SettingOutlined,
  SunOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { useMutation } from "@tanstack/react-query";
import {
  Card,
  Col,
  Image,
  Input,
  Layout,
  Menu,
  Row,
  Skeleton,
  Space,
  Typography,
  theme,
} from "antd";
import type React from "react";
import { useContext, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router-dom";

import { buildListPath, ROUTES } from "@/constants/routes";
import { postFetcher } from "@/fetchers/fetchers";
import { getTitleFromModel } from "@/helpers/title";
import { useIsMobile } from "@/hooks/useIsMobile";
import { usePageMeta } from "@/hooks/usePageMeta";
import type { IModel } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { SignInUserContext } from "@/providers/SignInUserProvider";
import { ThemeContext } from "@/providers/ThemeProvider";

const { Header, Sider } = Layout;
const { Title } = Typography;

interface ICrudContainer {
  title: string;
  breadcrumbs?: React.ReactNode;
  viewOnSite?: string;
  headerActions?: React.ReactNode;
  bottomActions?: React.ReactNode;
  isLoading?: boolean;
  children: React.ReactNode;
}

export const CrudContainer: React.FC<ICrudContainer> = ({
  title,
  breadcrumbs,
  viewOnSite,
  headerActions,
  bottomActions,
  isLoading,
  children,
}) => {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const [search, setSearch] = useState<string | undefined>();
  const { model } = useParams();
  const { configuration } = useContext(ConfigurationContext);
  const { signedInUser, signedInUserRefetch, signedIn } =
    useContext(SignInUserContext);
  const { mode, setMode } = useContext(ThemeContext);
  const { t: _t } = useTranslation("CrudContainer");

  const {
    token: { colorBgContainer, colorPrimary },
  } = theme.useToken();

  useEffect(() => {
    if (!signedIn) {
      navigate(ROUTES.SIGN_IN);
    }
  }, [navigate, signedIn]);

  const { mutate: mutateSignOut } = useMutation({
    /* v8 ignore next -- covered via mutation integration */
    mutationFn: () => postFetcher("/sign-out", {}),
    onSuccess: () => {
      signedInUserRefetch();
    },
  });

  const onClickSideBarMenuItem = (item: any) => {
    switch (item.key) {
      case "dashboard":
        navigate(ROUTES.HOME);
        break;
      default:
        navigate(buildListPath(item.key));
        break;
    }
  };

  const toggleThemeMode = () => {
    setMode(mode === "dark" ? "light" : "dark");
  };

  const onClickRightMenuItem = (item: any) => {
    switch (item.key) {
      case "theme":
        toggleThemeMode();
        break;
      case "sign-out":
        mutateSignOut();
        break;
      case "user":
        navigate(ROUTES.HOME);
        break;
      default:
        break;
    }
  };

  const hasSections = configuration.models.some(
    (m: IModel) => m.menu_section && m.menu_section.trim().length > 0,
  );

  const filteredModels = useMemo(
    () =>
      configuration.models.filter(
        (m: IModel) =>
          !search ||
          m.name.toLocaleLowerCase().includes(search?.toLocaleLowerCase()),
      ),
    [configuration.models, search],
  );

  const currentModelConfig = configuration.models.find(
    (m: IModel) => m.name === model,
  );

  const currentSectionKey =
    hasSections && currentModelConfig
      ? `section-${
          currentModelConfig.menu_section || _t("Other") || _t("Other")
        }`
      : undefined;

  const autoOpenSectionKeys = useMemo(() => {
    if (!hasSections) {
      return [];
    }

    // If no search term, only expand the current section (if any)
    if (!search || !search.trim()) {
      return currentSectionKey ? [currentSectionKey] : [];
    }

    const sections = new Set<string>();

    filteredModels.forEach((m) => {
      const section = m.menu_section || _t("Other") || _t("Other");
      sections.add(`section-${section}`);
    });

    if (currentSectionKey) {
      sections.add(currentSectionKey);
    }

    return Array.from(sections);
  }, [filteredModels, hasSections, currentSectionKey, search, _t]);

  const items = [
    {
      key: "dashboard",
      label: _t("Dashboard"),
    },
    {
      key: "divider",
      type: "divider",
    },
    ...(hasSections
      ? Object.entries(
          filteredModels.reduce<Record<string, IModel[]>>(
            (acc, modelConfig) => {
              const section =
                modelConfig.menu_section || _t("Other") || _t("Other");
              if (!acc[section]) {
                acc[section] = [];
              }
              acc[section].push(modelConfig);
              return acc;
            },
            {},
          ),
        ).map(([section, models]) => ({
          key: `section-${section}`,
          label: section,
          children: (models as IModel[]).map((m: IModel) => ({
            key: m.name,
            label: getTitleFromModel(m),
          })),
        }))
      : filteredModels.map((m: IModel) => {
          return {
            key: m.name,
            label: getTitleFromModel(m),
          };
        })),
  ];

  const onSearch = (e: any) => setSearch(e.target.value);

  usePageMeta({
    title: `${configuration.site_name} | ${title}`,
    description: title,
  });

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          background: colorPrimary,
          paddingInline: isMobile ? 0 : 20,
          height: isMobile ? 48 : 56,
          lineHeight: isMobile ? "48px" : "56px",
          boxShadow: "0 1px 4px rgba(0, 0, 0, 0.08)",
        }}
      >
        <Row
          justify="space-between"
          align="middle"
          style={{
            paddingLeft: 0,
            paddingRight: 0,
          }}
          // wrap={false}
          // style={{
          //   gap: isMobile ? 8 : 0,
          //   flexDirection: isMobile ? "column" : "row",
          //   alignItems: isMobile ? "stretch" : "center",
          // }}
        >
          <Col>
            <Space size={isMobile ? 8 : 16}>
              {isMobile && (
                <Menu
                  style={{ background: "transparent", minWidth: 0 }}
                  theme="light"
                  mode="horizontal"
                  triggerSubMenuAction="click"
                  defaultSelectedKeys={[model || "dashboard"]}
                  items={[
                    {
                      key: signedInUser?.id || "key",
                      icon: (
                        <BarsOutlined
                          style={{
                            color: mode === "dark" ? "white" : colorBgContainer,
                          }}
                        />
                      ),
                      children: items as any,
                    },
                  ]}
                  onClick={onClickSideBarMenuItem}
                />
              )}

              <Link
                to={ROUTES.HOME}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  margin: 0,
                  lineHeight: 1,
                  verticalAlign: "middle",
                  marginLeft: isMobile ? -24 : 0,
                }}
              >
                <Image
                  src={`${window.SERVER_DOMAIN ?? ""}${configuration.site_header_logo ?? ""}`}
                  preview={false}
                  height={32}
                  alt={configuration.site_name}
                />
                <span
                  style={{
                    color: mode === "dark" ? "white" : colorBgContainer,
                    fontSize: 18,
                    fontWeight: 600,
                    letterSpacing: "-0.01em",
                  }}
                >
                  {configuration.site_name}
                </span>
              </Link>
            </Space>
          </Col>
          <Col>
            <Menu
              style={{
                background: "transparent",
                minWidth: 0,
                marginRight: isMobile ? -18 : -24,
                marginTop: isMobile ? -18 : 0,
                justifyContent: isMobile ? "flex-start" : "flex-end",
              }}
              theme="light"
              mode="horizontal"
              triggerSubMenuAction="click"
              items={[
                {
                  key: "user-menu",
                  icon: (
                    <SettingOutlined
                      style={{
                        color: mode === "dark" ? "white" : colorBgContainer,
                      }}
                    />
                  ),
                  children: [
                    {
                      key: "user",
                      icon: <UserOutlined />,
                      label: (signedInUser || ({} as any))[
                        configuration.username_field
                      ],
                    },
                    {
                      type: "divider",
                    },
                    {
                      key: "theme",
                      icon:
                        mode === "dark" ? <SunOutlined /> : <MoonOutlined />,
                      label:
                        mode === "dark" ? _t("Light mode") : _t("Dark mode"),
                    },
                    {
                      type: "divider",
                    },
                    {
                      key: "sign-out",
                      icon: <LogoutOutlined />,
                      label: _t("Sign Out"),
                    },
                  ],
                },
              ]}
              onClick={onClickRightMenuItem}
            />
          </Col>
        </Row>
      </Header>
      <Layout>
        {!isMobile && (
          <Sider
            width={260}
            style={{
              background: colorBgContainer,
              borderRadius: 0,
              boxShadow: "1px 0 0 rgba(0, 0, 0, 0.06)",
            }}
          >
            <div style={{ padding: 16 }}>
              <Input
                value={search}
                onChange={onSearch}
                placeholder={_t("Search By Menu") as string}
                prefix={
                  <SearchOutlined style={{ color: "rgba(0,0,0,0.25)" }} />
                }
                allowClear
                style={{ borderRadius: 6 }}
              />
            </div>
            <Menu
              key={search ? `menu-search-${search}` : "menu-default"}
              mode="inline"
              theme="light"
              defaultSelectedKeys={[model || "dashboard"]}
              defaultOpenKeys={autoOpenSectionKeys}
              style={{
                borderRight: 0,
                padding: "0 12px 24px",
                height: "calc(100vh - 56px - 72px)",
                overflowY: "auto",
              }}
              items={items as any}
              onClick={onClickSideBarMenuItem}
            />
          </Sider>
        )}
        <Layout
          style={{
            padding: isMobile ? 8 : 24,
            minHeight: "calc(100vh - 56px)",
          }}
        >
          <Row
            justify="space-between"
            align="middle"
            style={{ marginBottom: isMobile ? 8 : 16 }}
          >
            <Col>{breadcrumbs}</Col>
            {viewOnSite && (
              <Col>
                <a
                  href={viewOnSite}
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: 14 }}
                >
                  <LinkOutlined /> {_t("View on site")}
                </a>
              </Col>
            )}
          </Row>
          <Card
            title={
              <Row justify="space-between" align="middle">
                <Col>
                  <Title style={{ margin: 0 }} level={5}>
                    {title}
                  </Title>
                </Col>
                {headerActions ? <Col>{headerActions}</Col> : null}
              </Row>
            }
            style={{
              marginTop: isMobile ? 4 : 0,
              borderRadius: isMobile ? 6 : 8,
              boxShadow: isMobile
                ? "0 1px 3px rgba(0, 0, 0, 0.05)"
                : "0 1px 4px rgba(0, 0, 0, 0.06)",
            }}
          >
            <Skeleton loading={isLoading} active={true}>
              {children}
              {bottomActions ? (
                <Row>
                  <Col>{bottomActions}</Col>
                </Row>
              ) : null}
            </Skeleton>
          </Card>
        </Layout>
      </Layout>
    </Layout>
  );
};
