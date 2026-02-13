import AxiosInstance from "../Calendar/AxiosInstance";

export async function uploadFile(fileOrFiles) {

  const files = Array.isArray(fileOrFiles) ? fileOrFiles : [fileOrFiles];
  const formData = new FormData();

  files.forEach((file) => formData.append("files", file));
    
  formData.append("title", `Upload (${files.length} files)`)
  const res = await AxiosInstance.post("api/uploads/", formData, {headers: { "Content-Type": "multipart/form-data" },});

  return res.data;
}
