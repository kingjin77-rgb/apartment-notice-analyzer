const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type StatusResponse = {
  claude_api: boolean;
  law_go_kr: boolean;
  clova_ocr: boolean;
  kakao_local: boolean;
  neis: boolean;
};

export type MatchedSection = { text: string; categories: string[] };
export type ToxicResult = { text: string; risk_level: string; reason: string };
export type LoanNotice = { date: string; text: string } | null;
export type DisclosureItem = {
  category: string;
  page: number;
  text: string;
  has_waiver_phrase: boolean;
};
export type DisclosureGroup = { category: string; items: DisclosureItem[] };

export type AnalyzeResponse = {
  used_dummy: boolean;
  address: string;
  notice_text: string;
  loan_notice: LoanNotice;
  matched_sections: MatchedSection[];
  toxic_results: ToxicResult[] | null;
  unit_rows: Record<string, unknown>[] | null;
  supply_summary: Record<string, unknown> | null;
  environment_survey: Record<string, unknown> | null;
  school_report: Record<string, unknown> | null;
  disclosure_grouped: DisclosureGroup[];
  errors: Record<string, string>;
  report_id: string | null;
  complex_name: string;
};

export async function fetchStatus(): Promise<StatusResponse> {
  const res = await fetch(`${API_URL}/api/status`);
  if (!res.ok) throw new Error("상태 조회 실패");
  return res.json();
}

export type AnalyzeParams = {
  complexName: string;
  address: string;
  useDummy: boolean;
  runToxic: boolean;
  runUnit: boolean;
  runEnv: boolean;
  runSchool: boolean;
  runDisclosure: boolean;
  file: File | null;
};

export async function analyze(params: AnalyzeParams): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.set("complex_name", params.complexName);
  form.set("address", params.address);
  form.set("use_dummy", String(params.useDummy));
  form.set("run_toxic", String(params.runToxic));
  form.set("run_unit", String(params.runUnit));
  form.set("run_env", String(params.runEnv));
  form.set("run_school", String(params.runSchool));
  form.set("run_disclosure", String(params.runDisclosure));
  if (params.file) form.set("file", params.file);

  const res = await fetch(`${API_URL}/api/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`분석 요청 실패 (${res.status})`);
  return res.json();
}

export function reportDownloadUrl(reportId: string, complexName: string): string {
  const params = new URLSearchParams({ complex_name: complexName });
  return `${API_URL}/api/report/${reportId}?${params.toString()}`;
}
