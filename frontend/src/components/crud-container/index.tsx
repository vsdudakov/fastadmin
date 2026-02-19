import {
  BarsOutlined,
  LinkOutlined,
  SearchOutlined,
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
import { useContext, useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router-dom";

import { buildListPath, ROUTES } from "@/constants/routes";
import { postFetcher } from "@/fetchers/fetchers";
import { getTitleFromModel } from "@/helpers/title";
import { useIsMobile } from "@/hooks/useIsMobile";
import type { IModel } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { SignInUserContext } from "@/providers/SignInUserProvider";

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

  const onClickRightMenuItem = (item: any) => {
    switch (item.key) {
      case "sign-out":
        mutateSignOut();
        break;
      default:
        break;
    }
  };

  const items = [
    {
      key: "dashboard",
      label: _t("Dashboard"),
    },
    {
      key: "divider",
      type: "divider",
    },
    ...configuration.models
      .filter(
        (m: IModel) =>
          !search ||
          m.name.toLocaleLowerCase().includes(search?.toLocaleLowerCase()),
      )
      .map((m: IModel) => {
        return {
          key: m.name,
          label: getTitleFromModel(m),
        };
      }),
  ];

  const onSearch = (e: any) => setSearch(e.target.value);

  return (
    <>
      <Helmet defaultTitle={title}>
        <meta name="description" content={title} />
      </Helmet>
      <Layout style={{ minHeight: "100vh" }}>
        <Header
          style={{
            background: colorPrimary,
            paddingInline: 24,
            height: 56,
            lineHeight: "56px",
            boxShadow: "0 1px 4px rgba(0, 0, 0, 0.08)",
          }}
        >
          <Row justify="space-between" align="middle">
            <Col>
              <Space size="middle">
                {isMobile && (
                  <Menu
                    style={{ background: "transparent", minWidth: 0 }}
                    theme="light"
                    mode="horizontal"
                    defaultSelectedKeys={[model || "dashboard"]}
                    items={[
                      {
                        key: signedInUser?.id || "key",
                        icon: (
                          <BarsOutlined style={{ color: colorBgContainer }} />
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
                  }}
                >
                  <Image
                    src={`${window.SERVER_DOMAIN ?? ""}${configuration.site_header_logo ?? ""}`}
                    preview={false}
                    height={32}
                    alt={configuration.site_name}
                  />
                  {!isMobile && (
                    <span
                      style={{
                        color: colorBgContainer,
                        fontSize: 18,
                        fontWeight: 600,
                        letterSpacing: "-0.01em",
                      }}
                    >
                      {configuration.site_name}
                    </span>
                  )}
                </Link>
              </Space>
            </Col>
            <Col>
              <Space size="middle">
                {!isMobile && (
                  <span
                    style={{
                      color: "rgba(255, 255, 255, 0.9)",
                      fontSize: 14,
                    }}
                  >
                    {
                      (signedInUser || ({} as any))[
                        configuration.username_field
                      ]
                    }
                  </span>
                )}

                <Menu
                  style={{ background: "transparent", minWidth: 0 }}
                  theme="light"
                  mode="horizontal"
                  items={[
                    {
                      key: signedInUser?.id || "key",
                      icon: (
                        <UserOutlined style={{ color: colorBgContainer }} />
                      ),
                      children: [
                        {
                          key: "sign-out",
                          label: _t("Sign Out"),
                        },
                      ],
                    },
                  ]}
                  onClick={onClickRightMenuItem}
                />
              </Space>
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
                mode="inline"
                theme="light"
                defaultSelectedKeys={[model || "dashboard"]}
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
          <Layout style={{ padding: 24, minHeight: "calc(100vh - 56px)" }}>
            <Row
              justify="space-between"
              align="middle"
              style={{ marginBottom: 16 }}
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
                marginTop: 0,
                borderRadius: 8,
                boxShadow: "0 1px 4px rgba(0, 0, 0, 0.06)",
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
    </>
  );
};
