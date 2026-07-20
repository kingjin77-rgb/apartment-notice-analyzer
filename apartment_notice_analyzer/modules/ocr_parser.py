"""
모집공고문 PDF -> 텍스트 추출

우선순위:
1. PyMuPDF로 텍스트 레이어 직접 추출 (텍스트 기반 PDF인 경우, 빠르고 정확)
2. 텍스트 추출 실패 시 (스캔본/이미지 PDF) -> Clova OCR
3. Clova OCR 미설정/실패 시 -> 더미 텍스트 반환 (개발/데모용)

실사용 시 CLOVA_OCR_API_URL / CLOVA_OCR_SECRET_KEY .env에 채워 넣으면
등기자동화 프로그램과 동일한 방식으로 동작합니다.
"""
import os
import base64
import uuid
import json
import requests

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_text_pymupdf(pdf_bytes: bytes) -> str:
    """텍스트 기반 PDF에서 직접 텍스트 레이어 추출."""
    if fitz is None:
        return ""
    text_chunks = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    return "\n".join(text_chunks).strip()


def extract_text_clova_ocr(pdf_bytes: bytes) -> str:
    """스캔본 PDF -> Clova OCR API 호출 (키 없으면 빈 문자열 반환)."""
    api_url = os.getenv("CLOVA_OCR_API_URL")
    secret_key = os.getenv("CLOVA_OCR_SECRET_KEY")
    if not api_url or not secret_key:
        return ""

    request_json = {
        "images": [{"format": "pdf", "name": "notice"}],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": 0,
    }
    payload = {"message": json.dumps(request_json).encode("UTF-8")}
    files = [("file", ("notice.pdf", pdf_bytes, "application/pdf"))]
    headers = {"X-OCR-SECRET": secret_key}

    try:
        resp = requests.post(api_url, headers=headers, data=payload, files=files, timeout=60)
        resp.raise_for_status()
        result = resp.json()
    except Exception:
        return ""

    lines = []
    for image in result.get("images", []):
        for field in image.get("fields", []):
            lines.append(field.get("inferText", ""))
    return "\n".join(lines)


def extract_text(pdf_bytes: bytes | None, dummy_text: str = "") -> str:
    """공고문 텍스트 추출 진입점. pdf_bytes가 None이면 더미 텍스트 사용(데모 모드)."""
    if pdf_bytes is None:
        return dummy_text

    text = extract_text_pymupdf(pdf_bytes)
    if text:
        return text

    text = extract_text_clova_ocr(pdf_bytes)
    if text:
        return text

    # 둘 다 실패 -> 데모 안내
    return "[텍스트 추출 실패: 스캔본이며 Clova OCR 키 미설정 상태입니다. .env를 확인하세요.]"
