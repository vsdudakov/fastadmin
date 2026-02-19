import { Col, Row } from "antd";
import type React from "react";
import { useContext, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { useNavigate } from "react-router-dom";

import { ROUTES } from "@/constants/routes";
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
  const navigate = useNavigate();

  useEffect(() => {
    if (signedIn) {
      navigate(ROUTES.HOME);
    }
  }, [navigate, signedIn]);

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(160deg, #f0f5ff 0%, #f5f5f5 50%, #e8f4f8 100%)",
        padding: 24,
      }}
    >
      <Helmet defaultTitle={title}>
        <meta name="description" content={title} />
      </Helmet>
      <Row justify="center" align="middle" style={{ minHeight: "100vh" }}>
        <Col xs={24} sm={20} md={16} lg={12} xl={10}>
          {children}
        </Col>
      </Row>
    </div>
  );
};
