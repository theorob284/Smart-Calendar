import AxiosInstance from "../Calendar/AxiosInstance";

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file); 
  formData.append("title", file.name)

  const res = await AxiosInstance.post("api/uploads/", formData, {headers: { "Content-Type": "multipart/form-data" },});

  return res.data;
}
