"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Article = { id: number; title: string; source_namespace: string; ownership: string; created_at: string; chunk_count: number };
type ListResult = { items: Article[]; has_more: boolean };

export default function LibraryPage() {
  const [offset, setOffset] = useState(0);
  const [result, setResult] = useState<ListResult | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    setResult(null); setError("");
    api<ListResult>(`/documents?limit=20&offset=${offset}`, { signal: controller.signal })
      .then((value) => { if (!controller.signal.aborted) setResult(value); })
      .catch((cause) => { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : "加载失败。"); });
    return () => controller.abort();
  }, [offset]);

  return <main className="library">
    <div className="section-heading"><div><h1>文章列表</h1><p className="lead">保存下来的素材，随时回来查看。</p></div><Link className="button-link" href="/">上传文章</Link></div>
    {error ? <p className="error" role="alert">{error}</p> : !result ? <p role="status">正在加载文章……</p> : <>
      {result.items.length === 0 ? <div className="empty-state"><h2>这里还没有文章</h2><p>上传第一篇 Markdown，开始积累你的素材。</p><Link href="/">去上传</Link></div> :
        <ul className="article-list">{result.items.map((article) => <li key={article.id}>
          <h2><Link href={`/library/${article.id}`}>{article.title}</Link></h2>
          <dl className="article-meta"><div><dt>来源</dt><dd>{article.source_namespace}</dd></div><div><dt>归属</dt><dd>{article.ownership === "owned" ? "自己的文章" : "外部参考"}</dd></div><div><dt>分块</dt><dd>{article.chunk_count}</dd></div><div><dt>首次入库</dt><dd>{new Date(article.created_at).toLocaleString("zh-CN")}</dd></div></dl>
        </li>)}</ul>}
      <div className="pagination"><button disabled={offset === 0} onClick={() => setOffset(offset - 20)}>上一页</button><span>第 {offset / 20 + 1} 页</span><button disabled={!result.has_more} onClick={() => setOffset(offset + 20)}>下一页</button></div>
    </>}
  </main>;
}
