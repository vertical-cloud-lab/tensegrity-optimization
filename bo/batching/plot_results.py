"""Two-panel figure: total and per-article walltime vs. articles per plate."""
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SURFACE = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; GRID = '#e7e6e2'
BATCHED = '#2a78d6'; SEQUENTIAL = '#eb6834'

rows = [r for r in csv.DictReader(open('batch-walltime-results.csv')) if r['n_articles'].isdigit()]
N = [int(r['n_articles']) for r in rows]
tot = [int(r['total_time_s']) / 3600 for r in rows]
seq = [int(r['sequential_total_s']) / 3600 for r in rows]
per = [int(r['per_article_s']) / 3600 for r in rows]
per_seq = seq[0]

plt.rcParams.update({
    'font.size': 11, 'text.color': INK, 'axes.edgecolor': GRID,
    'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.titlecolor': INK, 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE,
})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.4), dpi=200, layout='constrained')
fig.suptitle('T3 prism print walltime vs. articles per plate\n'
             'slicer estimates: Bambu Studio 02.07.01.62, Bambu Lab H2D, as-printed profile',
             fontsize=11, fontweight='bold')

for ax in (ax1, ax2):
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.set_xticks(N)
    ax.set_xlabel('articles per plate (N)')

ax1.plot(N, seq, color=SEQUENTIAL, linewidth=2, marker='o', markersize=7, label='N solo plates (sequential)')
ax1.plot(N, tot, color=BATCHED, linewidth=2, marker='o', markersize=7, label='one plate with N articles')
ax1.set_ylabel('total walltime (h)')
ax1.set_title('Total walltime for N articles', fontsize=11)
ax1.legend(frameon=False, loc='upper left')
ax1.annotate(f'{seq[-1]:.0f} h', (N[-1], seq[-1]), textcoords='offset points',
             xytext=(-4, 8), ha='right', color=INK, fontweight='bold')
ax1.annotate(f'{tot[-1]:.0f} h', (N[-1], tot[-1]), textcoords='offset points',
             xytext=(-2, 10), ha='right', color=INK, fontweight='bold')
ax1.annotate('71% less walltime\nat N = 9', xy=(9, (seq[-1] + tot[-1]) / 2),
             xytext=(-105, -8), textcoords='offset points', color=INK2)

ax2.axhline(per_seq, color=SEQUENTIAL, linewidth=2, linestyle=(0, (4, 3)))
ax2.plot(N, per, color=BATCHED, linewidth=2, marker='o', markersize=7, label='one plate with N articles')
ax2.set_ylabel('walltime per article (h)')
ax2.set_title('Walltime per article', fontsize=11)
ax2.set_ylim(0, per_seq * 1.15)
ax2.annotate(f'solo plate: {per_seq:.1f} h/article', (5.0, per_seq),
             textcoords='offset points', xytext=(0, 6), color=INK)
ax2.annotate(f'{per[-1]:.2f} h/article', (N[-1], per[-1]), textcoords='offset points',
             xytext=(2, 12), ha='right', color=INK, fontweight='bold')
ax2.legend(frameon=False, loc='center right')

fig.savefig('batch-walltime-tradeoff.png')
print('saved batch-walltime-tradeoff.png')
