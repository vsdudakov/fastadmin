import { Col, Row } from "antd";
import type React from "react";
import { useContext, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import { useNavigate } from "react-router-dom";

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
      navigate("/");
    }
  }, [navigate, signedIn]);

  return (
    <div style={{ height: "100vh" }}>
      <Helmet defaultTitle={title}>
        <meta name="description" content={title} />
      </Helmet>
      <Row justify="center" align="middle" style={{ height: "100%" }}>
        <Col xs={24} xl={8}>
          {children}
        </Col>
      </Row>
    </div>
  );
};
