
import React, { useState } from 'react'
import { uploadFile } from './ApiUpload'

export default function Upload({onUploaded}) {

    const [status, setStatus] = useState("")

    const handleChange = async (e) => {

        const file = e.target.files?.[0];
        if (!file) return;
        try {
            setStatus("Uploading...")
            const data = await uploadFile(file)
            setStatus("Uploaded (${data.title})")
            if (onUploaded) onUploaded();
        } catch (e) {
            console.error(e);
            setStatus("uploaed failed");
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
