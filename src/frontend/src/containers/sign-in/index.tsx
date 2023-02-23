import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Col, Form, Image, Input, Row } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';

import { SignInContainer } from 'components/sign-in-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { SignInUserContext } from 'providers/SignInUserProvider';
import { postFetcher } from 'fetchers/fetchers';
import { setFormErrors } from 'helpers/forms';

export const SignIn: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { configuration } = useContext(ConfigurationContext);
  const { signedInUserRefetch } = useContext(SignInUserContext);
  const { t: _t } = useTranslation('SignIn');

  const { mutate: mutateSignIn, isLoading: loadingSignIn } = useMutation(
    (payload: any) => postFetcher('/sign-in', payload),
    {
      onSuccess: (response) => {
        signedInUserRefetch();
        navigate('/');
      },
      onError: (error) => {
        setFormErrors(form, error);
      },
    }
  );

  const onFinish = (data: any) => {
    mutateSignIn(data);
  };

  return (
    <SignInContainer title={`${_t('Sign In')}`}>
      <Card>
        <Row justify="center">
          <Col>
            <Image
              src={(window as any).SERVER_FOMAIN + configuration.site_sign_in_logo}
              height={100}
              alt={configuration.site_name}
              preview={false}
            />
          </Col>
        </Row>

        <Form
          initialValues={{ remember: true }}
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item label="Username" name="username" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item label="Password" name="password" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>

          <Row justify="end">
            <Col>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loadingSignIn}>
                  {_t('Sign In')}
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>
    </SignInContainer>
  );
};
