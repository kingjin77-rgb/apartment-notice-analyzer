# -*- coding: utf-8 -*-
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

M = json.load(open('/tmp/lc/unit_matrix.json', encoding='utf-8'))
P = json.load(open('/tmp/lc/price_table.json', encoding='utf-8'))
F = json.load(open('/tmp/lc/findings.json', encoding='utf-8'))
ALLF = [f for c in F['categories'] for f in c['findings']]

FN = "맑은 고딕"
NAVY = "1F3864"; GOLD = "C89B3C"; RED = "C0392B"
thin = Side(style="thin", color="C8D0DA")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

def hdr(ws, row, vals, widths=None, height=26):
    for i, v in enumerate(vals, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = Font(name=FN, bold=True, size=10, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
    ws.row_dimensions[row].height = height
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

def cell(ws, r, c, v, **kw):
    x = ws.cell(row=r, column=c, value=v)
    x.font = Font(name=FN, size=kw.get('size', 10), bold=kw.get('bold', False),
                  color=kw.get('color', "1A1A1A"))
    x.alignment = Alignment(horizontal=kw.get('h', 'left'), vertical='center',
                            wrap_text=kw.get('wrap', True))
    x.border = BOX
    if kw.get('fill'): x.fill = PatternFill("solid", fgColor=kw['fill'])
    return x

def title(ws, text, sub=""):
    ws['A1'] = text
    ws['A1'].font = Font(name=FN, bold=True, size=16, color=NAVY)
    ws.row_dimensions[1].height = 30
    if sub:
        ws['A2'] = sub
        ws['A2'].font = Font(name=FN, size=9.5, color="666666")
        ws.row_dimensions[2].height = 18

wb = Workbook()

# ══════════════ 1. 사용안내 ══════════════
ws = wb.active; ws.title = "사용안내"
title(ws, "번영로 롯데캐슬 센트럴스카이 · 사전점검 체크리스트",
      "법무법인 제이엘 분양공고문 분석팀 · 입주자모집공고 69면 전수 통독 결과 기준")
ws.column_dimensions['A'].width = 4
ws.column_dimensions['B'].width = 24
ws.column_dimensions['C'].width = 96

rows = [
 ("시트 구성", "", ""),
 ("", "① 세대 점검표", "동·호수·타입만 입력하면 그 세대에 해당하는 유의사항이 자동으로 뜹니다. 실제 점검은 이 시트에서 합니다."),
 ("", "② 동별 유의사항", "101·102·103동 각각 어떤 시설이 어디에 있는지 — 공고문 50~54면에서 그대로 옮긴 것입니다."),
 ("", "③ 세대내부 점검", "마감재·옵션·설비 등 집 안에서 눈으로 확인할 항목입니다. 전 세대 공통입니다."),
 ("", "④ 타입 정보", "타입별 소방관 진입창 위치와 층별 공급금액입니다. ①번 시트가 이 표를 참조합니다."),
 ("", "⑤ 검토 발견목록", "공고문 69면에서 찾은 31건 전체 목록입니다."),
 ("", "", ""),
 ("입력 방법", "", ""),
 ("", "노란색 칸만 입력", "①번 시트의 노란 칸(동·호수·층·타입)만 채우시면 나머지는 자동으로 채워집니다."),
 ("", "판정란", "확인 결과를 '적합 / 하자 / 확인필요' 중에서 고르시면 됩니다. 목록에서 선택할 수 있습니다."),
 ("", "사진", "하자로 판정한 항목은 사진을 찍고 파일명을 비고란에 적어 두십시오. 나중에 근거가 됩니다."),
 ("", "", ""),
 ("색 표시", "", ""),
 ("", "빨강", "치명 — 계약·시공 전에 반드시 확인해야 할 항목"),
 ("", "주황", "높음 — 입주 전 확인하고 기록을 남겨야 할 항목"),
 ("", "파랑", "중간 — 알고 있어야 할 항목"),
 ("", "노랑", "입력하는 칸"),
 ("", "", ""),
 ("주의", "", ""),
 ("", "근거", "모든 항목에 공고문 면수가 붙어 있습니다. 사업주체와 다툴 때 그 면을 펴서 보여주십시오."),
 ("", "표현", "'하자다'라고 단정하기보다 '공고문 O면과 다릅니다'라고 기록하는 편이 낫습니다."),
 ("", "미확정", "'확인필요'로 남긴 항목은 사업주체에 서면 질의로 넘기십시오. 구두 답변은 기록에 남지 않습니다."),
]
r = 4
for a, b, c in rows:
    if a:
        x = cell(ws, r, 2, a, bold=True, size=11, color=NAVY)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        x.fill = PatternFill("solid", fgColor="EDF2F9")
        ws.cell(row=r, column=3).border = BOX
    elif b:
        cell(ws, r, 2, b, bold=True, color=NAVY)
        cell(ws, r, 3, c)
    ws.row_dimensions[r].height = 20 if a else 26
    r += 1

leg = r + 1
cell(ws, leg, 2, "예시", bold=True, color="666666")
cell(ws, leg, 3, "① 세대 점검표에  동=103동 · 호수=2102 · 층=21 · 타입=84B  를 넣으면, "
                 "'21층 소화수조와 같은 층', '진입창 없음(21층 이상)', '번영로 남동측 면함', "
                 "'승강기 4대' 가 자동으로 표시됩니다.", color="666666")
ws.row_dimensions[leg].height = 34

# ══════════════ 4. 타입 정보 (먼저 만들어야 ①이 참조 가능) ══════════════
wt = wb.create_sheet("④ 타입정보")
title(wt, "타입별 정보", "공고문 6·7·8면(공급금액·세대수) · 50면(소방관 진입창 위치)")
hdr(wt, 4, ["타입", "동·라인", "총 세대수", "소방관 진입창 위치", "3층", "11~19층", "21~30층", "31~40층", "41층 이상"],
    [10, 32, 11, 34, 15, 15, 15, 15, 15])
fw = {x['type']: x['where'] for x in M['fire_window']['by_type']}
r = 5
for t, d in P['주택형'].items():
    band = {b[0]: b[2] for b in d['층별']}
    cell(wt, r, 1, t, bold=True, h='center', color=NAVY)
    cell(wt, r, 2, d['동라인'])
    cell(wt, r, 3, d['총세대'], h='center')
    w = fw.get(t, "")
    warn = ('침실' in w) or ('안방' in w)
    cell(wt, r, 4, w, color=RED if warn else "1A1A1A", bold=warn,
         fill="FDF2F1" if warn else None)
    for i, b in enumerate(['3층', '11~19층', '21~30층', '31~40층', '41층 이상']):
        c = cell(wt, r, 5 + i, band.get(b, ""), h='right')
        c.number_format = '#,##0'
        if b == '21~30층':
            c.fill = PatternFill("solid", fgColor="FDF2F1"); c.font = Font(name=FN, size=10, bold=True, color=RED)
    wt.row_dimensions[r].height = 30
    r += 1
cell(wt, r + 1, 1, "합계", bold=True, h='center')
c = cell(wt, r + 1, 3, f"=SUM(C5:C{r-1})", bold=True, h='center'); c.number_format = '#,##0'
cell(wt, r + 1, 4, "← 634세대와 일치해야 합니다 (공고문 5면 '총 634세대')", color="666666")
note = r + 3
cell(wt, note, 1, "주의", bold=True, color=RED)
wt.merge_cells(start_row=note, start_column=2, end_row=note, end_column=9)
cell(wt, note, 2, "21~30층 칸을 붉게 표시한 이유 : 103동은 21층에 소화수조, 22층에 제연휀룸이 세대와 같은 층에 있습니다(52면). "
                  "그런데 가격표는 21층부터 30층까지를 한 칸으로 묶어 감액이 없습니다(7면).", color=RED)
wt.row_dimensions[note].height = 32
note2 = note + 1
cell(wt, note2, 1, "진입창", bold=True, color=RED)
wt.merge_cells(start_row=note2, start_column=2, end_row=note2, end_column=9)
cell(wt, note2, 2, "소방관 진입창은 각 동 20층 이하에만 있습니다(50면). 붉게 표시한 타입은 진입창이 거실이 아니라 "
                   "침실3·안방발코니에 있어 가구·가전이 가리기 쉬운 자리입니다.", color=RED)
wt.row_dimensions[note2].height = 32

# ══════════════ 2. 동별 유의사항 ══════════════
wd = wb.create_sheet("② 동별 유의사항")
title(wd, "동별 유의사항", "공고문 50~54면·59면에 동별로 흩어져 적힌 것을 한자리에 모은 것입니다")
hdr(wd, 4, ["동", "위치·층", "무엇이 있나", "어떤 영향", "등급", "근거 면", "확인 결과", "비고"],
    [9, 17, 42, 42, 9, 9, 13, 26])
GC = {"critical": (RED, "FDF2F1", "치명"), "high": ("B7791F", "FCF8EE", "높음"), "mid": ("3E6CB5", "FFFFFF", "중간")}
r = 5
first_row = r
for b in M['buildings']:
    start = r
    for it in b['items']:
        col, fill, lab = GC[it['risk']]
        cell(wd, r, 1, b['name'], bold=True, h='center', color=NAVY, fill=fill)
        cell(wd, r, 2, it['floor'], bold=True, color=col, fill=fill)
        cell(wd, r, 3, it['what'], fill=fill)
        cell(wd, r, 4, it['effect'], fill=fill)
        cell(wd, r, 5, lab, bold=True, h='center', color=col, fill=fill)
        cell(wd, r, 6, f"{it['page']}면", h='center', fill=fill)
        cell(wd, r, 7, "", fill="FFFDE7")
        cell(wd, r, 8, "", fill=fill)
        wd.row_dimensions[r].height = 30
        r += 1
    # 동 요약 한 줄
    cell(wd, r, 1, b['name'], bold=True, h='center', color="FFFFFF", fill=NAVY)
    wd.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
    cell(wd, r, 2, f"라인 : {b['lines']}   |   승강기 : {b['ev']}   |   {b['road']}",
         bold=True, color="FFFFFF")
    wd.cell(row=r, column=2).fill = PatternFill("solid", fgColor=NAVY)
    for cc in range(3, 9):
        wd.cell(row=r, column=cc).fill = PatternFill("solid", fgColor=NAVY)
        wd.cell(row=r, column=cc).border = BOX
    wd.row_dimensions[r].height = 24
    r += 2
last_row = r - 2

# 공통
cell(wd, r, 1, "세 동 공통", bold=True, h='center', color="FFFFFF", fill="0F2548")
wd.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
wd.row_dimensions[r].height = 24
r += 1
for c in M['common']:
    cell(wd, r, 1, "공통", h='center', bold=True, color="666666")
    cell(wd, r, 2, "저층부", bold=True, color="3E6CB5")
    cell(wd, r, 3, c['what'])
    cell(wd, r, 4, c['effect'])
    cell(wd, r, 5, "중간", h='center', color="3E6CB5")
    cell(wd, r, 6, f"{c['page']}면", h='center')
    cell(wd, r, 7, "", fill="FFFDE7")
    cell(wd, r, 8, "")
    wd.row_dimensions[r].height = 30
    r += 1

dv = DataValidation(type="list", formula1='"적합,하자,확인필요,해당없음"', allow_blank=True)
wd.add_data_validation(dv)
dv.add(f"G{first_row}:G{r-1}")
wd.freeze_panes = "A5"
wd.auto_filter.ref = f"A4:H{r-1}"

# ══════════════ 1. 세대 점검표 ══════════════
wu = wb.create_sheet("① 세대 점검표", 1)
title(wu, "세대 점검표", "노란 칸만 입력하시면 나머지는 자동으로 채워집니다")
for i, w in enumerate([14, 16, 16, 16, 16, 16, 16], 1):
    wu.column_dimensions[get_column_letter(i)].width = w
wu.column_dimensions['C'].width = 30
wu.column_dimensions['D'].width = 46
wu.column_dimensions['E'].width = 14
wu.column_dimensions['F'].width = 14
wu.column_dimensions['G'].width = 30

YEL = "FFFDE7"
cell(wu, 4, 1, "입력", bold=True, h='center', color="FFFFFF", fill=NAVY)
wu.merge_cells(start_row=4, start_column=1, end_row=4, end_column=7)
for c in range(2, 8):
    wu.cell(row=4, column=c).fill = PatternFill("solid", fgColor=NAVY); wu.cell(row=4, column=c).border = BOX
wu.row_dimensions[4].height = 22

labels = [("동", "103동"), ("호수", "2102"), ("층", 21), ("타입", "84B")]
r = 5
for lab, ex in labels:
    cell(wu, r, 1, lab, bold=True, h='center', color=NAVY, fill="EDF2F9")
    c = cell(wu, r, 2, ex, bold=True, h='center', fill=YEL, color="0000FF")
    wu.row_dimensions[r].height = 22
    r += 1
cell(wu, r, 1, "점검일", bold=True, h='center', color=NAVY, fill="EDF2F9")
cell(wu, r, 2, "", h='center', fill=YEL)
cell(wu, r, 3, "점검자", bold=True, h='center', color=NAVY, fill="EDF2F9")
cell(wu, r, 4, "", h='center', fill=YEL)
inp_last = r

dvd = DataValidation(type="list", formula1='"101동,102동,103동"', allow_blank=True)
wu.add_data_validation(dvd); dvd.add("B5")
dvt = DataValidation(type="list", formula1='"84A,84B,84C,84D,84E,84F,105"', allow_blank=True)
wu.add_data_validation(dvt); dvt.add("B8")

# 자동 판정 영역
r = inp_last + 2
cell(wu, r, 1, "이 세대에 해당하는 사항 (자동)", bold=True, h='center', color="FFFFFF", fill=NAVY)
wu.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
for c in range(2, 8):
    wu.cell(row=r, column=c).fill = PatternFill("solid", fgColor=NAVY); wu.cell(row=r, column=c).border = BOX
wu.row_dimensions[r].height = 22
r += 1
hdr(wu, r, ["구분", "판정", "내용", "왜 중요한가", "등급", "근거 면", "확인 결과 / 비고"])
head_row = r
r += 1

AUTO = [
 ("설비층 동거",
  '=IF(AND($B$5="103동",OR($B$7=21,$B$7=22)),"해당","해당없음")',
  '=IF(AND($B$5="103동",OR($B$7=21,$B$7=22)),IF($B$7=21,"21층 — 소화수조가 같은 층에 있습니다","22층 — 제연휀룸이 같은 층에 있습니다"),"-")',
  "가격표는 21~30층을 한 칸으로 묶어 감액이 없습니다. 이 세대는 11~19층보다 1,400~1,500만원을 더 냅니다.",
  "치명", "7·52면"),
 ("설비층 인접",
  '=IF(AND($B$5="103동",OR($B$7=20,$B$7=23)),"해당",IF(AND($B$5<>"103동",$B$7=20),"해당","해당없음"))',
  '=IF($B$7=20,"20층 — 피난안전구역·제연휀룸이 같은 층",IF(AND($B$5="103동",$B$7=23),"바로 아래 22층이 제연휀룸입니다","-"))',
  "공고문이 '아래 위 주변 층 세대의 소음, 진동'을 직접 고지한 구간입니다.",
  "높음", "52면"),
 ("소방관 진입창",
  '=IF($B$7<=20,"있음","없음")',
  '=IF($B$7<=20,IF(ISNA(MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),"타입을 선택하세요",INDEX(\'④ 타입정보\'!$D$5:$D$11,MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0))),"21층 이상 — 외부에서 들어올 창이 없습니다")',
  "진입창이 침실3·안방발코니인 타입은 가구·가전이 그 앞을 막지 않는지 확인하십시오. 21층 이상은 진입창 자체가 없습니다(396세대).",
  "치명", "50면"),
 ("최상층",
  '=IF($B$7>=49,"해당","해당없음")',
  '=IF($B$7>=49,"옥탑 소화수조·펌프실·EV기계실 바로 아래입니다","-")',
  "옥탑 설비의 소음·진동이 최상층 세대 및 주변 층에 미칠 수 있다고 공고문이 적었습니다.",
  "높음", "51·52면"),
 ("저층부",
  '=IF($B$7<=4,"해당","해당없음")',
  '=IF($B$7<=4,"2층 부대시설·1층 근생·차량동선·급배기 그릴 인접","-")',
  "부대시설 대부분이 2층에 몰려 있고 1층에 근생·DA·주차 급배기가 붙습니다.",
  "높음", "51·52·54면"),
 ("번영로 소음",
  '=IF(OR($B$5="102동",$B$5="103동"),"해당","해당없음")',
  '=IF(OR($B$5="102동",$B$5="103동"),"남동측 50M 대로(번영로)에 직접 면합니다","101동은 번영로에 면하지 않습니다")',
  "소음·조망·빛공해를 공고문이 동별로 따로 고지했습니다. 남동향 라인이면 방음창 등급을 확인하십시오.",
  "높음", "52면"),
 ("승강기",
  '=IF($B$5="103동","4대","5대")',
  '=IF($B$5="103동","아파트 4대 — 오피스텔 2대는 코어가 분리되어 쓸 수 없습니다","5호조합 기준 5대(비상용·피난용 포함)")',
  "103동만 1대 적습니다. 비상용·피난용을 포함한 대수이므로 평상시 가동 대수는 더 적습니다.",
  "높음", "50·53면"),
 ("필로티 직상부",
  '=IF(AND($B$7=3,OR(AND($B$5="103동",$B$8="84F"),AND($B$5<>"103동",$B$8="84E"))),"해당","해당없음")',
  '=IF(AND($B$7=3,OR(AND($B$5="103동",$B$8="84F"),AND($B$5<>"103동",$B$8="84E"))),"포디움 상부 2층 필로티 바로 위 세대입니다","-")',
  "101·102동은 5호라인, 103동은 4호라인에 2층 필로티가 있습니다. 바닥 단열·소음을 확인하십시오.",
  "중간", "51면"),
 ("공급금액",
  '=IF(ISNA(MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),"타입 선택","확인")',
  '=IF(ISNA(MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),"-",IF($B$7<=3,INDEX(\'④ 타입정보\'!$E$5:$E$11,MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),IF($B$7<=19,INDEX(\'④ 타입정보\'!$F$5:$F$11,MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),IF($B$7<=30,INDEX(\'④ 타입정보\'!$G$5:$G$11,MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),IF($B$7<=40,INDEX(\'④ 타입정보\'!$H$5:$H$11,MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)),INDEX(\'④ 타입정보\'!$I$5:$I$11,MATCH($B$8,\'④ 타입정보\'!$A$5:$A$11,0)))))))',
  "이 세대의 공급금액입니다(발코니 확장금액·옵션 별도). 계약서 금액과 대조하십시오.",
  "중간", "7·8면"),
]
GRADE_C = {"치명": (RED, "FDF2F1"), "높음": ("B7791F", "FCF8EE"), "중간": ("3E6CB5", "F7F9FC")}
auto_first = r
for name, f_jud, f_txt, why, grade, pages in AUTO:
    col, fill = GRADE_C[grade]
    cell(wu, r, 1, name, bold=True, color=NAVY, fill=fill)
    c = cell(wu, r, 2, f_jud, bold=True, h='center', color=col, fill=fill)
    cell(wu, r, 3, f_txt, fill=fill)
    cell(wu, r, 4, why, fill=fill)
    cell(wu, r, 5, grade, bold=True, h='center', color=col, fill=fill)
    cell(wu, r, 6, pages, h='center', fill=fill)
    cc = cell(wu, r, 7, "", fill=YEL)
    if name == "공급금액":
        wu.cell(row=r, column=3).number_format = '#,##0"원"'
    wu.row_dimensions[r].height = 40
    r += 1
auto_last = r - 1
dvj = DataValidation(type="list", formula1='"적합,하자,확인필요,해당없음"', allow_blank=True)
wu.add_data_validation(dvj); dvj.add(f"G{auto_first}:G{auto_last}")

r += 1
cell(wu, r, 1, "안내", bold=True, color="666666")
wu.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
cell(wu, r, 2, "위 판정은 입주자모집공고 원문 기재사항에 따른 것입니다. 실제 시공이 다를 수 있으므로, "
               "'해당'으로 뜬 항목은 현장에서 눈으로 확인하고 사진을 남기십시오. "
               "다르면 '하자'가 아니라 '공고문 O면과 상이'로 적는 편이 다투기 좋습니다.", color="666666")
wu.row_dimensions[r].height = 34
wu.freeze_panes = "A5"

# ══════════════ 3. 세대내부 점검 ══════════════
wi = wb.create_sheet("③ 세대내부 점검")
title(wi, "세대 내부 점검항목 (전 세대 공통)", "공고문에서 확인된 사항 중 집 안에서 눈으로 볼 수 있는 것만 뽑았습니다")
hdr(wi, 4, ["No", "구역", "점검 항목", "무엇을 보나", "근거 면", "판정", "사진 파일명 / 비고"],
    [6, 14, 34, 52, 11, 12, 26])
ITEMS = [
 ("주방", "상부장 자동소화장치 간섭", "상부장 안에 자동소화장치가 들어와 실사용 수납이 줄지 않았는지. 카탈로그 규격과 비교하십시오.", "58·59면"),
 ("주방", "하부장 온수·난방분배기 간섭", "하부장에 분배기·가스배관이 들어와 있는지. 제공품목표에는 정상 규격으로 표기됩니다.", "58·59면"),
 ("주방", "엔지니어드스톤 이음부", "상판·벽 이음부가 노출되거나 단차가 있는지. 56면이 '하자와 무관'으로 미리 적어 두었으니 사진이 중요합니다.", "44·56·61면"),
 ("주방", "엔지니어드스톤 스크래치·색차", "표면 스크래치와 패턴·색상 불균질. 역시 56면에서 사전 배제된 항목입니다.", "56면"),
 ("거실", "아트월 마감두께로 인한 내폭 감소", "유상 아트월 선택 시 거실 실사용 폭이 줄어듭니다. 줄어든 치수를 실측하십시오.", "61면"),
 ("거실", "소방관 진입창 표시", "지름 20cm 이상 붉은 역삼각형 표시가 있는지(20층 이하 세대). 가구가 가리지 않는지.", "50면"),
 ("침실", "침실2·3 에어컨 냉매배관", "시스템에어컨 미선택 세대는 배관이 없습니다. 선택 세대는 스탠드·벽걸이 추가 설치가 불가합니다.", "42면"),
 ("침실", "붙박이장이 진입창을 가리는지", "84A는 침실3, 84E·105는 안방발코니가 진입창입니다. 그 앞이 막혔는지 보십시오.", "50면"),
 ("발코니", "확장 부위 단열·결로", "확장 세대는 단열재 위치·벽체 두께가 달라집니다. 창호 주변 마감을 보십시오.", "41면"),
 ("발코니", "실외기실 위치와 소음", "커뮤니티·근생 실외기가 인접한 세대인지. 공고문이 환경권 침해 가능성을 자인했습니다.", "59면"),
 ("설비", "층간소음", "사후확인제 적용 대상이 아닙니다. 입주 전 자체 측정 결과를 요구해 두십시오.", "47면"),
 ("설비", "제연휀룸·소화수조 인접 소음", "103동 20~22층. 가동 시 소음·진동을 실제로 들어 보십시오.", "52면"),
 ("공용", "승강기 대수·운행", "103동은 아파트 4대. 출퇴근 시간대 대기시간을 확인하십시오.", "50·53면"),
 ("공용", "부대시설 지하주차장 연결", "커뮤니티 대부분이 지하주차장과 연결되지 않습니다. 실제 동선을 걸어 보십시오.", "54면"),
 ("공용", "주차 주행통로 높이", "택배차량 운행층 높이가 53면 2.7m, 64면 2.3m로 다릅니다. 실측 요청하십시오.", "53·64면"),
 ("공용", "총 주차대수", "공고문 69면 어디에도 없습니다. 세대당 몇 대인지 서면으로 받아 두십시오.", "전면"),
 ("옵션", "B2B 전용모델 사양", "옵션 가전은 시중 모델과 내부 스펙이 다를 수 있습니다. 모델명·에너지효율·보증기간을 확인하십시오.", "61면"),
 ("옵션", "기본품목 차감 내역", "옵션가는 기본품목 차감액이 이미 상계된 금액입니다. 산출내역서를 요구하십시오.", "60면"),
 ("서류", "홍보물과 실제 마감 대조", "카탈로그·모델하우스와 다른 부분을 사진으로 남기십시오. 우선순위가 공고문 안에서 세 번 뒤집힙니다.", "57·68·69면"),
 ("서류", "사전점검 지적사항 접수증", "제출한 지적사항의 접수 사실을 서면으로 받아 두십시오. 구두는 남지 않습니다.", "-"),
]
r = 5
for i, (zone, item, what, pages) in enumerate(ITEMS, 1):
    cell(wi, r, 1, i, h='center', bold=True, color="666666")
    cell(wi, r, 2, zone, bold=True, h='center', color=NAVY, fill="EDF2F9")
    cell(wi, r, 3, item, bold=True)
    cell(wi, r, 4, what)
    cell(wi, r, 5, pages, h='center', color="666666")
    cell(wi, r, 6, "", fill=YEL)
    cell(wi, r, 7, "", fill=YEL)
    wi.row_dimensions[r].height = 34
    r += 1
dvi = DataValidation(type="list", formula1='"적합,하자,확인필요,해당없음"', allow_blank=True)
wi.add_data_validation(dvi); dvi.add(f"F5:F{r-1}")
wi.freeze_panes = "A5"
wi.auto_filter.ref = f"A4:G{r-1}"

sm = r + 1
cell(wi, sm, 3, "판정 집계", bold=True, color=NAVY)
cell(wi, sm, 4, f'=_xlfn.CONCAT("적합 ",COUNTIF(F5:F{r-1},"적합")," / 하자 ",COUNTIF(F5:F{r-1},"하자")," / 확인필요 ",COUNTIF(F5:F{r-1},"확인필요"))', bold=True, color=RED)

# ══════════════ 5. 검토 발견목록 ══════════════
wf = wb.create_sheet("⑤ 검토 발견목록")
title(wf, "입주자모집공고 69면 전수 검토 — 발견 목록", "법무법인 제이엘 · 미통독 0면 · 총 %d건" % len(ALLF))
hdr(wf, 4, ["No", "등급", "분류", "근거 면", "쟁점", "공고문 원문", "협의회 확인란"],
    [6, 10, 14, 13, 44, 58, 22])
order = {"치명": 0, "높음": 1, "중간": 2}
rows_f = sorted(ALLF, key=lambda x: order[x['grade']])
cat_of = {f['id']: c['title'] for c in F['categories'] for f in c['findings']}
r = 5
for i, f in enumerate(rows_f, 1):
    col, fill = GRADE_C[f['grade']]
    cell(wf, r, 1, i, h='center', bold=True, color="666666")
    cell(wf, r, 2, f['grade'], bold=True, h='center', color=col, fill=fill)
    cell(wf, r, 3, cat_of[f['id']], h='center', fill=fill)
    cell(wf, r, 4, "·".join(str(p) for p in f['pages']) + "면", h='center', fill=fill)
    cell(wf, r, 5, f['title'], bold=True, color=NAVY, fill=fill)
    cell(wf, r, 6, f['quote'], color="555555", fill=fill)
    cell(wf, r, 7, "", fill=YEL)
    wf.row_dimensions[r].height = 40
    r += 1
wf.freeze_panes = "A5"
wf.auto_filter.ref = f"A4:G{r-1}"
cell(wf, r + 1, 5, "등급별 집계", bold=True, color=NAVY)
cell(wf, r + 1, 6, f'=_xlfn.CONCAT("치명 ",COUNTIF(B5:B{r-1},"치명")," / 높음 ",COUNTIF(B5:B{r-1},"높음")," / 중간 ",COUNTIF(B5:B{r-1},"중간")," = 총 ",COUNTA(B5:B{r-1}),"건")', bold=True, color=RED)

# 시트 순서 정리
wb.move_sheet("① 세대 점검표", offset=-1)
for s in wb.worksheets:
    s.sheet_view.showGridLines = False

# ── A4 인쇄 정밀 설정 (전 시트)
from openpyxl.worksheet.properties import PageSetupProperties
for ws_ in wb.worksheets:
    ws_.page_setup.paperSize = 9          # A4
    ws_.page_setup.orientation = 'landscape' if ws_.title in ('② 동별 유의사항','③ 세대내부 점검','⑤ 검토 발견목록') else 'portrait'
    ws_.page_setup.fitToWidth = 1
    ws_.page_setup.fitToHeight = 0        # 폭만 맞추고 세로는 흐름대로
    ws_.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws_.page_margins.left = ws_.page_margins.right = 0.35
    ws_.page_margins.top = 0.5; ws_.page_margins.bottom = 0.45
    ws_.print_options.horizontalCentered = True
# 반복 머리글
wb['② 동별 유의사항'].print_title_rows = '1:4'
wb['③ 세대내부 점검'].print_title_rows = '1:4'
wb['⑤ 검토 발견목록'].print_title_rows = '1:4'

wb.save('/tmp/lc/번영로롯데캐슬_사전점검_체크리스트.xlsx')
print("saved", [s.title for s in wb.worksheets])
