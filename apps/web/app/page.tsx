"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

type ImportResult = {
  status: "imported" | "duplicate" | "updated";
  article_id: number;
  chunk_count: number;
};

const STAMPS: Record<ImportResult["status"], { label: string; note: string; tone: string }> = {
  imported: { label: "新入库", note: "这篇文章已经写入素材库。", tone: "new" },
  duplicate: { label: "已在库中", note: "同一篇文章再次放入，没有新建记录。", tone: "same" },
  updated: { label: "已更新", note: "文章和分块已替换为本次上传的内容。", tone: "same" },
};

function isImportResult(value: unknown): value is ImportResult {
  if (!value || typeof value !== "object") return false;
  const result = value as Partial<ImportResult>;
  return (
    (result.status === "imported" || result.status === "duplicate" || result.status === "updated") &&
    typeof result.article_id === "number" &&
    typeof result.chunk_count === "number"
  );
}

function errorMessage(status: number, payload: unknown) {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  }
  if (status === 422) return "请求缺少必填内容。";
  if (status === 401) return "登录已过期，请重新登录。";
  if (status === 403) return "当前账号无权执行此操作。";
  if (status === 503) return "数据库未配置或暂时连不上。";
  if (status === 500) return "入库失败。";
  return "入库没有完成。";
}

export default function UploadPage() {
  const [source, setSource] = useState("");
  const [ownership, setOwnership] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ImportResult | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    const sourceNamespace = source.trim();
    if (!sourceNamespace) {
      setError("请填写来源集合。");
      return;
    }
    if (ownership !== "owned" && ownership !== "reference") {
      setError("请选择这篇文章的归属。");
      return;
    }
    if (!file) {
      setError("请选择一篇 Markdown。");
      return;
    }
    if (!/\.(md|markdown)$/i.test(file.name)) {
      setError("请选择扩展名为 .md 或 .markdown 的文件。");
      return;
    }

    setPending(true);
    try {
      const response = await fetch("/backend/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw: await file.text(),
          source_namespace: sourceNamespace,
          ownership,
          source_path: file.name,
        }),
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        if (response.status === 401) { window.location.assign("/login"); return; }
        setError(errorMessage(response.status, payload));
        return;
      }
      if (!isImportResult(payload)) {
        setError("服务返回了无法识别的结果。");
        return;
      }
      setResult(payload);
    } catch {
      setError("暂时无法连接服务，请稍后重试。");
    } finally {
      setPending(false);
    }
  }

  const stamp = result ? STAMPS[result.status] : null;

  return (
    <main className="desk">
      <section>
        <h1>素材入库</h1>
        <p className="lead">选择一篇 Markdown。相同内容会跳过；同一来源和文章标识的内容变化时，将覆盖原文和全部分块。</p>
        <form onSubmit={onSubmit} aria-busy={pending}>
          <div className="field">
            <label htmlFor="source">来源集合</label>
            <input
              id="source"
              name="source"
              type="text"
              value={source}
              onChange={(event) => setSource(event.target.value)}
              autoComplete="off"
            />
            <p className="hint">用来区分这批文章从哪里来，例如自己的博客或某一组外部资料。</p>
          </div>
          <fieldset>
            <legend>归属</legend>
            <div className="choices">
              <label>
                <input
                  type="radio"
                  name="ownership"
                  value="owned"
                  checked={ownership === "owned"}
                  onChange={() => setOwnership("owned")}
                />
                自己的文章
              </label>
              <label>
                <input
                  type="radio"
                  name="ownership"
                  value="reference"
                  checked={ownership === "reference"}
                  onChange={() => setOwnership("reference")}
                />
                外部参考
              </label>
            </div>
          </fieldset>
          <div className="field">
            <label htmlFor="article">Markdown 文件</label>
            <input
              id="article"
              name="article"
              type="file"
              accept=".md,.markdown,text/markdown"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </div>
          <button type="submit" disabled={pending}>{pending ? "正在入库" : "放入素材库"}</button>
        </form>
      </section>
      <aside className="slip" aria-live="polite">
        {stamp && result ? (
          <>
            <span className={`stamp ${stamp.tone}`}>{stamp.label}</span>
            <p>{stamp.note}</p>
            <p className="meta">文章编号 {result.article_id}，分块 {result.chunk_count}</p>
            <p><Link href={`/library/${result.article_id}`}>查看文章详情</Link></p>
          </>
        ) : error ? (
          <p className="error">{error}</p>
        ) : (
          <p>入库之后，这里会显示新入库、已在库中，或已更新。</p>
        )}
      </aside>
    </main>
  );
}
