import sys, os, json
sys.path.insert(0, r"D:\DDownloads\apartment_notice_analyzer\apartment_notice_analyzer")
from dotenv import load_dotenv
load_dotenv(r"D:\DDownloads\apartment_notice_analyzer\apartment_notice_analyzer\.env")

from modules.surrounding_environment import KakaoLocalClient

kakao = KakaoLocalClient()
print("kakao configured:", kakao.is_configured)

addr_candidates = [
    "경상북도 상주시 함창읍 윤직리 840",
    "경상북도 상주시 함창읍 함창로 491",  # 견본주택
]

coords = None
used_addr = None
for a in addr_candidates:
    c = kakao.geocode_address(a)
    print(a, "->", c)
    if c:
        coords = c
        used_addr = a
        break

if coords:
    survey = kakao.full_survey(used_addr)
    with open("kakao_survey.json", "w", encoding="utf-8") as f:
        json.dump(survey, f, ensure_ascii=False, indent=2)
    print("saved kakao_survey.json")
else:
    print("geocode failed for all candidates")
