# -*- coding: utf-8 -*-
"""
카카오맵 JS SDK로 실제 지도 위에 시설 마커를 그리는 HTML 생성기.
생성된 HTML은 로컬 서버(python -m http.server)로 띄운 뒤 claude-in-chrome(실제 크롬)으로
열어 스크린샷을 떠야 한다 — 카카오 SDK가 도메인 화이트리스트를 검사하므로 브라우저 프리뷰
샌드박스(외부 스크립트 차단)에서는 로드되지 않는다. developers.kakao.com에서 JS 키의
"JavaScript SDK 도메인"에 로컬서버 주소(예: http://localhost:8934)를 등록해 둘 것.

사용법:
    python make_kakao_map_html.py <out.html>
    (facilities/site 정보는 이 파일 상단 상수를 단지별로 고쳐서 사용 — 매 리포트마다 재사용)
"""
import sys
import json

KAKAO_JS_KEY = "6dd941689e3c39956d9ba809f127c947"

COLOR = {"대형마트": "#1F3864", "편의점": "#C89B3C", "지하철역": "#2E5395",
         "학교": "#2E7D32", "장례식장": "#C00000", "혐오시설": "#C00000"}

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>kakao map render</title>
<style>
  html, body {{ margin:0; padding:0; }}
  #map {{ width: {w}px; height: {h}px; }}
  #titlebar {{ position:absolute; top:0; left:0; width:{w}px; height:40px; background:#1F3864;
    color:white; font-family:'Malgun Gothic',sans-serif; font-size:18px; font-weight:bold;
    display:flex; align-items:center; padding-left:16px; z-index:10; box-sizing:border-box; }}
  #legend {{ position:absolute; left:16px; bottom:20px; background:rgba(255,255,255,0.92);
    border:1px solid #888; padding:10px 14px; font-family:'Malgun Gothic',sans-serif; font-size:13px;
    z-index:10; line-height:1.7; }}
  .dot {{ display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:6px; }}
</style></head>
<body>
<div id="titlebar">{title}</div>
<div id="map"></div>
<div id="legend">{legend_html}</div>
<script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={key}"></script>
<script>
const siteLat = {site_lat}, siteLon = {site_lon};
const siteName = {site_name_json};
const radiusM = {radius_m};
const facilities = {facilities_json};
const COLOR = {color_json};

const container = document.getElementById('map');
const map = new kakao.maps.Map(container, {{ center: new kakao.maps.LatLng(siteLat, siteLon), level: {level} }});

new kakao.maps.Circle({{
  map, center: new kakao.maps.LatLng(siteLat, siteLon), radius: radiusM,
  strokeWeight: 2, strokeColor: '#555', strokeOpacity: 0.8, strokeStyle: 'shortdash',
  fillColor: '#000', fillOpacity: 0
}});

function drawDot(lat, lon, color, label) {{
  const pos = new kakao.maps.LatLng(lat, lon);
  const content = document.createElement('div');
  content.style.width='14px'; content.style.height='14px'; content.style.borderRadius='50%';
  content.style.background=color; content.style.border='2px solid white';
  content.style.boxShadow='0 0 2px rgba(0,0,0,0.5)';
  new kakao.maps.CustomOverlay({{ map, position: pos, content, yAnchor: 0.5, xAnchor: 0.5, zIndex: 5 }});
  const labelDiv = document.createElement('div');
  labelDiv.textContent = label;
  labelDiv.style.fontFamily = "'Malgun Gothic',sans-serif";
  labelDiv.style.fontSize = '12px';
  labelDiv.style.fontWeight = 'bold';
  labelDiv.style.color = color;
  labelDiv.style.textShadow = '1px 1px 0 #fff,-1px -1px 0 #fff,1px -1px 0 #fff,-1px 1px 0 #fff';
  labelDiv.style.whiteSpace = 'nowrap';
  new kakao.maps.CustomOverlay({{ map, position: pos, content: labelDiv, yAnchor: 1.6, xAnchor: 0, zIndex: 6 }});
}}

facilities.forEach(f => drawDot(f.lat, f.lon, COLOR[f.category] || '#666', f.name));

const siteDiv = document.createElement('div');
siteDiv.style.fontSize = '26px'; siteDiv.style.color = '#1F3864'; siteDiv.textContent = '★';
new kakao.maps.CustomOverlay({{ map, position: new kakao.maps.LatLng(siteLat, siteLon), content: siteDiv, yAnchor: 0.5, xAnchor: 0.5, zIndex: 10 }});
const siteLabelDiv = document.createElement('div');
siteLabelDiv.textContent = siteName;
siteLabelDiv.style.fontFamily = "'Malgun Gothic',sans-serif";
siteLabelDiv.style.fontWeight = 'bold'; siteLabelDiv.style.fontSize = '14px'; siteLabelDiv.style.color = '#1F3864';
siteLabelDiv.style.textShadow = '1px 1px 0 #fff,-1px -1px 0 #fff,1px -1px 0 #fff,-1px 1px 0 #fff';
new kakao.maps.CustomOverlay({{ map, position: new kakao.maps.LatLng(siteLat, siteLon), content: siteLabelDiv, yAnchor: -0.8, xAnchor: 0.5, zIndex: 10 }});
</script>
</body></html>
"""


def build_html(site_lat, site_lon, site_name, facilities, out_path,
               radius_m=1000, w=980, h=900, level=5, title=None):
    cats = sorted({f["category"] for f in facilities})
    legend_html = "".join(
        f'<div><span class="dot" style="background:{COLOR.get(c, "#666")}"></span>{c}</div>'
        for c in cats
    )
    html = TEMPLATE.format(
        w=w, h=h, title=title or f"단지 주변 시설 위치관계도 ({site_name})",
        legend_html=legend_html, key=KAKAO_JS_KEY,
        site_lat=site_lat, site_lon=site_lon,
        site_name_json=json.dumps(site_name, ensure_ascii=False),
        radius_m=radius_m, facilities_json=json.dumps(facilities, ensure_ascii=False),
        color_json=json.dumps(COLOR, ensure_ascii=False), level=level,
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    import viz_generator as vg
    site_lat, site_lon = 37.4775890304877, 126.85778483448
    facs = vg.find_nearby_facilities(site_lat, site_lon, radius_m=1000)
    out = sys.argv[1] if len(sys.argv) > 1 else "_kakao_map.html"
    build_html(site_lat, site_lon, "힐스테이트 광명11", facs, out)
    print("wrote", out)
