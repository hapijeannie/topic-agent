"use client";

import { useEffect, useState } from "react";

export default function LoginPage() {
  const [error, setError] = useState("");
  useEffect(() => {
    const reason = new URLSearchParams(window.location.search).get("error");
    if (reason) setError(reason === "denied" ? "这个 GitHub 账号没有访问权限，请使用你的个人账号。" : "登录未完成，请重新尝试。");
  }, []);
  return <main className="login-panel">
    <p className="hint">个人素材库</p>
    <h1>登录，继续积累。</h1>
    <p className="lead">保存文章，查看原文与分块。仅允许授权的个人账号访问。</p>
    {error && <p className="error" role="alert">{error}</p>}
    <a className="button-link" href="/backend/auth/login">使用 GitHub 登录</a>
  </main>;
}
