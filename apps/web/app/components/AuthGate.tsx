"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

export default function AuthGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<{ login: string } | null>(null);
  const [error, setError] = useState("");
  const [checkedPath, setCheckedPath] = useState("");
  const [leaving, setLeaving] = useState(false);

  useEffect(() => {
    if (pathname === "/login") return;
    const controller = new AbortController();
    setError("");
    fetch("/backend/auth/me", { cache: "no-store", signal: controller.signal })
      .then(async (response) => {
        if (response.status === 401) { router.replace("/login"); return; }
        if (!response.ok) throw new Error(response.status === 403 ? "当前账号无权访问。" : "登录服务暂不可用，请稍后重试。");
        const profile = await response.json();
        if (!controller.signal.aborted) { setUser(profile); setCheckedPath(pathname); }
      })
      .catch((cause) => { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : "连接失败。"); });
    return () => controller.abort();
  }, [pathname, router]);

  async function logout() {
    setLeaving(true);
    try {
      const response = await fetch("/backend/auth/logout", { method: "POST" });
      if (!response.ok && response.status !== 401) throw new Error("退出失败，请重试。");
      setUser(null);
      setCheckedPath("");
      window.location.assign("/login");
    } catch {
      setError("退出失败，请重试。");
      setLeaving(false);
    }
  }

  if (pathname === "/login") return children;
  if (error) return <main className="library"><h1>暂时无法访问</h1><p role="alert">{error}</p><a href="/login">返回登录</a></main>;
  if (!user || checkedPath !== pathname) return <main className="library"><p role="status">正在确认登录状态……</p></main>;
  return <>
    <header className="navigation">
      <Link className="brand" href="/library">素材库</Link>
      <nav aria-label="主导航"><Link href="/library" aria-current={pathname.startsWith("/library") ? "page" : undefined}>文章列表</Link><Link href="/" aria-current={pathname === "/" ? "page" : undefined}>上传文章</Link></nav>
      <div className="account"><span>{user.login}</span><button onClick={logout} disabled={leaving}>{leaving ? "正在退出" : "退出"}</button></div>
    </header>
    {children}
  </>;
}
