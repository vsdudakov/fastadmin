import { DownloadOutlined } from "@ant-design/icons";
import { useMutation } from "@tanstack/react-query";
import {
  Button,
  Col,
  Divider,
  Form,
  InputNumber,
  Modal,
  Row,
  Select,
  Space,
  message,
} from "antd";
import fileDownload from "js-file-download";
import querystring from "query-string";
import type React from "react";
import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";

import { postFetcher } from "@/fetchers/fetchers";
import { transformFiltersToServer } from "@/helpers/transform";
import { EExportFormat } from "@/interfaces/configuration";

export interface IExportBtn {
  model?: string;
  search?: string;
  sortBy?: string;

  filters?: any;

  style?: any;
}

export const ExportBtn: React.FC<IExportBtn> = ({
  model,
  search,
  sortBy,
  filters,
  style,
}) => {
  const [form] = Form.useForm();
  const { t: _t } = useTranslation("ExportBtn");

  const [open, setOpen] = useState<boolean>(false);

  const exportQueryString = querystring.stringify({
    search,
    sort_by: sortBy,
    ...transformFiltersToServer(filters),
  });

  const { mutate: mutateExport, isPending: isLoadingExport } = useMutation({
    mutationFn: (payload: any) =>
      postFetcher(`/export/${model}?${exportQueryString}`, payload),
    onSuccess: (data) => {
      const fileData =
        form.getFieldValue("format") === EExportFormat.JSON
          ? JSON.stringify(data)
          : data;
      fileDownload(
        fileData,
        `${model}.${form.getFieldValue("format").toLowerCase()}`,
      );
      setOpen(false);
      form.resetFields();
      message.success(_t("Successfully exported"));
    },
    onError: () => {
      message.error(_t("Server error"));
    },
  });

  const onExport = useCallback(
    (data: any) => mutateExport(data),
    [mutateExport],
  );
  const onClose = useCallback(() => setOpen(false), []);
  const onOpen = useCallback(() => setOpen(true), []);

  return (
    <>
      <Button style={style} loading={isLoadingExport} onClick={onOpen}>
        <Space>
          <DownloadOutlined />
          {_t("Export")}
        </Space>
      </Button>
      <Modal
        width={300}
        open={open}
        onCancel={onClose}
        footer={null}
        title={_t("Export")}
      >
        <Divider />
        <Row>
          <Col xs={24}>
            <Form
              form={form}
              layout="vertical"
              onFinish={onExport}
              initialValues={{
                limit: 1000,
                format: EExportFormat.CSV,
              }}
            >
              <Form.Item name="format" label={_t("Format")}>
                <Select
                  options={[
                    { label: EExportFormat.CSV, value: EExportFormat.CSV },
                    { label: EExportFormat.JSON, value: EExportFormat.JSON },
                  ]}
                />
              </Form.Item>
              <Form.Item name="limit" label={_t("Max Export Count")}>
                <InputNumber style={{ width: "100%" }} />
              </Form.Item>
              <Divider />
              <Form.Item>
                <Button type="primary" htmlType="submit">
                  <Space>
                    <DownloadOutlined />
                    {_t("Export")}
                  </Space>
                </Button>
              </Form.Item>
            </Form>
          </Col>
        </Row>
      </Modal>
    </>
  );
};
