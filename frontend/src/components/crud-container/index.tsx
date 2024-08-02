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
      navigate("/sign-in");
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
        navigate("/");
        break;
      default:
        navigate(`/list/${item.key}`);
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
        <Header style={{ background: colorPrimary, paddingInline: 20 }}>
          <Row justify="space-between">
            <Col>
              <Space>
                {isMobile && (
                  <Menu
                    style={{ background: colorPrimary }}
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

                <Link to="/">
                  <Image
                    src={
                      (window as any).SERVER_DOMAIN +
                      configuration.site_header_logo
                    }
                    preview={false}
                    height={32}
                    alt={configuration.site_name}
                    style={{ marginTop: -2 }}
                  />
                </Link>

                {!isMobile && (
                  <Link to="/">
                    <span
                      style={{
                        color: colorBgContainer,
                        fontSize: 18,
                        marginLeft: 10,
                      }}
                    >
                      {configuration.site_name}
                    </span>
                  </Link>
                )}
              </Space>
            </Col>
            <Col>
              <Space>
                {!isMobile && (
                  <span style={{ color: colorBgContainer, marginRight: 5 }}>
                    {
                      (signedInUser || ({} as any))[
                        configuration.username_field
                      ]
                    }
                  </span>
                )}

                <Menu
                  style={{ background: colorPrimary }}
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
            <Sider style={{ background: colorBgContainer, borderRadius: 8 }}>
              <div style={{ padding: 10 }}>
                <Input
                  value={search}
                  onChange={onSearch}
                  placeholder={_t("Search By Menu") as string}
                  prefix={<SearchOutlined />}
                />
              </div>
              <Menu
                mode="inline"
                theme="light"
                defaultSelectedKeys={[model || "dashboard"]}
                style={{
                  borderRight: 0,
                  overflowY: "scroll",
                }}
                items={items as any}
                onClick={onClickSideBarMenuItem}
              />
            </Sider>
          )}
          <Layout style={{ padding: 16 }}>
            <Row justify="space-between">
              <Col>{breadcrumbs}</Col>
              {viewOnSite && (
                <Col>
                  <a href={viewOnSite} target="_blank" rel="noreferrer">
                    <LinkOutlined /> {_t("View on site")}
                  </a>
                </Col>
              )}
            </Row>
            <Card
              title={
                <Row justify="space-between">
                  <Col>
                    <Title style={{ margin: 0, marginTop: 15 }} level={5}>
                      {title}
                    </Title>
                  </Col>
                  {headerActions ? <Col>{headerActions}</Col> : null}
                </Row>
              }
              style={{ marginTop: 16 }}
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
