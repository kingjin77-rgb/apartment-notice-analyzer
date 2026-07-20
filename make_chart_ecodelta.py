import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = '210 OmniGothicOTF 030'
plt.rcParams['axes.unicode_minus'] = False

# 에코델타용 — 독소조항 6건 + 동별유의사항 18건
data = [
    ("양호 확인 요소", 2, "#2E7D32"),
    ("검토 필요", 16, "#B45309"),
    ("위험 높음", 6, "#C00000"),
]
labels = [d[0] for d in data]
values = [d[1] for d in data]
colors = [d[2] for d in data]

fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
bars = ax.barh(labels, values, color=colors, height=0.55)

for bar, v in zip(bars, values):
    if v > 0:
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2, str(v),
                va='center', ha='left', fontsize=13, fontweight='bold', color='#333333')

ax.set_xlim(0, max(values) + 2)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#CCCCCC')
ax.tick_params(axis='y', length=0, labelsize=13)
ax.tick_params(axis='x', length=0, labelsize=0)
ax.set_xticks([])
ax.set_title('계약조항 검토 결과 분포', fontsize=14, fontweight='bold', color='#222222', loc='left', pad=12)

plt.tight_layout()
plt.savefig('chart_risk_ecodelta.png', transparent=True)
print('saved')
