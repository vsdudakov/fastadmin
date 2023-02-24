import { Col, Image, Layout, Menu, Row, theme, Card, Typography, Space } from 'antd';
import { UserOutlined, BarsOutlined } from '@ant-design/icons';
import React, { useContext, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';
import { useMutation } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { SignInUserContext } from 'providers/SignInUserProvider';
import { postFetcher } from 'fetchers/fetchers';
import { IModel } from 'interfaces/configuration';
import { useIsMobile } from 'hooks/useIsMobile';

const { Header, Sider } = Layout;
const { Title } = Typography;

interface ICrudContainer {
  title: string;
  breadcrumbs?: JSX.Element | JSX.Element[];
  actions?: JSX.Element | JSX.Element[];
  children: JSX.Element | JSX.Element[];
}

export const CrudContainer: React.FC<ICrudContainer> = ({
  title,
  breadcrumbs,
  actions,
  children,
}) => {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const { model } = useParams();
  const { configuration } = useContext(ConfigurationContext);
  const { signedInUser, signedInUserRefetch, signedIn } = useContext(SignInUserContext);
  const { t: _t } = useTranslation('CrudContainer');

  const {
    token: { colorBgContainer, colorPrimary },
  } = theme.useToken();

  useEffect(() => {
    if (!signedIn) {
      navigate('/sign-in');
    }
  }, [navigate, signedIn]);

  const { mutate: mutateSignOut } = useMutation(() => postFetcher('/sign-out', {}), {
    onSuccess: () => {
      signedInUserRefetch();
    },
  });

  const onClickSideBarMenuItem = (item: any) => {
    switch (item.key) {
      case 'dashboard':
        navigate('/');
        break;
      default:
        navigate(`/list/${item.key}`);
        break;
    }
  };

  const onClickRightMenuItem = (item: any) => {
    switch (item.key) {
      case 'sign-out':
        mutateSignOut();
        break;
      default:
        break;
    }
  };

  const items = [
    {
      key: 'dashboard',
      label: _t('Dashboard'),
    },
    ...configuration.models.map((model: IModel) => {
      return {
        key: model.name,
        label: model.name,
      };
    }),
  ];

  return (
    <>
      <Helmet defaultTitle={title}>
        <meta name="description" content={title} />
      </Helmet>
      <Layout style={{ height: '100vh' }}>
        <Header style={{ background: colorPrimary, paddingInline: 20 }}>
          <Row justify="space-between">
            <Col>
              <Space>
                {isMobile && (
                  <Menu
                    style={{ background: colorPrimary }}
                    theme="light"
                    mode="horizontal"
                    defaultSelectedKeys={[model || 'dashboard']}
                    items={[
                      {
                        key: signedInUser?.id || 'key',
                        icon: <BarsOutlined style={{ color: colorBgContainer }} />,
                        children: items,
                      },
                    ]}
                    onClick={onClickSideBarMenuItem}
                  />
                )}

                <Link to="/">
                  <Image
                    src={(window as any).SERVER_FOMAIN + configuration.site_header_logo}
                    preview={false}
                    height={32}
                    alt={configuration.site_name}
                    style={{ marginTop: -2 }}
                  />
                </Link>

                {!isMobile && (
                  <Link to="/">
                    <span style={{ color: colorBgContainer, fontSize: 18, marginLeft: 10 }}>
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
                    {(signedInUser || ({} as any))[configuration.username_field]}
                  </span>
                )}

                <Menu
                  style={{ background: colorPrimary }}
                  theme="light"
                  mode="horizontal"
                  items={[
                    {
                      key: signedInUser?.id || 'key',
                      icon: <UserOutlined style={{ color: colorBgContainer }} />,
                      children: [
                        {
                          key: 'sign-out',
                          label: _t('Sign Out'),
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
            <Sider style={{ background: colorBgContainer }}>
              <Menu
                mode="inline"
                theme="light"
                defaultSelectedKeys={[model || 'dashboard']}
                style={{
                  borderRight: 0,
                  marginTop: 50,
                }}
                items={items}
                onClick={onClickSideBarMenuItem}
              />
            </Sider>
          )}
          <Layout style={{ padding: 16 }}>
            {breadcrumbs}
            <Card
              title={
                <Row justify="space-between">
                  <Col>
                    <Title style={{ margin: 0, marginTop: 15 }} level={5}>
                      {title}
                    </Title>
                  </Col>
                  <Col>{actions}</Col>
                </Row>
              }
              style={{ marginTop: 16 }}
            >
              {children}
            </Card>
          </Layout>
        </Layout>
      </Layout>
    </>
  );
};
