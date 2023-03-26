import React from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

interface ITextEditorFieldProps {
  value?: any;
  onChange?: (value: any) => void;
}

export const TextEditor: React.FC<ITextEditorFieldProps> = ({ value, onChange, ...props }) => {
  return <ReactQuill theme="snow" value={value} onChange={onChange} {...props} />;
};
