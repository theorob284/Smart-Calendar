import AxiosInstance from "../Calendar/AxiosInstance";

export async function uploadFile(fileOrFiles) {
  //make sure we're working with arrays
  const files = Array.isArray(fileOrFiles) ? fileOrFiles : [fileOrFiles];
  const formData = new FormData();

  //add selected files to FormData
  files.forEach((file) => formData.append("files", file));
    //name upload batch
  formData.append("title", `Upload (${files.length} files)`)
  // send to backend
  const res = await AxiosInstance.post("api/uploads/", formData, {headers: { "Content-Type": "multipart/form-data" },});

  return res.data;
}
