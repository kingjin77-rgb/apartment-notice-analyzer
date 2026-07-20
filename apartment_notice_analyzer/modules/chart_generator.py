"""
공고문에서 파싱한 실제 데이터로 차트 생성 (matplotlib).

부동산지인 등에서 보는 시세비교/실거래가 그래프와 달리, 여기서는
공고문 자체에 명시된 데이터(공급세대수, 특별공급 breakdown, 타입별 분양가,
층별 분양가)만 사용합니다 — 외부 시세 API 없이도 100% 정확한 데이터입니다.
인근 시세·실거래가 비교는 market_analysis.py(국토교통부 실거래가 API) 참고.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Noto Sans CJK JP"  # 한글 렌더링 (Noto CJK가 한글도 포함)
plt.rcParams["axes.unicode_minus"] = False

COLOR_PRIMARY = "#2E5EAA"
COLOR_ACCENT = "#E8743B"


def _clean_int(value: str) -> int:
    return int(str(value).replace(",", "").replace("-", "0") or 0)


def chart_special_supply_breakdown(summary: dict, output_path: str) -> str:
    """특별공급 유형별 세대수 바 차트."""
    labels = ["기관추천", "다자녀가구", "신혼부부", "노부모부양", "생애최초", "신생아"]
    values = [_clean_int(summary.get(l, 0)) for l in labels]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(labels, values, color=COLOR_PRIMARY)
    ax.set_title("특별공급 유형별 공급세대수", fontsize=13, fontweight="bold")
    ax.set_ylabel("세대수")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, str(v), ha="center", fontsize=9)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def chart_special_vs_general(summary: dict, output_path: str) -> str:
    """특별공급 vs 일반공급 비중 파이 차트."""
    special = _clean_int(summary.get("특별공급계", 0))
    general = _clean_int(summary.get("일반공급세대수", 0))

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        [special, general],
        labels=[f"특별공급\n{special}세대", f"일반공급\n{general}세대"],
        autopct="%1.1f%%",
        colors=[COLOR_PRIMARY, COLOR_ACCENT],
        startangle=90,
        textprops={"fontsize": 10},
    )
    ax.set_title("특별공급 vs 일반공급 비중", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def chart_units_by_type(price_rows: list[dict], output_path: str) -> str:
    """타입별 공급세대수 바 차트 (공급금액표 파싱 결과 집계)."""
    from collections import defaultdict
    totals = defaultdict(int)
    for row in price_rows:
        totals[row["타입"]] += _clean_int(row["세대수"])

    types = list(totals.keys())
    values = [totals[t] for t in types]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(types, values, color=COLOR_PRIMARY)
    ax.set_title("타입별 공급세대수", fontsize=13, fontweight="bold")
    ax.set_ylabel("세대수")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3, str(v), ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def chart_avg_price_by_type(price_rows: list[dict], output_path: str) -> str:
    """타입별 평균 공급금액(공급가) 바 차트, 억 단위."""
    from collections import defaultdict
    sums = defaultdict(float)
    counts = defaultdict(int)
    for row in price_rows:
        amt = _clean_int(row["공급금액계"])
        units = _clean_int(row["세대수"])
        sums[row["타입"]] += amt * units
        counts[row["타입"]] += units

    types = list(sums.keys())
    avgs_eok = [sums[t] / counts[t] / 1e8 for t in types]  # 억원 단위

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(types, avgs_eok, color=COLOR_ACCENT)
    ax.set_title("타입별 평균 공급금액", fontsize=13, fontweight="bold")
    ax.set_ylabel("억원")
    for bar, v in zip(bars, avgs_eok):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{v:.1f}억", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def chart_price_by_floor(price_rows: list[dict], housing_type: str, output_path: str) -> str | None:
    """특정 타입의 층별 공급금액 변화 라인 차트 (고층일수록 비싸지는 추세 시각화)."""
    rows = [r for r in price_rows if r["타입"] == housing_type]
    if not rows:
        return None

    def floor_sort_key(r):
        floor = r["층구분"].replace("층", "").replace(" 이상", "")
        return int(floor.split("-")[0])

    rows = sorted(rows, key=floor_sort_key)
    floors = [r["층구분"] for r in rows]
    prices_eok = [_clean_int(r["공급금액계"]) / 1e8 for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(floors, prices_eok, marker="o", color=COLOR_PRIMARY, linewidth=2)
    ax.set_title(f"{housing_type} 타입 — 층별 공급금액 변화", fontsize=13, fontweight="bold")
    ax.set_ylabel("억원")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def chart_price_trend(trend_data: list[dict], output_path: str, title: str = "인근 아파트 실거래가 추이") -> str:
    """
    market_analysis.MolitTradeClient.get_price_trend() 결과로 월별 평균 실거래가 라인 차트.
    ⚠️ 이 함수는 실제 국토교통부 실거래가 API 키로 데이터를 받아온 뒤에만 의미 있는 그래프가 나옵니다.
    """
    months = [d["year_month"] for d in trend_data]
    prices_eok = [
        (d["avg_price_manwon"] / 10000) if d["avg_price_manwon"] else None
        for d in trend_data
    ]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(months, prices_eok, marker="o", color=COLOR_PRIMARY, linewidth=2)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel("평균 거래가 (억원)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def chart_disclosure_severity(disclosure_items: list[dict], output_path: str) -> str:
    """사전고지 유의사항 심각도(상/중/하) 분포 바 차트."""
    from collections import Counter
    counter = Counter(item["severity"] for item in disclosure_items)
    order = ["상", "중", "하"]
    values = [counter.get(o, 0) for o in order]
    colors = ["#C0392B", "#E8A33D", "#95A5A6"]

    fig, ax = plt.subplots(figsize=(5, 4.5))
    bars = ax.bar(order, values, color=colors)
    ax.set_title("사전고지 유의사항 — 심각도 분포", fontsize=13, fontweight="bold")
    ax.set_ylabel("건수")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(v), ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
