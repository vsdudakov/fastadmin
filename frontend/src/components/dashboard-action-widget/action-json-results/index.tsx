import { CopyOutlined, ExpandOutlined } from "@ant-design/icons";
import {
  Button,
  Col,
  Divider,
  Input,
  Modal,
  message,
  Row,
  Space,
  Tooltip,
  theme,
} from "antd";
import React, { useContext, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import type { IWidgetActionResponse } from "@/interfaces/configuration";
import { ThemeContext } from "@/providers/ThemeProvider";

interface ActionJsonResultsProps {
  actionResult: IWidgetActionResponse;
  maxHeight?: number;
  toolbarActions?: React.ReactNode;
}

const { useToken } = theme;

const escapeRegExp = (value: string) =>
  value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

export const ActionJsonResults: React.FC<ActionJsonResultsProps> = ({
  actionResult,
  maxHeight,
  toolbarActions,
}) => {
  const { t: _t } = useTranslation("DashboardWidget");
  const { token } = useToken();
  const { mode } = useContext(ThemeContext);

  const [searchTerm, setSearchTerm] = useState("");
  const [isResultsModalVisible, setIsResultsModalVisible] = useState(false);

  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) {
      return actionResult.data;
    }
    const term = searchTerm.toLowerCase();
    return actionResult.data.filter((row) =>
      JSON.stringify(row).toLowerCase().includes(term),
    );
  }, [actionResult.data, searchTerm]);

  const highlightedResults = useMemo(() => {
    const json = JSON.stringify(filteredData, null, 2);

    if (!searchTerm.trim()) {
      return json;
    }

    const term = searchTerm.toLowerCase();
    const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, "gi");
    const parts = json.split(regex);

    return parts.map((part, index) => {
      const key = `${part}-${index}`;
      return part.toLowerCase() === term ? (
        <mark key={key}>{part}</mark>
      ) : (
        <React.Fragment key={key}>{part}</React.Fragment>
      );
    });
  }, [filteredData, searchTerm]);

  const handleCopyResults = async () => {
    await navigator.clipboard.writeText(JSON.stringify(filteredData, null, 2));
    message.success(_t("Results copied to clipboard"));
  };

  return (
    <>
      <Row>
        <Divider />
        <Col xs={24}>
          <Row justify="space-between">
            <Col xs={12}>
              <Input.Search
                placeholder={_t("Search results")}
                onSearch={(value) => setSearchTerm(value)}
                enterButton
              />
            </Col>
            <Col>
              <Space>
                <Tooltip title={_t("Expand results")}>
                  <Button
                    type="default"
                    onClick={() => setIsResultsModalVisible(true)}
                    icon={<ExpandOutlined />}
                  />
                </Tooltip>
                <Tooltip title={_t("Copy to clipboard")}>
                  <Button
                    type="primary"
                    onClick={handleCopyResults}
                    icon={<CopyOutlined />}
                  />
                </Tooltip>
                {toolbarActions}
              </Space>
            </Col>
          </Row>
          <pre
            style={{
              marginTop: 12,
              maxHeight: maxHeight || 240,
              overflow: "auto",
              background: mode === "dark" ? token.colorBgContainer : "#fafafa",
              color: mode === "dark" ? token.colorText : "inherit",
              padding: 8,
              borderRadius: 4,
              border:
                mode === "dark"
                  ? `1px solid ${token.colorBorderSecondary}`
                  : "1px solid #f0f0f0",
            }}
          >
            {highlightedResults}
          </pre>
        </Col>
      </Row>
      <Modal
        open={isResultsModalVisible}
        title={_t("Action results")}
        onCancel={() => setIsResultsModalVisible(false)}
        footer={null}
        width="100%"
        style={{ top: 0, paddingBottom: 0, marginTop: 20 }}
        styles={{ body: { paddingTop: 0 } }}
      >
        <Space orientation="vertical" style={{ width: "100%" }} size="middle">
          <Row justify="start" align="middle">
            <Col xs={20}>
              <Input.Search
                style={{ marginTop: 12 }}
                placeholder={_t("Search results")}
                onSearch={(value) => setSearchTerm(value)}
                defaultValue={searchTerm}
                enterButton
              />
            </Col>
          </Row>
          <pre
            style={{
              flex: 1,
              maxHeight: "calc(100vh - 300px)",
              overflow: "auto",
              background: mode === "dark" ? token.colorBgContainer : "#fafafa",
              color: mode === "dark" ? token.colorText : "inherit",
              padding: 12,
              borderRadius: 4,
              border:
                mode === "dark"
                  ? `1px solid ${token.colorBorderSecondary}`
                  : "1px solid #f0f0f0",
            }}
          >
            {highlightedResults}
          </pre>
          <Row justify="end">
            <Col>
              <Tooltip title={_t("Copy to clipboard")}>
                <Button
                  type="primary"
                  onClick={handleCopyResults}
                  icon={<CopyOutlined />}
                />
              </Tooltip>
            </Col>
          </Row>
        </Space>
      </Modal>
    </>
  );
};
