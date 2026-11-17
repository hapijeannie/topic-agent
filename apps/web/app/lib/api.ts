export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/backend${path}`, { ...init, cache: "no-store" });
  if (response.status === 401) {
    window.location.assign("/login");
    throw new Error("登录已过期，请重新登录。");
  }
  if (!response.ok) {
    const messages: Record<number, string> = {
      403: "当前账号无权访问。", 404: "文章不存在。",
      503: "服务暂不可用，请稍后重试。",
    };
    throw new Error(messages[response.status] ?? "请求失败，请稍后重试。");
  }
  return response.json();
}
