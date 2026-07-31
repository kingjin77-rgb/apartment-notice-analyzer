"""
viz_generator.py
확장 모듈(environment/school/landuse/defect/indoor_air_quality/fire_safety) 결과를
report_pipeline 스타일(맑은 고딕, NAVY/GOLD 팔레트)의 차트 이미지로 변환한다.

report_engine.js COLORS 상수와 동일한 팔레트를 쓴다 — 리포트 본문과 시각적으로
어긋나지 않게 하기 위함. 색상 하나라도 바꿀 거면 report_engine.js도 같이 바꿀 것.

의존성: matplotlib, PIL (모두 이 프로젝트에 이미 설치돼 있음)
"""

from __future__ import annotations

import os
import math
import requests
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Rectangle
from matplotlib.font_manager import FontProperties

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# report_engine.js COLORS 와 동일 (하나 바꾸면 저쪽도 바꿀 것)
NAVY = "#1F3864"
NAVY2 = "#2E5395"
GOLD = "#C89B3C"
RED = "#C00000"
ORANGE = "#B45309"
GREEN = "#2E7D32"
GRAY = "#595959"
LIGHTGRAY = "#F2F2F2"
CREAM = "#F7F3EA"

SEVERITY_COLOR = {"상": RED, "중": ORANGE, "하": GREEN}


def _to_xy(lat: float, lon: float, site_lat: float, site_lon: float) -> tuple[float, float]:
    """단지 중심 기준 상대좌표(m) — 소규모 반경에서는 등거리원통도법 근사로 충분."""
    R = 6371000
    dx = math.radians(lon - site_lon) * R * math.cos(math.radians(site_lat))
    dy = math.radians(lat - site_lat) * R
    return dx, dy


# ─────────────────────────────────────────────────────────────
# 1) 용도지역 지도 — landuse_analysis.py의 ZoneItem.geometry(V-World 실제 폴리곤) 사용
# ─────────────────────────────────────────────────────────────

def render_landuse_map(land_report, site_lat: float, site_lon: float, out_path: str,
                        radius_m: int = 500) -> str:
    """
    land_report: landuse_analysis.analyze_landuse() 반환값 (LandUseReport)
    ZoneItem.geometry가 비어있으면(예전 캐시된 결과 등) 해당 zone은 지도에 그리지 않는다.
    """
    fig, ax = plt.subplots(figsize=(7.4, 7.0), dpi=150)

    for item in land_report.items:
        if item.kind != "용도지역" or not item.geometry:
            continue
        color = SEVERITY_COLOR.get(item.severity, GRAY)
        for polygon in item.geometry:
            _draw_geometry(ax, polygon, site_lat, site_lon, color, item.name)

    site_x, site_y = 0, 0
    ax.scatter([site_x], [site_y], marker="*", s=260, c=NAVY, edgecolors="white",
               linewidths=0.8, zorder=5)
    ax.annotate("단지 위치", (site_x, site_y), textcoords="offset points", xytext=(0, -18),
                fontsize=10, fontweight="bold", color=NAVY, ha="center", zorder=5)

    r = radius_m * 1.3
    ax.set_xlim(-r, r)
    ax.set_ylim(-r, r)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(f"단지 주변 용도지역 현황 (반경 {radius_m}m, V-World 실측)",
                 fontsize=12, fontweight="bold", color=NAVY, pad=12)

    handles = [plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=SEVERITY_COLOR[s],
                          markersize=12, label=f"위험도 {s}") for s in ("상", "중", "하")]
    ax.legend(handles=handles, loc="lower left", fontsize=9, frameon=False)
    plt.tight_layout()
    plt.savefig(out_path, facecolor="white")
    plt.close()
    return out_path


