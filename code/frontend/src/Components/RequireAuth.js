import { Navigate, Outlet } from "react-router-dom";

// This function tells the app what pages can be loaded witha authorisation
export default function RequireAuth({ }) {

  const token = localStorage.getItem("accessToken");
  if (!token)return <Navigate to="/login" replace />;
  return <Outlet />;
}
