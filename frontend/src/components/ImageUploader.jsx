import React from 'react';

function ImageUploader({ onUpload, fileInputRef }) {
  return (
    <input
      ref={fileInputRef}
      id="hidden-file-input"
      type="file"
      accept="image/*"
      onChange={onUpload}
      style={{ display: "none" }}
    />
  );
}

export default ImageUploader;
