import { Button, Divider, Form, Input, message, Modal, Tooltip } from 'antd';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { EditOutlined } from '@ant-design/icons';
import { patchFetcher } from 'fetchers/fetchers';
import { handleError } from 'helpers/forms';
import { useMutation } from '@tanstack/react-query';

export interface IPasswordInput {
  parentId: string;
  passwordModalForm?: boolean;
}

export const PasswordInput: React.FC<IPasswordInput> = ({
  parentId,
  passwordModalForm,
  ...props
}) => {
  const { t: _t } = useTranslation('PasswordInput');
  const [form] = Form.useForm();
  const [open, setOpen] = React.useState<boolean>(false);

  const onClose = () => {
    setOpen(false);
    form.resetFields();
  };

  const onOpen = () => {
    form.resetFields();
    setOpen(true);
  };

  const { mutate, isLoading } = useMutation(
    (payload: any) => patchFetcher(`/change-password/${parentId}`, payload),
    {
      onSuccess: () => {
        message.success(_t('Succesfully changed'));
        onClose();
      },
      onError: (error: Error) => {
        handleError(error, form);
      },
    }
  );

  const onChangePassword = (data: any) => {
    mutate(data);
  };

  if (!passwordModalForm) {
    return <Input.Password {...props} />;
  }
  return (
    <>
      <Input.Password
        prefix={
          <Tooltip title={_t('Change Password')}>
            <Button size="small" onClick={onOpen}>
              <EditOutlined />
            </Button>
          </Tooltip>
        }
        {...props}
      />
      <Modal open={open} title={_t('Change Password')} onCancel={onClose} footer={null}>
        <Divider />
        <Form form={form} layout="vertical" onFinish={onChangePassword}>
          <Form.Item name="password" label="Password">
            <Input.Password />
          </Form.Item>
          <Form.Item name="confirm_password" label="Confirm Password">
            <Input.Password />
          </Form.Item>
          <Divider />
          <Form.Item>
            <Button type="primary" loading={isLoading} htmlType="submit">
              {_t('Save')}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
