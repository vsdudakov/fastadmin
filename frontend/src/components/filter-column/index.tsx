import { FilterOutlined, SearchOutlined } from "@ant-design/icons";
import { Button, Col, Input, Radio, Row, Space } from "antd";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { getWidgetCls } from "@/helpers/widgets";
import type { EFieldWidgetType } from "@/interfaces/configuration";

interface IFilterColumn {
  widgetType: EFieldWidgetType;

  widgetProps?: any;

  value?: any;

  onFilter(value: any): void;
  onReset(): void;
}

export const FilterColumn = ({
  widgetType,
  widgetProps,
  value,
  onFilter,
  onReset,
}: IFilterColumn) => {
  const { t: _t } = useTranslation("List");

  const [filterValue, setFilterValue] = useState<any | undefined>();

  const [FilterWidget, defaultProps]: any = getWidgetCls(widgetType, _t);

  useEffect(() => {
    setFilterValue(value);
  }, [value]);

  const onFilterButton = () => {
    onFilter(filterValue);
  };

  const onChangeWidget = (widgetValue: any) => {
    switch (FilterWidget) {
      case Input:
      case Input.TextArea:
      case Radio.Group:
        setFilterValue(widgetValue.target.value);
        break;
      default:
        setFilterValue(widgetValue);
        break;
    }
  };

  return (
    <Row style={{ width: 400 }}>
      <Col xs={24} style={{ padding: 10 }}>
        <FilterWidget
          value={filterValue}
          size="middle"
          onChange={onChangeWidget}
          placeholder={_t("Filter By")}
          {...(defaultProps || {})}
          {...(widgetProps || {})}
        />
      </Col>
      <Col xs={24} style={{ padding: 10 }}>
        <Space align="end">
          <Button onClick={onReset} size="small">
            {_t("Reset")}
          </Button>
          <Button
            type="primary"
            onClick={onFilterButton}
            icon={
              FilterWidget === Input ? <SearchOutlined /> : <FilterOutlined />
            }
            size="small"
          >
            {_t("Filter")}
          </Button>
        </Space>
      </Col>
    </Row>
  );
};