def _draw_geometry(ax, coords, site_lat, site_lon, color, label):
    """GeoJSON Polygon([[lon,lat],...]) 또는 MultiPolygon([[[lon,lat],...]]) 좌표를 그린다."""
    if not coords:
        return
    # 깊이 판별: Polygon의 첫 ring은 [ [lon,lat], ... ] (숫자 쌍의 리스트)
    depth = 0
    probe = coords
    while isinstance(probe, list) and probe and isinstance(probe[0], list):
        depth += 1
        probe = probe[0]
    # depth==2 -> Polygon([ring, ring...]), depth==3 -> MultiPolygon([poly, poly...])
    polygons = coords if depth == 3 else [coords]
    for poly in polygons:
        exterior = poly[0]
        pts = [_to_xy(lat, lon, site_lat, site_lon) for lon, lat in exterior]
        ax.add_patch(MplPolygon(pts, closed=True, facecolor=color, edgecolor=color,
                                 alpha=0.35, linewidth=1.2))


# ─────────────────────────────────────────────────────────────
# 2) 학교 통학거리 차트 — school_analysis.py의 School 리스트 사용
# ─────────────────────────────────────────────────────────────

def render_school_chart(school_report, out_path: str) -> str:
    schools = [s for s in school_report.schools if s.walk_m or s.straight_m]
    if not schools:
        return ""
    schools.sort(key=lambda s: s.walk_m or s.straight_m or 0)

    fig, ax = plt.subplots(figsize=(7.2, max(2.4, 0.6 * len(schools) + 1)), dpi=150)
    names = [f"{s.name}\n({s.level})" for s in schools]
    dists = [s.walk_m or s.straight_m for s in schools]
    colors = [SEVERITY_COLOR.get(s.severity, NAVY) for s in schools]
    bars = ax.barh(names, dists, color=colors, height=0.5)
    for bar, d in zip(bars, dists):
        ax.text(bar.get_width() + max(dists) * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{d}m", va="center", ha="left", fontsize=10, color="#333333")
    ax.set_xlim(0, max(dists) * 1.25)
    ax.set_xlabel("단지 중심 기준 도보거리(m) 추정 — NEIS 좌표 기반", fontsize=8.5)
    ax.set_title("통학 예정 학교 거리 및 심각도", fontsize=12, fontweight="bold", color=NAVY, pad=10)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, facecolor="white")
    plt.close()
    return out_path


# ─────────────────────────────────────────────────────────────
# 3) 소방/실내공기질 체크리스트 인포그래픽
# ─────────────────────────────────────────────────────────────

def render_checklist_infographic(fire_report, air_report, out_path: str) -> str:
    """
    fire_report: fire_safety_check.scan_fire_safety() 반환값
    air_report:  indoor_air_quality.analyze_air_quality() 반환값
    체크(있음)=녹색 원, 미확인(누락 의심)=적색 X 로 표시하는 간단한 매트릭스.
    """
    rows: list[tuple[str, bool, str]] = []
    for f in fire_report.flags:
        rows.append((f.name, f.found_in_notice, f.condition))
    rows.append((
        "실내공기질 측정계획 고지",
        air_report.measurement_notice_found,
        "「실내공기질 관리법 시행규칙」 제6조 — 측정 20일 전 고지 의무",
    ))

    n = len(rows)
    fig, ax = plt.subplots(figsize=(8.4, 0.75 * n + 1.2), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, n + 1)
    ax.axis("off")

    ax.add_patch(Rectangle((0, n + 0.15), 10, 0.7, facecolor=NAVY, edgecolor="none"))
    ax.text(0.2, n + 0.5, "소방·실내공기질 고지사항 체크리스트", color="white",
            fontsize=13, fontweight="bold", va="center")

    for i, (name, ok, cond) in enumerate(rows):
        y = n - i - 0.5
        bg = CREAM if i % 2 else "white"
        ax.add_patch(Rectangle((0, y - 0.4), 10, 0.8, facecolor=bg, edgecolor="none"))
        color = GREEN if ok else RED
        marker = "●" if ok else "X"
        ax.text(0.35, y, marker, color=color, fontsize=16, va="center", ha="center",
                fontweight="bold")
        ax.text(0.9, y, name, fontsize=11, fontweight="bold", color="#222222", va="center")
        ax.text(0.9, y - 0.32, cond, fontsize=8, color=GRAY, va="center")

    plt.tight_layout()
    plt.savefig(out_path, facecolor="white")
    plt.close()
    return out_path


