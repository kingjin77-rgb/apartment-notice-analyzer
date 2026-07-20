"use client";

import { useEffect, useState } from "react";
import { fetchStatus, type StatusResponse } from "@/lib/api";

const LABELS: { key: keyof StatusResponse; label: string; hint: string }[] = [
  { key: "claude_api", label: "Claude API", hint: "조항분해·독소조항 정확도" },
  { key: "law_go_kr", label: "국가법령정보", hint: "" },
  { key: "clova_ocr", label: "Clova OCR", hint: "스캔본 PDF" },
  { key: "kakao_local", label: "카카오 로컬", hint: "주변환경 조사" },
  { key: "neis", label: "NEIS", hint: "학군조사" },
];

export default function StatusBadges() {
  const [status, setStatus] = useState<StatusResponse | null>(null);

  useEffect(() => {
    fetchStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
  }, []);

  return (
    <div className="flex flex-wrap gap-2">
      {LABELS.map(({ key, label, hint }) => {
        const ok = status?.[key];
        return (
          <span
            key={key}
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[13px] font-medium ${
              ok
                ? "bg-accent-green/10 text-accent-green"
                : "bg-ink-faint/10 text-ink-muted"
            }`}
            title={hint}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-accent-green" : "bg-ink-faint"}`}
            />
            {label}
          </span>
        );
      })}
    </div>
  );
}
