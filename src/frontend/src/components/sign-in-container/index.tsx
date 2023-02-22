import { Col, Row } from 'antd';
import React from 'react';
import { Helmet } from 'react-helmet-async';

interface ISignInContainer {
  title: string;
  children: JSX.Element | JSX.Element[];
}

export const SignInContainer: React.FC<ISignInContainer> = ({ title, children }) => {
  return (
    <div style={{ height: '100vh' }}>
      <Helmet defaultTitle={title}>
        <meta name="description" content={title} />
      </Helmet>
      <Row justify="center" align="middle" style={{ height: '100%' }}>
        <Col xs={24} xl={6}>
          {children}
        </Col>
      </Row>
    </div>
  );
};
