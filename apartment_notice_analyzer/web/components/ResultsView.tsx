"use client";

import { useState } from "react";
import type { AnalyzeResponse } from "@/lib/api";
import { reportDownloadUrl } from "@/lib/api";

function SectionTitle({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <h2 className="text-[22px] font-bold tracking-heading2 text-ink">
      {n}. {children}
    </h2>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="rounded-lg border-l-[3px] border-accent-pink bg-accent-pink/5 px-4 py-3 text-[14px] text-ink shadow-soft">
      기능 실행 중 오류 — 건너뜁니다: {message}
    </div>
  );
}

function InfoBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border-l-[3px] border-accent-sky bg-accent-sky/10 px-4 py-3 text-[14px] text-ink shadow-soft">
      {children}
    </div>
  );
}

function SuccessBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border-l-[3px] border-accent-green bg-accent-green/10 px-4 py-3 text-[14px] text-ink shadow-soft">
      {children}
    </div>
  );
}

function WarningBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border-l-[3px] border-accent-orange bg-accent-orange/10 px-4 py-3 text-[14px] text-ink shadow-soft">
      {children}
    </div>
  );
}

function DataTable({ rows }: { rows: Record<string, unknown>[] }) {
  if (!rows.length) return null;
  const cols = Object.keys(rows[0]);
  return (
    <div className="overflow-x-auto rounded-lg border border-hairline">
      <table className="w-full text-left text-[14px]">
        <thead>
          <tr className="bg-canvas-soft">
            {cols.map((c) => (
              <th
                key={c}
                className="whitespace-nowrap border-b border-hairline px-3 py-2 text-[12px] font-semibold uppercase tracking-wide text-ink-muted"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-hairline last:border-0">
              {cols.map((c) => (
                <td key={c} className="whitespace-nowrap px-3 py-2 text-ink-secondary">
                  {String(row[c] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Accordion({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="overflow-hidden rounded-lg border border-hairline bg-canvas">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left text-[15px] font-semibold text-ink"
      >
        {title}
        <span className={`transition-transform ${open ? "rotate-90" : ""}`}>›</span>
      </button>
      {open && <div className="border-t border-hairline px-4 py-3">{children}</div>}
    </div>
  );
}

export default function ResultsView({ result }: { result: AnalyzeResponse }) {
  const flaggedToxic = (result.toxic_results ?? []).filter((r) =>
    ["검토 필요", "높음"].includes(r.risk_level)
  );

  return (
    <div className="flex flex-col gap-6">
      {result.used_dummy && (
        <InfoBanner>더미 샘플 데이터로 분석합니다 (실제 공고문 아님).</InfoBanner>
      )}

      {result.address && (
        <p className="text-[13px] text-ink-faint">📍 조사 대상 주소: {result.address}</p>
      )}

      <Accordion title="추출된 원문 텍스트">
        <pre className="max-h-80 overflow-y-auto whitespace-pre-wrap text-[13px] text-ink-secondary">
          {result.notice_text}
        </pre>
      </Accordion>

      {result.loan_notice && (
        <WarningBanner>
          <strong>대출규제 적용 기준일: {result.loan_notice.date}</strong>
          <br />
          {result.loan_notice.text}
        </WarningBanner>
      )}

      <section className="flex flex-col gap-3">
        <SectionTitle n={1}>조항별 법령 대조 결과</SectionTitle>
        {result.errors.sections && <ErrorBanner message={result.errors.sections} />}
        <div className="grid gap-3 sm:grid-cols-2">
          {result.matched_sections.map((item, i) => (
            <div key={i} className="rounded-lg border border-hairline bg-canvas p-4 shadow-soft">
              <p className="text-[15px] text-ink">{item.text}</p>
              <p className="mt-2 text-[13px] text-ink-faint">
                관련 카테고리: {item.categories.length ? item.categories.join(", ") : "없음"}
              </p>
            </div>
          ))}
        </div>
      </section>

      {result.toxic_results !== null && (
        <section className="flex flex-col gap-3">
          <SectionTitle n={2}>독소조항 1차 스크리닝</SectionTitle>
          <p className="text-[13px] text-ink-faint">⚠️ 최종 법률 판단 아님 — 변호사 검토 필요</p>
          {result.errors.toxic && <ErrorBanner message={result.errors.toxic} />}
          {flaggedToxic.length === 0 ? (
            <SuccessBanner>자동 기준으로 특이사항 없음</SuccessBanner>
          ) : (
            flaggedToxic.map((r, i) => (
              <WarningBanner key={i}>
                <strong>{r.risk_level}</strong> — {r.text}
                <br />
                {r.reason}
              </WarningBanner>
            ))
          )}
        </section>
      )}

      {result.unit_rows !== null && (
        <section className="flex flex-col gap-3">
          <SectionTitle n={3}>동별/세대별 체크 (타입별 공급금액)</SectionTitle>
          {result.errors.unit && <ErrorBanner message={result.errors.unit} />}
          {result.unit_rows.length ? (
            <DataTable rows={result.unit_rows} />
          ) : (
            <InfoBanner>공급금액표 구조를 찾지 못했습니다. 이 문서는 다른 표 양식을 사용할 수 있습니다.</InfoBanner>
          )}
        </section>
      )}

      {(result.environment_survey || result.errors.environment) && (
        <section className="flex flex-col gap-3">
          <SectionTitle n={4}>주변환경 조사</SectionTitle>
          {result.errors.environment && <ErrorBanner message={result.errors.environment} />}
          {result.environment_survey && (
            <pre className="overflow-x-auto rounded-lg border border-hairline bg-canvas-soft p-4 text-[12px]">
              {JSON.stringify(result.environment_survey, null, 2)}
            </pre>
          )}
        </section>
      )}

      {(result.school_report || result.errors.school) && (
        <section className="flex flex-col gap-3">
          <SectionTitle n={5}>학군조사</SectionTitle>
          {result.errors.school && <ErrorBanner message={result.errors.school} />}
          {result.school_report && (
            <>
              <p className="text-[13px] text-ink-faint">
                {String(result.school_report.disclaimer ?? "")}
              </p>
              {Array.isArray(result.school_report.nearby_schools) && (
                <DataTable rows={result.school_report.nearby_schools as Record<string, unknown>[]} />
              )}
            </>
          )}
        </section>
      )}

      {result.disclosure_grouped.length > 0 && (
        <section className="flex flex-col gap-3">
          <SectionTitle n={6}>사전고지 유의사항 (입예협 개선요구용)</SectionTitle>
          <p className="text-[13px] text-ink-faint">
            공고문에 명시되어 있지만 놓치기 쉬운 환경권·생활불편 관련 조항 — 입주 전 입예협 차원 개선요구 검토용
          </p>
          {result.errors.disclosure && <ErrorBanner message={result.errors.disclosure} />}
          {result.disclosure_grouped.map((group) => (
            <Accordion key={group.category} title={`${group.category} (${group.items.length}건)`}>
              <div className="flex flex-col gap-2">
                {group.items.map((it, i) => (
                  <p key={i} className="text-[14px] text-ink-secondary">
                    p.{it.page} — {it.text}
                    {it.has_waiver_phrase && (
                      <span className="ml-1 text-accent-orange">⚠️이의제기불가 문구 포함</span>
                    )}
                  </p>
                ))}
              </div>
            </Accordion>
          ))}
        </section>
      )}

      {result.errors.report && <ErrorBanner message={result.errors.report} />}

      {result.report_id && (
        <a
          href={reportDownloadUrl(result.report_id, result.complex_name)}
          className="self-start rounded-full border border-hairline bg-canvas px-6 py-2.5 text-[15px] font-medium text-ink shadow-soft transition hover:bg-canvas-soft active:scale-[0.97]"
        >
          입주민 배포용 검수 리포트(docx) 다운로드
        </a>
      )}
    </div>
  );
}
