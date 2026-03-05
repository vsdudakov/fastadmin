import { Col, Row } from "antd";
import type React from "react";
import { useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { ROUTES } from "@/constants/routes";
import { useIsMobile } from "@/hooks/useIsMobile";
import { usePageMeta } from "@/hooks/usePageMeta";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { SignInUserContext } from "@/providers/SignInUserProvider";

interface ISignInContainer {
  title: string;
  children: React.ReactNode;
}

export const SignInContainer: React.FC<ISignInContainer> = ({
  title,
  children,
}) => {
  const { signedIn } = useContext(SignInUserContext);
  const { configuration } = useContext(ConfigurationContext);
  const navigate = useNavigate();
  const isMobile = useIsMobile();

  useEffect(() => {
    if (signedIn) {
      navigate(ROUTES.HOME);
    }
  }, [navigate, signedIn]);

  usePageMeta({
    title: `${configuration.site_name} | ${title}`,
    description: title,
  });

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(160deg, #f0f5ff 0%, #f5f5f5 50%, #e8f4f8 100%)",
        padding: isMobile ? 16 : 24,
      }}
    >
      <Row justify="center" align="middle" style={{ minHeight: "100vh" }}>
        <Col xs={24} sm={20} md={16} lg={12} xl={10}>
          {children}
        </Col>
      </Row>
    </div>
  );
};
