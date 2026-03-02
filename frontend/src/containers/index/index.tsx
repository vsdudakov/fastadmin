import { Col, Empty, Row, Tabs } from "antd";
import type React from "react";
import { useContext, useMemo } from "react";
import { useTranslation } from "react-i18next";

import { CrudContainer } from "@/components/crud-container";
import { DashboardActionWidget } from "@/components/dashboard-action-widget";
import { DashboardChartWidget } from "@/components/dashboard-chart-widget";
import {
  EDashboardWidgetType,
  type IModel,
  type IModelWidgetAction,
} from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const Index: React.FC = () => {
  const { t: _t } = useTranslation("Dashboard");
  const { configuration } = useContext(ConfigurationContext);

  const widgets = useMemo(
    () =>
      (configuration.models as IModel[]).flatMap((model) =>
        (model.widget_actions || []).map((widgetAction) => ({
          modelName: model.name,
          widgetAction,
        })),
      ),
    [configuration.models],
  );

  return (
    <CrudContainer title={_t("Dashboard")}>
      {widgets.length === 0 && (
        <Empty
          description={_t("No dashboard widgets configured")}
          style={{ padding: "48px 0" }}
        />
      )}
      {widgets.length > 0 && (
        <Tabs
          items={Array.from(
            widgets.reduce((acc, widget) => {
              const tabKey = widget.widgetAction.tab || _t("Dashboard");
              const existing = acc.get(tabKey) || [];
              existing.push(widget);
              acc.set(tabKey, existing);
              return acc;
            }, new Map<
              string,
              { modelName: string; widgetAction: IModelWidgetAction }[]
            >()),
          ).map(([tabKey, tabWidgets]) => ({
            key: tabKey,
            label: tabKey,
            children: (
              <Row gutter={[24, 24]}>
                {tabWidgets.map(({ modelName, widgetAction }) => (
                  <Col
                    xs={24}
                    md={widgetAction.width || 12}
                    key={`${modelName}-${widgetAction.name}`}
                  >
                    {widgetAction.widget_action_type ===
                    EDashboardWidgetType.Action ? (
                      <DashboardActionWidget
                        modelName={modelName}
                        widgetAction={widgetAction}
                      />
                    ) : (
                      <DashboardChartWidget
                        modelName={modelName}
                        widgetAction={widgetAction}
                      />
                    )}
                  </Col>
                ))}
              </Row>
            ),
          }))}
        />
      )}
    </CrudContainer>
  );
};