# ─────────────────────────────────────────────────────────────
# 4) 카카오 로컬 API — 반경 내 시설 자동 검색 (render_facility_map 입력 자동 생성)
# ─────────────────────────────────────────────────────────────

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

# 카테고리 그룹 코드 검색 (거리순 최대 15개, Kakao 카테고리 검색 API 한도)
_CATEGORY_SEARCH = {
    "대형마트": "MT1",
    "편의점": "CS2",
    "학교": "SC4",
    "지하철역": "SW8",
}
# 카테고리 코드가 없는 유의시설 — 키워드 검색으로 대체
_KEYWORD_SEARCH = {
    "장례식장": "장례식장",
}


def find_nearby_facilities(lat: float, lon: float, radius_m: int = 1000,
                            categories: list[str] | None = None,
                            per_category_limit: int = 5) -> list[dict]:
    """
    Kakao 로컬 API로 반경 내 시설을 자동 수집해 render_facility_map()이 바로 쓸 수 있는
    형식으로 반환한다. categories 생략 시 _CATEGORY_SEARCH + _KEYWORD_SEARCH 전체 조회.
    """
    if not KAKAO_REST_API_KEY:
        raise RuntimeError("KAKAO_REST_API_KEY 미설정 — 시설 자동검색 불가")

    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    targets = categories or list(_CATEGORY_SEARCH) + list(_KEYWORD_SEARCH)
    out: list[dict] = []

    for cat in targets:
        if cat in _CATEGORY_SEARCH:
            r = requests.get(
                "https://dapi.kakao.com/v2/local/search/category.json",
                headers=headers,
                params={"category_group_code": _CATEGORY_SEARCH[cat], "x": lon, "y": lat,
                        "radius": radius_m, "sort": "distance", "size": per_category_limit},
                timeout=10,
            )
        elif cat in _KEYWORD_SEARCH:
            r = requests.get(
                "https://dapi.kakao.com/v2/local/search/keyword.json",
                headers=headers,
                params={"query": _KEYWORD_SEARCH[cat], "x": lon, "y": lat,
                        "radius": radius_m, "sort": "distance", "size": per_category_limit},
                timeout=10,
            )
        else:
            continue
        r.raise_for_status()
        for doc in r.json().get("documents", []):
            out.append({
                "name": doc["place_name"],
                "lat": float(doc["y"]),
                "lon": float(doc["x"]),
                "category": cat,
                "distance_m": int(doc["distance"]) if doc.get("distance") else None,
            })
    return out


# ─────────────────────────────────────────────────────────────
# 5) 시설 위치관계도 (실제 지도) — bucheon 리포트에서 쓴 방식의 일반화 버전
# ─────────────────────────────────────────────────────────────

CATEGORY_COLOR = {
    "대형마트": NAVY, "편의점": GOLD, "지하철역": NAVY2, "학교": GREEN,
    "장례식장": RED, "혐오시설": RED,
}
CATEGORY_MARKER = {"장례식장": "x", "혐오시설": "x"}


