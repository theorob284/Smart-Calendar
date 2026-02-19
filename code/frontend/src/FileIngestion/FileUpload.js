
import React, { useState } from 'react'
import { uploadFile } from './ApiUpload'
import { useNavigate } from 'react-router-dom'
import "../CSS/Upload.css"

export default function Upload({onUploaded}) {
  const [multipleFiles, setMultipleFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();

  const addFiles = (files) => {
    if (!files.length) return;

    setMultipleFiles((prev) => {
      const map = new Map();
      [...prev, ...files].forEach((f) => {
        const key = `${f.name}_${f.size}_${f.lastModified}`;
        map.set(key, f);
      });
      return Array.from(map.values());
    });

    setStatus("Files selected");
  };

  const handleChange = (e) => {
    const files = Array.from(e.target.files || []);
    addFiles(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files || []);
    addFiles(files);
  };

  const handleUpload = async () => {
    if (!multipleFiles.length) return;

    try {
      setStatus(`Uploading ${multipleFiles.length} file(s)...`);
      const data = await uploadFile(multipleFiles);
      setStatus(`Uploaded (${multipleFiles.length}) file(s)`);

      if (onUploaded) onUploaded();

      const docId = data.document?.id;
      if (docId) navigate(`/review/${docId}`);
    } catch (e) {
      console.error(e);
      setStatus("Upload failed - Ensure file is PDF, Calendar or Image");
    }
  };

  return (
    <div className="uploadPage">
      <div className="uploadCard">
        <h2>Import Calendar Files</h2>

        <div className={`uploadBox ${dragActive ? "dragActive" : ""}`} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
          <label className="fileButton">Choose Files
            <input type="file" multiple accept=".pdf,image/*,.ics" onChange={handleChange} />
          </label>
          <p className="uploadHint"> Or drag and drop files here (.ics, PDF, images) </p>
        </div>

        <button className="uploadPrimary" onClick={handleUpload} disabled={!multipleFiles.length} > Upload</button>

        {status && <p className="uploadStatus">{status}</p>}

        {multipleFiles.length > 0 && (
          <ul className="fileList">
            {multipleFiles.map((f) => {
              const key = `${f.name}_${f.size}_${f.lastModified}`;
              return (
                <li key={key}>
                  {f.name}
                  <button type="button" onClick={() => setMultipleFiles((prev) => prev.filter((x) =>`${x.name}_${x.size}_${x.lastModified}` !== key))}>remove</button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}