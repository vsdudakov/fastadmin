import { Input, theme } from 'antd';
import { isString } from 'helpers/transform';
import React from 'react';

interface IJsonTextAreaProps {
  value?: any;
  onChange?: (data: any) => void;
}

const { useToken } = theme;

export const JsonTextArea: React.FC<IJsonTextAreaProps> = ({ value, onChange, ...props }) => {
  const { token } = useToken();
  const jsonValue = !isString(value) ? JSON.stringify(value, null, '\t') : value;
  return (
    <Input.TextArea
      rows={jsonValue?.split(/\r\n|\r|\n/)?.length}
      value={jsonValue}
      onChange={onChange}
      style={{ backgroundColor: token.colorTextBase, color: token.colorBgBase, border: 'none' }}
      {...props}
    />
  );
};
