"""원문 증거 스니펫 카드 생성기 — 공고문 PDF에서 문구가 실린 줄을 크롭하고 빨간 박스 표시.
사용: python3 make_evidence_card.py <pdf> <페이지> <앵커단어> <출력.png> [위로포함줄수]
pdftotext -bbox 로 단어 좌표를 얻어 해당 행(및 위 N행)에 통짜 박스를 그린다. (2026-08-07 1군-1 구현)"""
import subprocess, re, glob, sys
from PIL import Image, ImageDraw

DPI = 200; SCALE = DPI / 72.0

def evidence_card(pdf, page, phrase_anchor, out, lines_up=1, pad_lines=2):
    xml = subprocess.run(['pdftotext','-f',str(page),'-l',str(page),'-bbox',pdf,'-'],capture_output=True,text=True).stdout
    words = [(float(a),float(b),float(c),float(d),w) for a,b,c,d,w in
             re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]+)</word>', xml)]
    anchor = next(((a,b,c,d) for a,b,c,d,w in words if phrase_anchor in w), None)
    if not anchor: raise SystemExit(f'앵커 미발견: {phrase_anchor} (p{page})')
    ax0, ay0, ax1, ay1 = anchor
    line_h = 12.3
    target_ys = [ay0 - line_h*i for i in range(0, lines_up+1)]
    y_top = min(target_ys) - line_h*pad_lines; y_bot = ay1 + line_h*pad_lines
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r',str(DPI),'-png',pdf,f'/tmp/_ev_{page}'],check=True)
    img = Image.open(sorted(glob.glob(f'/tmp/_ev_{page}-*.png'))[0]).convert('RGB')
    W, H = img.size
    off_y = max(0,int(y_top*SCALE))
    crop = img.crop((0, off_y, W, min(H,int(y_bot*SCALE))))
    dr = ImageDraw.Draw(crop)
    for ty in target_ys:
        row = [(a,b,c,d) for a,b,c,d,w in words if abs(b-ty) < 4]
        if not row: continue
        x0 = min(r[0] for r in row); x1 = max(r[2] for r in row)
        yy0 = min(r[1] for r in row); yy1 = max(r[3] for r in row)
        dr.rectangle([x0*SCALE-6, yy0*SCALE-off_y-4, x1*SCALE+6, yy1*SCALE-off_y+4], outline=(192,57,43), width=4)
    dr.rectangle([0,0,crop.width-1,crop.height-1], outline=(190,195,202), width=2)
    crop.save(out)
    print('OK', out, crop.size)

if __name__ == '__main__':
    a = sys.argv
    evidence_card(a[1], int(a[2]), a[3], a[4], int(a[5]) if len(a)>5 else 1)
