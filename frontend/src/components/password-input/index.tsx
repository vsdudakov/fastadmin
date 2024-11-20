import { EditOutlined } from "@ant-design/icons";
import { useMutation } from "@tanstack/react-query";
import {
  Button,
  Divider,
  Form,
  Input,
  Modal,
  Space,
  Tooltip,
  message,
} from "antd";
import React from "react";
import { useTranslation } from "react-i18next";

import { patchFetcher } from "@/fetchers/fetchers";
import { handleError } from "@/helpers/forms";

export interface IPasswordInput {
  parentId?: string;
}

export const PasswordInput: React.FC<IPasswordInput> = ({
  parentId,
  ...props
}) => {
  const { t: _t } = useTranslation("PasswordInput");
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

  const { mutate, isPending: isLoading } = useMutation({
    mutationFn: (data: any) =>
      patchFetcher(`/change-password/${parentId}`, data),
    onSuccess: () => {
      message.success(_t("Succesfully changed"));
      onClose();
    },
    onError: (error: Error) => {
      handleError(error, form);
    },
  });

  const onChangePassword = (data: any) => {
    mutate(data);
  };

  if (!parentId) {
    return <Input.Password {...props} />;
  }
  return (
    <>
      <Space.Compact style={{ width: "100%" }}>
        <Tooltip title={_t("Change Password")}>
          <Button onClick={onOpen}>
            <EditOutlined />
          </Button>
        </Tooltip>
        <Input.Password {...props} disabled />
      </Space.Compact>
      <Modal
        open={open}
        title={_t("Change Password")}
        onCancel={onClose}
        footer={null}
      >
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
              {_t("Save")}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
