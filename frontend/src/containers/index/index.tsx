import { Col, Empty, Row } from "antd";
import type React from "react";
import { useContext } from "react";
import { useTranslation } from "react-i18next";

import { CrudContainer } from "@/components/crud-container";
import { DashboardWidget } from "@/components/dashboard-widget";
import type { IDashboardWidget } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const Index: React.FC = () => {
  const { t: _t } = useTranslation("Dashboard");
  const { configuration } = useContext(ConfigurationContext);
  return (
    <CrudContainer title={_t("Dashboard")}>
      <Row gutter={[16, 16]}>
        {configuration.dashboard_widgets.map((widget: IDashboardWidget) => (
          <Col xs={24} md={12} key={widget.title}>
            <DashboardWidget widget={widget} />
          </Col>
        ))}
      </Row>
      {configuration.dashboard_widgets.length === 0 && <Empty />}
    </CrudContainer>
  );
};
