"""
Claude API 예상 비용 계산기.

section_splitter.py / toxic_clause.py 가 실제로 보내는 system prompt를 그대로 재현해서
count_tokens로 정확한 입력 토큰 수를 재고, sonnet-4-6 단가로 비용을 추정한다.

사용법:
    python estimate_cost.py                       # data/sample_notice.txt 사용
    python estimate_cost.py path/to/notice.txt     # 다른 텍스트 파일 사용
"""
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
INPUT_PRICE_PER_MTOK = 3.00
OUTPUT_PRICE_PER_MTOK = 15.00

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_law_mapping() -> dict:
    with open(os.path.join(DATA_DIR, "law_mapping.json"), encoding="utf-8") as f:
        return json.load(f)


def load_reference() -> dict:
    with open(os.path.join(DATA_DIR, "standard_contract_reference.json"), encoding="utf-8") as f:
        return json.load(f)


def build_split_prompt(notice_text: str) -> tuple[str, str]:
    mapping = load_law_mapping()
    category_names = [c["category"] for c in mapping["categories"]]
    system_prompt = (
        "너는 아파트 모집공고문을 분석하는 법무 보조 도구다. "
        "입력된 공고문 텍스트를 조항 단위로 나누고, 각 조항이 다음 카테고리 중 "
        f"어디에 해당하는지 분류하라: {category_names}. "
        "해당사항 없으면 빈 리스트. 반드시 JSON 배열만 출력하라. "
        '형식: [{"text": "...", "categories": ["..."]}]'
    )
    return system_prompt, notice_text


def build_toxic_prompt(notice_text: str) -> tuple[str, str]:
    ref = load_reference()
    system_prompt = (
        "너는 아파트 공급계약 조항의 독소조항 여부를 1차 스크리닝하는 법무 보조 도구다. "
        "아래 표준 조항 요약을 기준선으로 삼아, 입력된 공고문 조항이 수분양자에게 "
        "비정상적으로 불리한지 판단하라. 반드시 JSON 배열만 출력. "
        '형식: [{"text": "...", "risk_level": "낮음|검토 필요|높음", "reason": "..."}] '
        "risk_level은 반드시 이 최종 판단이 아니라 1차 스크리닝임을 전제로 신중하게 판정하라. "
        f"표준 조항 기준선: {json.dumps(ref['standard_clauses'], ensure_ascii=False)}"
    )
    # 실제로는 split 단계에서 추출된 조항 리스트가 들어가지만,
    # 비용 추정 목적으로는 전체 문서 텍스트를 그대로 넣어 상한선을 잡는다.
    return system_prompt, notice_text


def cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1_000_000) * INPUT_PRICE_PER_MTOK + (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MTOK


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY 미설정 — .env에 키 넣고 다시 실행")
        sys.exit(1)

    import anthropic

    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA_DIR, "sample_notice.txt")
    with open(path, encoding="utf-8") as f:
        notice_text = f.read()

    client = anthropic.Anthropic(api_key=api_key)

    print(f"입력 파일: {path} ({len(notice_text)}자)\n")

    total_input_tokens = 0
    # max_tokens은 두 호출 모두 4000으로 상한 잡혀있음 — 실제 출력은 보통 이보다 적지만
    # 여기서는 상한선 비용을 보여주기 위해 max_tokens를 출력 토큰으로 가정
    assumed_output_tokens = 4000

    for label, builder in [("1) split_sections (조항 분해)", build_split_prompt),
                            ("2) analyze_toxic_clauses (독소조항 스크리닝)", build_toxic_prompt)]:
        system_prompt, user_content = builder(notice_text)
        result = client.messages.count_tokens(
            model=MODEL,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        input_tokens = result.input_tokens
        total_input_tokens += input_tokens
        c = cost(input_tokens, assumed_output_tokens)
        print(f"{label}")
        print(f"  입력 토큰: {input_tokens:,}")
        print(f"  가정 출력 토큰(상한): {assumed_output_tokens:,}")
        print(f"  예상 비용(상한): ${c:.4f}\n")

    total_cost_upper = cost(total_input_tokens, assumed_output_tokens * 2)
    print(f"--- 전체 (분석 1회 기준, 상한선) ---")
    print(f"총 입력 토큰: {total_input_tokens:,}")
    print(f"예상 비용(상한): ${total_cost_upper:.4f}")
    print("(실제 출력은 max_tokens보다 보통 훨씬 적으니 실비용은 이보다 낮음)")


if __name__ == "__main__":
    main()