def render_facility_map(site_lat: float, site_lon: float, site_name: str,
                        facilities: list[dict], out_path: str, zoom: int = 15,
                        radius_m: int = 1000) -> str:
    """
    facilities: [{"name":str,"lat":float,"lon":float,"category":str}, ...]
    좌표는 호출자가 미리 확보해서 넘겨야 한다 (Kakao Local API 등) — 이 함수는
    렌더링만 담당한다. staticmap으로 OSM 타일을 받아오므로 인터넷 연결이 필요하다.
    """
    from staticmap import StaticMap, CircleMarker
    from PIL import Image, ImageDraw, ImageFont

    W, H = 980, 900
    m = StaticMap(W, H, url_template="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                  headers={"User-Agent": "apartment-notice-analyzer/1.0"})
    for fac in facilities:
        m.add_marker(CircleMarker((fac["lon"], fac["lat"]), "#00000000", 0))
    m.add_marker(CircleMarker((site_lon, site_lat), "#00000000", 0))

    img = m.render(zoom=zoom, center=[site_lon, site_lat]).convert("RGBA")

    def lon_to_x(lon, z): return ((lon + 180.0) / 360.0) * (2 ** z)
    def lat_to_y(lat, z):
        return (1 - math.log(math.tan(lat * math.pi / 180.0) + 1 / math.cos(lat * math.pi / 180.0)) / math.pi) / 2 * (2 ** z)
    xc, yc = lon_to_x(site_lon, zoom), lat_to_y(site_lat, zoom)
    def to_px(lon, lat):
        return (W / 2 + (lon_to_x(lon, zoom) - xc) * 256, H / 2 + (lat_to_y(lat, zoom) - yc) * 256)

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 105))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    def font(sz, bold=False):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf", sz)
        except Exception:
            return ImageFont.load_default()

    def hx(c):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

    def text_with_halo(xy, s, fnt, fill, anchor="mm"):
        x, y = xy
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                draw.text((x + ox, y + oy), s, font=fnt, fill=(255, 255, 255, 230), anchor=anchor)
        draw.text((x, y), s, font=fnt, fill=fill, anchor=anchor)

    site_px = to_px(site_lon, site_lat)
    edge_px = to_px(site_lon, site_lat + radius_m / 111320.0)
    r = abs(site_px[1] - edge_px[1])
    draw.ellipse([site_px[0] - r, site_px[1] - r, site_px[0] + r, site_px[1] + r],
                 outline=(60, 60, 60, 180), width=2)
    draw.text((site_px[0] - r * 0.72, site_px[1] + r * 0.72), f"반경 {radius_m}m",
              fill=(70, 70, 70, 255), font=font(14), anchor="mm")

    for fac in facilities:
        px, py = to_px(fac["lon"], fac["lat"])
        col = hx(CATEGORY_COLOR.get(fac["category"], GRAY))
        if CATEGORY_MARKER.get(fac["category"]) == "x":
            s = 7
            draw.line([px - s, py - s, px + s, py + s], fill=col, width=3)
            draw.line([px - s, py + s, px + s, py - s], fill=col, width=3)
        else:
            rr = 6
            draw.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col, outline=(255, 255, 255, 255), width=2)
        text_with_halo((px + 12, py - 8), fac["name"], font(13), col, anchor="lm")

    star_col = hx(NAVY)
    sx, sy = site_px
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = 13 if i % 2 == 0 else 6
        pts.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
    draw.polygon(pts, fill=star_col, outline=(255, 255, 255, 255))
    text_with_halo((sx, sy + 22), site_name, font(16, bold=True), star_col)

    draw.rectangle([0, 0, W, 40], fill=(31, 56, 100, 235))
    draw.text((16, 20), "단지 주변 시설 위치관계도 (실제 지도)", fill=(255, 255, 255, 255),
              font=font(18, bold=True), anchor="lm")

    cats = sorted(set(f["category"] for f in facilities))
    lx, ly = 16, H - 20 - 19 * len(cats) - 16
    draw.rectangle([lx, ly, lx + 224, ly + 19 * len(cats) + 12], fill=(255, 255, 255, 225),
                   outline=(120, 120, 120, 255))
    fy = ly + 16
    for cat in cats:
        cx = lx + 20
        col = hx(CATEGORY_COLOR.get(cat, GRAY))
        if CATEGORY_MARKER.get(cat) == "x":
            s = 6
            draw.line([cx - s, fy - s, cx + s, fy + s], fill=col, width=3)
            draw.line([cx - s, fy + s, cx + s, fy - s], fill=col, width=3)
        else:
            draw.ellipse([cx - 6, fy - 6, cx + 6, fy + 6], fill=col, outline=(255, 255, 255, 255), width=1)
        draw.text((cx + 16, fy), cat, fill=(40, 40, 40, 255), font=font(14), anchor="lm")
        fy += 19

    draw.text((W - 6, H - 6), "© OpenStreetMap contributors", fill=(90, 90, 90, 255),
              font=font(11), anchor="rb")

    img.convert("RGB").save(out_path, "PNG")
    return out_path


# ─────────────────────────────────────────────────────────────
# 6) 확대 크롭(돋보기) — 단지배치도/평면배치도 등에서 특정 구간만 확대
# ─────────────────────────────────────────────────────────────

