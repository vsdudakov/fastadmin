import type React from "react";
import ReactQuill from "react-quill";

import "react-quill/dist/quill.snow.css";

interface ITextEditorFieldProps {
  value?: any;

  onChange?: (value: any) => void;
}

export const TextEditor: React.FC<ITextEditorFieldProps> = ({
  value,
  onChange,
  ...props
}) => {
  return (
    <ReactQuill
      theme="snow"
      value={value}
      onChange={onChange}
      formats={[
        "header",
        "bold",
        "italic",
        "underline",
        "strike",
        "blockquote",
        "list",
        "bullet",
        "indent",
        "link",
        "image",
      ]}
      modules={{
        toolbar: [
          [{ header: [1, 2, 3, 4, false] }],
          ["bold", "italic", "underline", "strike", "blockquote"],
          [
            { list: "ordered" },
            { list: "bullet" },
            { indent: "-1" },
            { indent: "+1" },
          ],
          ["link", "image"],
          ["clean"],
        ],
      }}
      {...props}
    />
  );
};
