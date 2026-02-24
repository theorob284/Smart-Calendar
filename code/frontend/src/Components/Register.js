import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AxiosInstance from "../Calendar/AxiosInstance";
import "../CSS/Auth.css"

export default function Register() {
  const nav = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await AxiosInstance.post("api/auth/register/", { username, password });
      nav("/login");
    } catch (err) {
      const msg =err?.response?.data?.username?.[0] || err?.response?.data?.password?.[0] || "Could not register. Try a different username or a longer password.";
      setError(msg);
    }
  };

  return (
    <div className="authPage">
      <form className="authCard" onSubmit={submit}>
        <h2 className="authTitle">Create account</h2>
        <p className="authSub">Set up your login for Smart Calendar.</p>

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
          <button className="authPrimary" type="submit">Create account</button>
        </div>

        <div className="authLinkRow">
          <span>Already have an account?</span>
          <Link to="/login">Sign in</Link>
        </div>
      </form>
    </div>
  );
}
