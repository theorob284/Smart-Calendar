
import React, { useState } from 'react'
import { uploadFile } from './ApiUpload'
import { useNavigate } from 'react-router-dom'

export default function Upload({onUploaded}) {

    const [status, setStatus] = useState("")
    const navigate = useNavigate()


    const handleChange = async (e) => {

        const file = e.target.files?.[0];
        if (!file) return;
        try {
            setStatus("Uploading...")
            const data = await uploadFile(file)
            setStatus(`Uploaded (${data.title})`)
            if (onUploaded) onUploaded();
            const docId = data.document.id;
            navigate(`/review/${docId}`);
        } catch (e) {
            console.error(e);
            setStatus("upload failed");
        } finally {
            e.target.value = "";
        }
    
    }

    return (
        <div style={{ padding: 12 }}>
      <label>
        <span>Import file: </span>
        <input type="file" accept=".pdf,image/*,.ics" onChange={handleChange} />
      </label>
      <div>{status}</div>
    </div>
  );
}
