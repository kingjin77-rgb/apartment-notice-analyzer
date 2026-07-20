"use client";

import { useState } from "react";
import StatusBadges from "@/components/StatusBadges";
import ConfigForm from "@/components/ConfigForm";
import ResultsView from "@/components/ResultsView";
import { analyze, type AnalyzeParams, type AnalyzeResponse } from "@/lib/api";

export default function Home() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (params: AnalyzeParams) => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyze(params);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "알 수 없는 오류");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <header className="flex flex-col gap-3">
        <h1 className="text-[40px] font-bold leading-tight tracking-heading1 text-ink">
          아파트 모집공고문 분석 프로그램
        </h1>
        <StatusBadges />
      </header>

      <div className="grid gap-8 lg:grid-cols-[380px_1fr] lg:items-start">
        <div className="lg:sticky lg:top-8">
          <ConfigForm onSubmit={handleSubmit} loading={loading} />
        </div>

        <div className="flex flex-col gap-6">
          {error && (
            <div className="rounded-lg border-l-[3px] border-accent-pink bg-accent-pink/5 px-4 py-3 text-[14px] text-ink shadow-soft">
              {error}
            </div>
          )}
          {loading && (
            <div className="flex items-center gap-3 rounded-xl border border-hairline bg-canvas p-6 text-[15px] text-ink-muted shadow-soft">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              분석 중...
            </div>
          )}
          {!loading && !result && !error && (
            <div className="rounded-xl border border-dashed border-hairline bg-canvas/50 p-10 text-center text-[15px] text-ink-faint">
              왼쪽에서 설정 후 &ldquo;분석 시작&rdquo;을 눌러주세요.
            </div>
          )}
          {result && <ResultsView result={result} />}
        </div>
      </div>
    </main>
  );
}
