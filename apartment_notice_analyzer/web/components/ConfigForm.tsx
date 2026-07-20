"use client";

import { useRef, useState } from "react";
import type { AnalyzeParams } from "@/lib/api";

type Props = {
  onSubmit: (params: AnalyzeParams) => void;
  loading: boolean;
};

function Checkbox({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <label className="flex cursor-pointer items-start gap-2.5 text-[15px] text-ink-secondary">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 h-4 w-4 shrink-0 accent-primary"
      />
      <span>{label}</span>
    </label>
  );
}

export default function ConfigForm({ onSubmit, loading }: Props) {
  const [complexName, setComplexName] = useState("○○아파트 (예시)");
  const [address, setAddress] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [useDummy, setUseDummy] = useState(true);
  const [runToxic, setRunToxic] = useState(true);
  const [runUnit, setRunUnit] = useState(true);
  const [runEnv, setRunEnv] = useState(false);
  const [runSchool, setRunSchool] = useState(false);
  const [runDisclosure, setRunDisclosure] = useState(true);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File | null) => {
    setFile(f);
    if (f) setUseDummy(false);
  };

  return (
    <form
      className="flex flex-col gap-5 rounded-xl border border-hairline bg-canvas p-6 shadow-soft"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          complexName,
          address,
          useDummy: useDummy || !file,
          runToxic,
          runUnit,
          runEnv,
          runSchool,
          runDisclosure,
          file,
        });
      }}
    >
      <div className="flex flex-col gap-1.5">
        <label className="text-[13px] font-medium text-ink-muted">단지명</label>
        <input
          value={complexName}
          onChange={(e) => setComplexName(e.target.value)}
          className="rounded-xs border border-hairline px-3 py-2 text-[15px] outline-none transition focus:border-primary focus:shadow-soft"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-[13px] font-medium text-ink-muted">
          주소 <span className="text-ink-faint">(주변환경/학군 조사용 — 비워두면 자동 추출 시도)</span>
        </label>
        <input
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="예: 경기도 화성시 동탄순환대로 127-5"
          className="rounded-xs border border-hairline px-3 py-2 text-[15px] outline-none transition focus:border-primary focus:shadow-soft"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-[13px] font-medium text-ink-muted">모집공고문 PDF 업로드</label>
        <div
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            const f = e.dataTransfer.files?.[0];
            if (f) handleFile(f);
          }}
          className={`flex cursor-pointer flex-col items-center gap-1 rounded-lg border border-dashed px-4 py-6 text-center transition ${
            dragOver ? "border-primary bg-primary/5" : "border-hairline bg-canvas-soft"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
          />
          <span className="text-[14px] font-medium text-ink">
            {file ? file.name : "클릭하거나 파일을 끌어다 놓으세요"}
          </span>
          <span className="text-[12px] text-ink-faint">PDF · 최대 200MB</span>
        </div>
      </div>

      <div className="flex flex-col gap-3 border-t border-hairline pt-4">
        <Checkbox checked={useDummy || !file} onChange={setUseDummy} label="PDF 없이 더미 샘플로 테스트" />
        <Checkbox checked={runToxic} onChange={setRunToxic} label="독소조항 1차 스크리닝 실행" />
        <Checkbox checked={runUnit} onChange={setRunUnit} label="동별/세대별 체크 실행" />
        <Checkbox checked={runEnv} onChange={setRunEnv} label="주변환경 조사 실행 (카카오 API 필요)" />
        <Checkbox checked={runSchool} onChange={setRunSchool} label="학군조사 실행 (카카오+NEIS API 필요)" />
        <Checkbox checked={runDisclosure} onChange={setRunDisclosure} label="사전고지 유의사항 추출 (입예협 개선요구용)" />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-1 self-start rounded-full bg-primary px-6 py-2.5 text-[15px] font-medium text-white shadow-soft transition hover:bg-primary-active active:scale-[0.97] disabled:opacity-50"
      >
        {loading ? "분석 중..." : "분석 시작"}
      </button>
    </form>
  );
}
