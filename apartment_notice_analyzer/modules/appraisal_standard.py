"""
감정평가 실무기준 (국토교통부 고시 제2023-522호) 파서

법제처 API의 행정규칙 본문은 줄바꿈이 전혀 없는 단일 문자열로 옵니다.
편(編)만 U+3000(전각 공백)으로 구분되고, 그 아래 절·항목 번호는 본문에 그대로 붙어 있습니다.

    　600 물건별 감정평가610 토지 및 그 정착물1 토지의 감정평가1.1 정의토지란 ...

이 모듈은 위 텍스트를 [610-3.1.3] 형태의 표준 인용부호로 조회 가능한 구조로 분해합니다.

    >>> std = AppraisalStandard.load()
    >>> std["610-3.1.3"].text
    '① 구분소유 부동산을 감정평가할 때에는 건물(전유부분과 공유부분)과 ...'

번호 뒤에 숫자가 섞인 본문("5년 이상", "제3조제3항")이 많아 단순 정규식으로는 오탐이 납니다.
따라서 후보를 뽑은 뒤 (1) 단위명사 블랙리스트 (2) 번호 시퀀스 연속성 두 단계로 걸러냅니다.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict

from .law_api import LawApiClient, KNOWN_IDS

# 실무기준 본문 캐시 위치 (API 호출 없이 재사용)
_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "appraisal_standard.json",
)

# 편 구분자: 법제처 응답에서 편 머리말 앞에만 전각 공백이 들어간다.
_PYEON_SEP = "　"

# 편/절 머리말: 3자리 번호 + 한글 제목.
# 제목 문자클래스에 숫자와 ①이 없으므로 greedy로 두어도 본문 앞에서 정확히 멈춘다.
_HEAD3 = re.compile(r"^([1-9]\d{2})\s*([가-힣][가-힣ㆍ·()\s]*)")
_JEOL = re.compile(r"([1-9]\d{2})\s*([가-힣][가-힣ㆍ·()\s]*)")

# 항목 번호: "3.1.3 구분소유..." 형태.
# 핵심은 번호와 제목 사이의 공백이다. 실제 항목 번호는 항상 공백을 두지만
# 본문의 수량 표현("5년", "제3조", "3방식")은 공백 없이 단위가 바로 붙는다.
# lookbehind는 숫자 내부에서 잘려 매칭되는 것만 막는다.
# ("다.2 기본적 사항" 처럼 마침표 뒤에 오는 진짜 헤더는 통과시켜야 한다.)
_ITEM = re.compile(r"(?<![0-9])(?<![0-9]\.)(?<!제)(\d+(?:\.\d+)*)[ \t]+(?=[가-힣(])")

# 본문이 시작됐음을 알리는 항 기호
_HANG = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"

# 제목만 있고 본문이 곧바로 이어지는 짧은 상용 제목
_COMMON_TITLES = (
    "정의", "목적", "적용범위", "용어의 정의",
    "자료의 수집 및 정리", "대상물건의 확인",
    "감정평가방법", "가치형성요인 비교",
    "지역요인 비교", "개별요인 비교",
    "사정보정", "시점수정", "면적사정",
)


@dataclass
class Section:
    """실무기준의 최소 인용 단위."""

    code: str          # 표준 인용부호. 예) "610-3.1.3"
    pyeon: str         # 편 번호. 예) "600"
    pyeon_title: str   # 편 이름. 예) "물건별 감정평가"
    jeol: str          # 절 번호. 예) "610" (절이 없는 편은 편 번호와 동일)
    jeol_title: str    # 절 이름. 예) "토지 및 그 정착물"
    number: str        # 절 내부 번호. 예) "3.1.3"
    title: str         # 항목 제목. 예) "구분소유 부동산의 감정평가방법"
    text: str          # 본문
    hang: list[str] = field(default_factory=list)  # ①②③ 단위로 쪼갠 항

    @property
    def full_text(self) -> str:
        return f"[{self.code}] {self.title}\n{self.text}"


def _num_tuple(s: str) -> tuple[int, ...]:
    return tuple(int(p) for p in s.split("."))


def _is_successor(cur: tuple[int, ...] | None, cand: tuple[int, ...]) -> bool:
    """cand가 cur 다음에 올 수 있는 항목 번호인지 판정."""
    if cur is None:
        # 절의 첫 항목은 반드시 1 또는 1.1 계열
        return all(p == 1 for p in cand)
    # 하위로 진입: 1.5 -> 1.5.1
    if len(cand) == len(cur) + 1 and cand[:-1] == cur and cand[-1] == 1:
        return True
    # 같은 레벨 또는 상위 레벨로 복귀하면서 +1
    for k in range(1, len(cand) + 1):
        if k > len(cur):
            break
        if cand[: k - 1] == cur[: k - 1] and cand[k - 1] == cur[k - 1] + 1 and len(cand) == k:
            return True
    return False


def _split_title_body(seg: str) -> tuple[str, str]:
    """'제목본문' 형태의 붙은 문자열을 분리."""
    # 1) 항 기호가 있으면 그 앞이 제목
    for i, ch in enumerate(seg):
        if ch in _HANG:
            if i <= 40:
                return seg[:i].strip(), seg[i:].strip()
            break
    # 2) 상용 제목으로 시작하면 그것을 제목으로
    for t in sorted(_COMMON_TITLES, key=len, reverse=True):
        if seg.startswith(t):
            return t, seg[len(t):].strip()
    # 3) 제목이 본문 첫머리에 반복되는 형태 ("사정보정" + "사정보정은 ...")
    for k in range(2, min(31, len(seg) // 2 + 1)):
        if seg[k : k + k] == seg[:k]:
            return seg[:k].strip(), seg[k:].strip()
    # 4) 분리 실패 - 전체를 본문으로 두고 제목은 비움
    return "", seg.strip()


def _split_hang(text: str) -> list[str]:
    """본문을 ①②③ 단위로 분해. 항 기호가 없으면 통째로 1건."""
    idxs = [i for i, ch in enumerate(text) if ch in _HANG]
    if not idxs:
        return [text] if text else []
    out = []
    if idxs[0] > 0:
        out.append(text[: idxs[0]].strip())
    for a, b in zip(idxs, idxs[1:] + [len(text)]):
        out.append(text[a:b].strip())
    return [s for s in out if s]


def parse(raw: str) -> list[Section]:
    """실무기준 본문 문자열을 Section 목록으로 분해."""
    sections: list[Section] = []

    for block in raw.split(_PYEON_SEP):
        block = block.strip()
        if not block:
            continue
        m = _HEAD3.match(block)
        if not m:
            continue
        pyeon, pyeon_title = m.group(1), m.group(2).strip()
        rest = block[m.end():]

        # 편 아래에 절(610, 710, 810 ...)이 있는지 확인해 절 단위로 자른다.
        # 절 번호는 편 번호와 백의 자리가 같고 편 번호 자신은 아니다.
        jeol_heads = [
            mm for mm in _JEOL.finditer(rest)
            if mm.group(1)[0] == pyeon[0] and mm.group(1) != pyeon
        ]
        if jeol_heads:
            chunks = []
            for i, mm in enumerate(jeol_heads):
                end = jeol_heads[i + 1].start() if i + 1 < len(jeol_heads) else len(rest)
                chunks.append((mm.group(1), mm.group(2).strip(), rest[mm.end():end]))
        else:
            chunks = [(pyeon, pyeon_title, rest)]

        for jeol, jeol_title, body in chunks:
            sections.extend(
                _parse_jeol(pyeon, pyeon_title, jeol, jeol_title, body)
            )

    return sections


def _parse_jeol(pyeon, pyeon_title, jeol, jeol_title, body) -> list[Section]:
    """절 본문에서 항목 번호를 추출해 Section으로 만든다."""
    accepted: list[tuple[int, int, str]] = []  # (start, end_of_number, number)
    cur: tuple[int, ...] | None = None

    for m in _ITEM.finditer(body):
        num = m.group(1)
        cand = _num_tuple(num)
        if not _is_successor(cur, cand):
            continue
        accepted.append((m.start(), m.end(), num))
        cur = cand

    # 번호 없이 항(①②③)만으로 구성된 절은 통째로 한 건으로 담는다. 예) 710 담보평가
    if not accepted:
        text = body.strip()
        if not text:
            return []
        return [
            Section(
                code=jeol, pyeon=pyeon, pyeon_title=pyeon_title,
                jeol=jeol, jeol_title=jeol_title, number="",
                title=jeol_title, text=text, hang=_split_hang(text),
            )
        ]

    out: list[Section] = []
    for i, (start, num_end, num) in enumerate(accepted):
        end = accepted[i + 1][0] if i + 1 < len(accepted) else len(body)
        seg = body[num_end:end].strip()
        title, text = _split_title_body(seg)
        out.append(
            Section(
                code=f"{jeol}-{num}",
                pyeon=pyeon,
                pyeon_title=pyeon_title,
                jeol=jeol,
                jeol_title=jeol_title,
                number=num,
                title=title,
                text=text,
                hang=_split_hang(text),
            )
        )
    return out


class AppraisalStandard:
    """파싱된 실무기준에 대한 조회 인터페이스."""

    def __init__(self, sections: list[Section], meta: dict | None = None):
        self.sections = sections
        self.meta = meta or {}
        self._by_code = {s.code: s for s in sections}

    # -- 생성 ---------------------------------------------------------
    @classmethod
    def load(cls, use_cache: bool = True, cache_path: str = _CACHE_PATH) -> "AppraisalStandard":
        """캐시가 있으면 캐시에서, 없으면 법제처 API에서 받아 파싱하고 캐시에 저장."""
        if use_cache and os.path.exists(cache_path):
            with open(cache_path, encoding="utf-8") as f:
                blob = json.load(f)
            return cls([Section(**s) for s in blob["sections"]], blob.get("meta"))
        return cls.fetch(cache_path=cache_path if use_cache else None)

    @classmethod
    def fetch(cls, client: LawApiClient | None = None, cache_path: str | None = _CACHE_PATH) -> "AppraisalStandard":
        """법제처 API에서 실무기준 본문을 받아 파싱."""
        client = client or LawApiClient()
        if not client.is_configured:
            raise RuntimeError("LAW_GO_KR_OC 미설정 - .env를 확인하세요.")
        rule_id = KNOWN_IDS["감정평가 실무기준"]["id"]
        data = client.get_admin_rule(rule_id)
        raw = data.get("조문내용", "")
        if not raw:
            raise RuntimeError(f"실무기준 본문이 비어 있습니다. 응답 키: {list(data)}")
        info = data.get("행정규칙기본정보", {})
        meta = {
            "행정규칙명": info.get("행정규칙명"),
            "발령번호": info.get("발령번호"),
            "시행일자": info.get("시행일자"),
            "행정규칙일련번호": rule_id,
            "원문길이": len(raw),
        }
        obj = cls(parse(raw), meta)
        if cache_path:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"meta": meta, "sections": [asdict(s) for s in obj.sections]},
                    f, ensure_ascii=False, indent=1,
                )
        return obj

    # -- 조회 ---------------------------------------------------------
    def __len__(self) -> int:
        return len(self.sections)

    def __getitem__(self, code: str) -> Section:
        return self._by_code[code]

    def get(self, code: str) -> Section | None:
        return self._by_code.get(code)

    def search(self, keyword: str, limit: int = 20) -> list[Section]:
        """제목·본문에서 키워드를 포함하는 조항 검색."""
        hits = [s for s in self.sections if keyword in s.title or keyword in s.text]
        return hits[:limit]

    def in_jeol(self, jeol: str) -> list[Section]:
        return [s for s in self.sections if s.jeol == jeol]

    def cite(self, code: str) -> str:
        """보고서에 넣을 인용 문자열 생성."""
        s = self._by_code.get(code)
        if s is None:
            return f"[{code}] (조항 없음)"
        head = f"[{code}]"
        if s.title:
            head += f" {s.title}"
        return f"{head}\n{s.text}"


# AVM 파이프라인이 근거로 삼는 핵심 조항 (보고서·화면 각주에 그대로 사용)
KEY_SECTIONS = {
    "구분소유_주방식": "610-3.1.3",   # 아파트는 거래사례비교법 + 층별·위치별 효용 반영
    "구분소유_정의": "610-3.1.1",
    "거래사례비교법_정의": "400-3.3.1.1",
    "사례선택": "400-3.3.1.2",
    "사정보정": "400-3.3.1.3",
    "시점수정": "400-3.3.1.4",
    "가치형성요인비교": "400-3.3.1.5",
    "시산가액조정": "400-4",
}
