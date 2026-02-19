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
      <Card
        style={{
          maxWidth: 420,
          margin: "0 auto",
          borderRadius: 12,
          boxShadow: "0 8px 24px rgba(0, 0, 0, 0.08)",
          border: "none",
        }}
      >
        <Row justify="center">
          <Col>
            <Space
              direction="vertical"
              align="center"
              size="middle"
              style={{ width: "100%", marginBottom: 32 }}
            >
              <Image
                src={`${window.SERVER_DOMAIN ?? ""}${configuration.site_sign_in_logo ?? ""}`}
                height={72}
                alt={configuration.site_name}
                preview={false}
                style={{ display: "block" }}
              />
              <span
                style={{
                  color: colorPrimary,
                  fontSize: 28,
                  fontWeight: 600,
                  letterSpacing: "-0.02em",
                  lineHeight: 1.3,
                }}
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
          requiredMark={false}
          size="large"
        >
          <Form.Item
            label={getTitleFromFieldName(
              configuration?.username_field || "username",
            )}
            name="username"
            rules={[{ required: true }]}
          >
            <Input
              placeholder={getTitleFromFieldName(
                configuration?.username_field || "username",
              )}
            />
          </Form.Item>

          <Form.Item
            label={_t("Password")}
            name="password"
            rules={[{ required: true }]}
          >
            <Input.Password placeholder={_t("Password")} />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: 8 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loadingSignIn}
              block
              size="large"
              style={{ height: 44, fontWeight: 600 }}
            >
              {_t("Sign In")}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </SignInContainer>
  );
};
