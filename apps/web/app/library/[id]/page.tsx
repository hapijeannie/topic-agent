"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";

type Article = { id: number; title: string; source_namespace: string; source_id: string; ownership: string; source_path: string; body: string; created_at: string; chunks: { index: number; text: string }[] };

export default function ArticlePage() {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    setArticle(null); setError("");
    api<Article>(`/documents/${encodeURIComponent(id)}`, { signal: controller.signal })
      .then((value) => { if (!controller.signal.aborted) setArticle(value); })
      .catch((cause) => { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : "加载失败。"); });
    return () => controller.abort();
  }, [id]);
  return <main className="library article-detail">
    <Link href="/library">返回文章列表</Link>
    {error ? <p className="error" role="alert">{error}</p> : !article ? <p role="status">正在加载文章……</p> : <>
      <h1>{article.title}</h1>
      <dl className="article-meta"><div><dt>来源</dt><dd>{article.source_namespace}</dd></div><div><dt>文章标识</dt><dd>{article.source_id}</dd></div><div><dt>归属</dt><dd>{article.ownership === "owned" ? "自己的文章" : "外部参考"}</dd></div><div><dt>文件</dt><dd>{article.source_path}</dd></div><div><dt>首次入库</dt><dd>{new Date(article.created_at).toLocaleString("zh-CN")}</dd></div></dl>
      <section><h2>正文</h2><pre className="article-body">{article.body}</pre></section>
      <section><h2>分块（{article.chunks.length}）</h2>{article.chunks.map((chunk) => <details key={chunk.index}><summary>第 {chunk.index + 1} 块</summary><pre className="article-body">{chunk.text}</pre></details>)}</section>
    </>}
  </main>;
}
