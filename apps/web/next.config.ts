import path from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The dev server otherwise blocks assets requested from 127.0.0.1.
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    root: path.dirname(fileURLToPath(import.meta.url)),
  },
  async rewrites() {
    const api = (process.env.API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
    return [{ source: "/backend/:path*", destination: `${api}/:path*` }];
  },
};

export default nextConfig;
