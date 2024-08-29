import { SwapOutlined } from "@ant-design/icons";
import { Button, Input, Space, Tooltip } from "antd";
import type React from "react";

import { useTranslation } from "react-i18next";
import slugify from "slugify";

interface ISlugInputProps {
  value?: any;

  onChange?: (data: any) => void;
}

export const SlugInput: React.FC<ISlugInputProps> = ({
  value,
  onChange,
  ...props
}) => {
  const { t: _t } = useTranslation("SlugInput");

  const onSwap = () => {
    if (onChange) onChange(slugify(value));
  };
  return (
    <Space.Compact style={{ width: "100%" }}>
      <Tooltip title={_t("Slugify")}>
        <Button onClick={onSwap}>
          <SwapOutlined />
        </Button>
      </Tooltip>
      <Input value={value} onChange={onChange} {...props} />
    </Space.Compact>
  );
};
