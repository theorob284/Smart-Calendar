
import React, { useState } from 'react'
import { uploadFile } from './ApiUpload'
import { useNavigate } from 'react-router-dom'

export default function Upload({onUploaded}) {
    const [multipleFiles, setMultipleFiles] = useState([])
    const [status, setStatus] = useState("")
    const navigate = useNavigate()


    const handleChange = (e) => {
      const files = Array.from(e.target.files || []);
      if (!files.length) return;

      setMultipleFiles((prev) => {
        const map = new Map();
        [...prev, ...files].forEach((f) => {
          const key = `${f.name}_${f.size}_${f.lastModified}`;
          map.set(key, f);
        });
        return Array.from(map.values());
      });
      setStatus((prevStatus) => "Files selected");
    };
      
    const handleUpload = async () => {
      if (!multipleFiles.length) return;

      try {
        setStatus(`Uploading ${multipleFiles.length} file(s)..`)
        const data = await uploadFile(multipleFiles);
        setStatus(`Uploaded (${multipleFiles.length}) file(s)`);
        if (onUploaded) onUploaded();
        const docId = data.document?.id;
        if (docId) navigate(`/review/${docId}`);
         
      } catch (e) {
        console.error(e);
        setStatus("upload failed");
      }
    }

    return (
    <div style={{ padding: 12 }}>
      <label>
        <span>Import files: </span>
        <input type="file" multiple accept=".pdf,image/*,.ics" onChange={handleChange} />
      </label>

      <div style={{marginTop: 10}}>
        <button onClick={handleUpload} disabled={!multipleFiles.length}> Upload</button>
      </div>
      <div style={{marginTop:8}}>{status}</div>
      
      {multipleFiles.length > 0 && (
      <ul style={{ marginTop: 10 }}>
        {multipleFiles.map((f) => {
          const key = `${f.name}_${f.size}_${f.lastModified}`;
          return (<li key={key}>{f.name}{" "}<button type="button" onClick={() => setMultipleFiles((prev) =>prev.filter((x) =>`${x.name}_${x.size}_${x.lastModified}` !== key))}>remove</button></li>);
        })}
      </ul>
    )}
    </div>
  );
}
