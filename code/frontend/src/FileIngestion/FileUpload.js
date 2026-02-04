
import {React, Button} from 'react'
import { uploadFile } from './ApiUpload'

export default function Upload() {

    const onFileSelected = async (file) => {
        const data = await uploadFile(file)
    }

    return (
        <div style={{ padding: 12}}>
            <label>
                <span> Import file: </span>
                <input type="file" accept=".pdf, image/*, .ics" onChange={ (e) => {
                    const file = e.target.files?.[0]
                    if (file) onFileSelected(file);
                    e.target.value = "" // pick same file
                }}>
                </input>
            </label>
        </div>
    )

}