def render_zoom_crop(source_path: str, crop_box: tuple[float, float, float, float],
                      out_path: str, zoom: float = 2.5, label: str | None = None,
                      context_thumb: bool = True, box_color: str = RED) -> str:
    """
    source_path: 원본 이미지(단지배치도, 평면배치도 등) 경로.
    crop_box: (x0, y0, x1, y1). 네 값 모두 1.0 이하면 원본 크기 대비 비율로,
              하나라도 1.0을 넘으면 픽셀 좌표로 해석한다.
    zoom: 크롭 영역을 몇 배로 확대할지.
    label: 크롭 이미지 상단 배너에 표시할 설명(예: "3층 세대창고 부분 확대"). 생략 가능.
    context_thumb: True면 좌상단에 원본 축소본 + 빨간 박스로 크롭 위치를 함께 표시해
                   "전체 도면 중 어디를 확대한 것인지"를 한눈에 알 수 있게 한다.
    반환값: out_path (report_engine.js의 image 블록에 그대로 넘기면 됨).
    """
    from PIL import Image, ImageDraw, ImageFont

    def hx(c):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

    def font(sz, bold=False):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf", sz)
        except Exception:
            return ImageFont.load_default()

    img = Image.open(source_path).convert("RGB")
    W, H = img.size
    x0, y0, x1, y1 = crop_box
    if max(x0, y0, x1, y1) <= 1.0:
        x0, x1 = x0 * W, x1 * W
        y0, y1 = y0 * H, y1 * H

    crop = img.crop((int(x0), int(y0), int(x1), int(y1)))
    crop = crop.resize((max(1, int(crop.width * zoom)), max(1, int(crop.height * zoom))), Image.LANCZOS)

    banner_h = 44 if label else 0
    canvas = Image.new("RGB", (crop.width, crop.height + banner_h), "white")
    canvas.paste(crop, (0, banner_h))
    draw = ImageDraw.Draw(canvas)

    if label:
        draw.rectangle([0, 0, canvas.width, banner_h], fill=hx(NAVY))
        # 돋보기 아이콘(유니코드 이모지는 malgun 폰트에 글리프가 없어 직접 그림)
        icx, icy, icr = 24, banner_h // 2 - 2, 7
        draw.ellipse([icx - icr, icy - icr, icx + icr, icy + icr], outline="white", width=3)
        draw.line([icx + icr * 0.7, icy + icr * 0.7, icx + icr * 1.7, icy + icr * 1.7], fill="white", width=3)
        draw.text((44, banner_h // 2), label, fill="white", font=font(17, bold=True), anchor="lm")

    draw.rectangle([0, banner_h, canvas.width - 1, canvas.height - 1], outline=hx(box_color), width=4)

    if context_thumb:
        thumb_w = max(80, int(canvas.width * 0.24))
        thumb = img.copy()
        thumb.thumbnail((thumb_w, thumb_w))
        scale = thumb.width / W
        tdraw = ImageDraw.Draw(thumb)
        tdraw.rectangle([x0 * scale, y0 * scale, x1 * scale, y1 * scale], outline=hx(box_color), width=3)
        pad = 5
        framed = Image.new("RGB", (thumb.width + 2 * pad, thumb.height + 2 * pad), "white")
        framed.paste(thumb, (pad, pad))
        fd = ImageDraw.Draw(framed)
        fd.rectangle([0, 0, framed.width - 1, framed.height - 1], outline=hx(GRAY), width=1)
        canvas.paste(framed, (12, banner_h + 12))

    canvas.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    # 간단한 자체 점검 — 실제 데이터 없이 그리기 로직만 확인
    import fire_safety_check, indoor_air_quality
    fr = fire_safety_check.scan_fire_safety("본 아파트는 지상 15층이며 스프링클러설비를 설치합니다.")
    ar = indoor_air_quality.analyze_air_quality("실내공기질 측정 계획을 수립합니다.")
    render_checklist_infographic(fr, ar, "_viz_test_checklist.png")
    print("체크리스트 인포그래픽 생성 OK -> _viz_test_checklist.png")
