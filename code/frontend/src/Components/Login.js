import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AxiosInstance from "../Calendar/AxiosInstance";
import { Link } from "react-router-dom";
import "../CSS/Auth.css"

export default function Login() {
  const nav = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await AxiosInstance.post("api/auth/token/", { username, password });
      localStorage.setItem("accessToken", res.data.access);
      localStorage.setItem("refreshToken", res.data.refresh);
      nav("/");
    } catch (err) {
      setError("Invalid username or password.");
    }
  };

  return (
    <div className="authPage">
      <form className="authCard" onSubmit={submit}>
        <h2 className="authTitle">Sign in</h2>
        <p className="authSub">Access your calendar and uploads.</p>

        <div className="authField">
          <label>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>

        <div className="authField">
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>

        {error && <div className="authError">{error}</div>}

        <div className="authActions">
          <button className="authPrimary" type="submit">Sign in</button>
        </div>

        <div className="authLinkRow">
          <span>No account?</span>
          <Link to="/register">Create one</Link>
        </div>
      </form>
    </div>
  );
}
