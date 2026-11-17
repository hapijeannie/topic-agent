import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import AuthGate from "./components/AuthGate";

export const metadata: Metadata = {
  title: "个人素材库",
  description: "积累文章，查看原文与分块",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body><AuthGate>{children}</AuthGate></body>
    </html>
  );
}
