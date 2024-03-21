import { Input, theme } from "antd";
import type React from "react";

import { isString } from "@/helpers/transform";

interface IJsonTextAreaProps {
  value?: any;

  onChange?: (data: any) => void;
}

const { useToken } = theme;

export const JsonTextArea: React.FC<IJsonTextAreaProps> = ({
  value,
  onChange,
  ...props
}) => {
  const { token } = useToken();
  const jsonValue = !isString(value)
    ? JSON.stringify(value, null, "\t")
    : value;
  const rowsCount = jsonValue?.split(/\r\n|\r|\n/)?.length;
  return (
    <Input.TextArea
      rows={rowsCount > 30 ? 30 : rowsCount}
      value={jsonValue}
      onChange={onChange}
      style={{
        backgroundColor: token.colorTextBase,
        color: token.colorBgBase,
        border: "none",
      }}
      {...props}
    />
  );
};
