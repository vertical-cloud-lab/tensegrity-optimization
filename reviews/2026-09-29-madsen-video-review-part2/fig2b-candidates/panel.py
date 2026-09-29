"""Emulate the manuscript's TikZ callout overlay (Fig. 2b) with matplotlib.
TikZ style being emulated (manuscript-body.tex, fig:printed-prototypes):
  callout: -{Latex[length=1.5mm]}, line width 0.5pt, draw=red!75!black
  lab: fill=white, fill opacity 0.85, inner sep 1pt, rounded corners 1pt
  font: \sffamily\scriptsize, symbols in math italic ($d_s$, $d_t$, $H$)
  single callouts: label node anchored south at the start point, arrow to target
  H: black double arrow, label at midway
Coordinates are TikZ-normalized: x in [0,1] left to right, y in [0,1] bottom to top.
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.transforms import ScaledTranslation
plt.rcParams['mathtext.fontset'] = 'cm'
RED = (0.75, 0.0, 0.0)  # red!75!black
PANEL_W_IN = 0.54 * 3.375  # 0.54\linewidth of an asmejour column (approx.)
FS = 6.5  # scriptsize (approx.)

def render(img, callouts, out, grid=False):
    img = np.asarray(img)
    h, w = img.shape[:2]
    dpi = w / PANEL_W_IN
    fig = plt.figure(figsize=(PANEL_W_IN, PANEL_W_IN * h / w), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, extent=(0, 1, 0, 1), aspect='auto', interpolation='lanczos')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    box = dict(boxstyle='round,pad=0.12,rounding_size=0.25', fc='white', ec='none', alpha=0.85)
    up = ScaledTranslation(0, 1.0 / 72, fig.dpi_scale_trans)
    head = '-|>,head_length=0.425,head_width=0.16'
    for c in callouts:
        if c['kind'] == 'arrow':
            (x0, y0), (x1, y1) = c['start'], c['end']
            ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=head, mutation_scale=10,
                                         lw=0.5, color=RED, shrinkA=0, shrinkB=0, zorder=2))
            ax.text(x0, y0, c['label'], ha='center', va='bottom', fontsize=FS, bbox=box,
                    transform=ax.transData + up, zorder=3)
        else:  # dim: double arrow with midway label
            (x0, y0), (x1, y1) = c['start'], c['end']
            ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                         arrowstyle='<|-|>,head_length=0.425,head_width=0.16',
                                         mutation_scale=10, lw=0.5, color='black', shrinkA=0, shrinkB=0, zorder=2))
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, c['label'], ha='center', va='center', fontsize=FS,
                    bbox=box, zorder=3)
    if grid:
        for v in np.arange(0.05, 1.0, 0.05):
            ax.axvline(v, color='c', lw=0.2); ax.axhline(v, color='c', lw=0.2)
            ax.text(v, 0.005, f'{v:.2f}', fontsize=2.5, color='b', ha='center')
            ax.text(0.003, v, f'{v:.2f}', fontsize=2.5, color='b', va='center')
    fig.savefig(out, dpi=dpi)
    plt.close(fig)

CURRENT = [
    dict(kind='arrow', label=r'$d_s$', start=(0.74, 0.95), end=(0.63, 0.52)),
    dict(kind='arrow', label=r'$d_t$', start=(0.22, 0.96), end=(0.34, 0.70)),
    dict(kind='dim', label=r'$H$', start=(0.05, 0.23), end=(0.05, 0.85)),
]
