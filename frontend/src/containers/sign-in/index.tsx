import { useMutation } from "@tanstack/react-query";
import { Button, Card, Col, Form, Image, Input, Row, Space, theme } from "antd";
import type React from "react";
import { useContext } from "react";
import { useTranslation } from "react-i18next";

import { SignInContainer } from "@/components/sign-in-container";
import { postFetcher } from "@/fetchers/fetchers";
import { handleError } from "@/helpers/forms";
import { getTitleFromFieldName } from "@/helpers/title";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { SignInUserContext } from "@/providers/SignInUserProvider";

export const SignIn: React.FC = () => {
  const [form] = Form.useForm();
  const {
    token: { colorPrimary },
  } = theme.useToken();
  const { configuration } = useContext(ConfigurationContext);
  const { signedInUserRefetch } = useContext(SignInUserContext);
  const { t: _t } = useTranslation("SignIn");

  const { mutate: mutateSignIn, isPending: loadingSignIn } = useMutation({
    mutationFn: (payload: any) => postFetcher("/sign-in", payload),
    onSuccess: () => {
      signedInUserRefetch();
    },
    onError: (error) => {
      handleError(error, form);
    },
  });

  const onFinish = (data: any) => {
    mutateSignIn(data);
  };

  return (
    <SignInContainer title={`${_t("Sign In")}`}>
      <Card>
        <Row justify="center">
          <Col>
            <Space style={{ marginBottom: 20 }}>
              <Image
                src={
                  (window as any).SERVER_DOMAIN +
                  configuration.site_sign_in_logo
                }
                height={80}
                alt={configuration.site_name}
                preview={false}
              />
              <span
                style={{ color: colorPrimary, fontSize: 36, fontWeight: 600 }}
              >
                {configuration.site_name}
              </span>
            </Space>
          </Col>
        </Row>

        <Form
          initialValues={{ remember: true }}
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            label={getTitleFromFieldName(
              configuration?.username_field || "username",
            )}
            name="username"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[{ required: true }]}
          >
            <Input.Password />
          </Form.Item>

          <Row justify="end">
            <Col>
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loadingSignIn}
                >
                  {_t("Sign In")}
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>
    </SignInContainer>
  );
};
