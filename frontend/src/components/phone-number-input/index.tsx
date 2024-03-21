import { theme } from "antd";
import type React from "react";
import PhoneInput from "react-phone-input-2";

import "react-phone-input-2/lib/style.css";

interface IPhoneFieldProps {
  value?: any;

  onChange?: (value: any) => void;
}

const { useToken } = theme;

export const PhoneNumberInput: React.FC<IPhoneFieldProps> = ({
  value,
  onChange,
  ...props
}) => {
  const { token } = useToken();
  return (
    <PhoneInput
      value={value}
      onChange={onChange}
      country="us"
      buttonStyle={{
        backgroundColor: token.colorBgBase,
        color: token.colorTextBase,
        borderColor: token.colorBorder,
      }}
      dropdownStyle={{
        backgroundColor: token.colorBgBase,
        color: token.colorTextBase,
        borderRadius: token.borderRadius,
        borderColor: token.colorBorder,
      }}
      inputStyle={{
        backgroundColor: token.colorBgBase,
        color: token.colorTextBase,
        width: "100%",
        height: 33,
        borderRadius: token.borderRadius,
        borderColor: token.colorBorder,
      }}
      {...props}
    />
  );
};
