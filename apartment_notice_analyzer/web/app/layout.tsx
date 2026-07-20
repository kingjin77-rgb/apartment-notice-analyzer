import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "모집공고문 분석",
  description: "아파트 모집공고문 자동 검수 · 독소조항 스크리닝",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
