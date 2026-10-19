"""Regenerate ai_running_cost.png from claude_runs.csv and copilot_sessions.csv.

Copilot AI-credits counterfactual is priced at Opus-class credit rates
($5 in / $25 out per MTok, identical for every Opus 4.5 through Opus 5),
per sgbaird's note in issue #103 that Copilot sessions almost always ran
the latest model, i.e. Opus-class (mostly Opus 4.8). The per-minute band
is the Sonnet-class band from the first pass ($0.10 to $0.20/min) scaled
by the Opus/Sonnet price ratio (5/3), giving $0.167 to $0.333/min with a
$0.25/min center. Cross-check: this repo's own measured Opus-class agent
burn is $0.250/min (opus-5, 1,158 min) and $0.286/min (opus-4-8, 311 min),
both inside the band. Code review runs use the denser review-rate band
scaled the same way.
"""

import csv
from datetime import date, datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["text.parse_math"] = False
from matplotlib.patches import Rectangle

HERE = Path(__file__).parent
WEEK1 = date(2026, 3, 9)  # repo creation

# Opus-class credit-rate bands, USD per agent-minute (see module docstring)
CODING_LO, CODING_MID, CODING_HI = 1 / 6, 0.25, 1 / 3
REVIEW_LO, REVIEW_MID, REVIEW_HI = 21 / 45 * 5 / 3, 26 / 45 * 5 / 3, 31 / 45 * 5 / 3
# Superseded Sonnet-class central rates from the first pass, for comparison
SONNET_CODING_MID, SONNET_REVIEW_MID = 0.15, 26 / 45

SURFACE = "#fcfcfb"
BLUE = "#2a78d6"      # Claude measured
VIOLET = "#4a3aa7"    # Copilot AI-credits counterfactual
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"


def week_x(d):
    return (d - WEEK1).days / 7 + 1


def load(name):
    with open(HERE / name) as f:
        return list(csv.DictReader(f))


def cumulative(events):
    """events: list of (date, value) -> step-plot arrays (x in project weeks)."""
    events = sorted(events)
    xs, ys, total = [], [], 0.0
    for d, v in events:
        total += v
        xs.append(week_x(d))
        ys.append(total)
    return xs, ys


claude = [
    (datetime.fromisoformat(r["date_utc"].replace("Z", "+00:00")).date(), float(r["cost_usd"]))
    for r in load("claude_runs.csv")
]
copilot = [
    (datetime.fromisoformat(r["date_utc"].replace("Z", "+00:00")).date(), float(r["minutes"]), r["kind"])
    for r in load("copilot_sessions.csv")
]


def copilot_cum(coding_rate, review_rate):
    return cumulative(
        [(d, m * (coding_rate if k == "coding-agent" else review_rate)) for d, m, k in copilot]
    )


cx, cy = cumulative(claude)
px_mid, py_mid = copilot_cum(CODING_MID, REVIEW_MID)
_, py_lo = copilot_cum(CODING_LO, REVIEW_LO)
_, py_hi = copilot_cum(CODING_HI, REVIEW_HI)
_, py_sonnet = copilot_cum(SONNET_CODING_MID, SONNET_REVIEW_MID)

legacy_total = sum(1 for _ in copilot) * 0.04
lx, ly = cumulative([(d, 0.04) for d, _, _ in copilot])

fees = [(date(2026, 6, 29), 200.0), (date(2026, 7, 29), 200.0)]
fx, fy = cumulative(fees)

END = date(2026, 8, 24)
end_x = week_x(END)

fig, ax = plt.subplots(figsize=(16, 8.8), dpi=120)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#c3c2b7")
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)


def step_extend(xs, ys):
    return xs + [end_x], ys + [ys[-1]]


# Copilot uncertainty band (Opus-class rates)
bx, blo = step_extend(px_mid, py_lo)
_, bhi = step_extend(px_mid, py_hi)
ax.fill_between(bx, blo, bhi, step="post", color=VIOLET, alpha=0.13, linewidth=0)

# Superseded Sonnet-class central line, for comparison with the first pass
sx, sy = step_extend(px_mid, py_sonnet)
ax.step(sx, sy, where="post", color=VIOLET, linewidth=1.4, linestyle=(0, (2, 3)), alpha=0.55)

mx, my = step_extend(px_mid, py_mid)
ax.step(mx, my, where="post", color=VIOLET, linewidth=2.6)

gx, gy = step_extend(lx, ly)
ax.step(gx, gy, where="post", color=MUTED, linewidth=2)

dx, dy = step_extend(fx, fy)
ax.step(dx, dy, where="post", color=INK2, linewidth=2, linestyle="--")

kx, ky = step_extend(cx, cy)
ax.step(kx, ky, where="post", color=BLUE, linewidth=2.6)

label_kw = dict(fontsize=15, va="center")
ax.text(end_x + 0.25, ky[-1], "Claude, API-equivalent\n$%s (actual)" % format(round(ky[-1]), ","),
        color=BLUE, **label_kw)
ax.text(end_x + 0.25, my[-1],
        "Copilot under 2026\nAI-credits pricing, Opus-class\n≈ $%s (est. $%s to $%s)"
        % tuple(format(round(v), ",") for v in (my[-1], py_lo[-1], py_hi[-1])),
        color=VIOLET, **label_kw)
ax.text(end_x + 0.25, py_sonnet[-1] - 60,
        "same, at Sonnet-class rates\n≈ $%d (superseded)" % round(py_sonnet[-1]),
        color=VIOLET, alpha=0.6, fontsize=13, va="center")
ax.text(end_x + 0.25, fy[-1] - 15, "Claude Max fees paid\n$400 (2 cycles at $200)",
        color=INK2, **label_kw)
ax.text(end_x + 0.25, ly[-1] - 60, "Copilot as billed, legacy\npremium requests ≈ $%.0f" % legacy_total,
        color=MUTED, **label_kw)

fig.text(0.065, 0.965, "Running cost of AI usage", fontsize=24, fontweight="bold", color=INK, va="top")
fig.text(0.065, 0.915,
         "Cumulative since repo creation. Claude line is measured per-run cost; Copilot AI-credits line prices "
         "logged session minutes\nat Opus-class credit rates (band $0.17 to $0.33 per agent-minute), since "
         "sessions almost always ran the latest Opus model.",
         fontsize=13.5, color=INK2, va="top")

ax.set_xlabel("Project week", fontsize=15, color=INK2)
ax.set_ylabel("Cumulative cost, USD", fontsize=15, color=INK2)
ax.set_xlim(0.6, 25.4)
ax.set_ylim(0, None)
ax.set_xticks(range(1, 26))
ax.tick_params(colors=MUTED, labelsize=13)

# Calendar month band beneath the axis
months = [(date(2026, m, 1), name) for m, name in
          [(3, "Mar"), (4, "Apr"), (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Aug")]]
band_y, band_h = -0.16, 0.055
for i, (start, name) in enumerate(months):
    nxt = date(2026, months[i + 1][0].month, 1) if i + 1 < len(months) else date(2026, 9, 1)
    x0 = max(week_x(start), 0.6)
    x1 = min(week_x(nxt), 25.4)
    ax.add_patch(Rectangle((x0, band_y), x1 - x0, band_h, transform=ax.get_xaxis_transform(),
                           clip_on=False, facecolor="#f0efec" if i % 2 == 0 else "#e3e2da",
                           edgecolor=SURFACE, linewidth=2))
    ax.text((x0 + x1) / 2, band_y + band_h / 2, name, transform=ax.get_xaxis_transform(),
            ha="center", va="center", fontsize=13.5, color=INK2, clip_on=False)
ax.text(0.6, band_y - 0.035, "2026", transform=ax.get_xaxis_transform(),
        ha="left", va="top", fontsize=13, color=MUTED, clip_on=False)

fig.subplots_adjust(left=0.065, right=0.79, top=0.83, bottom=0.19)
fig.savefig(HERE / "ai_running_cost.png", facecolor=SURFACE)
print("coding central $%.0f, range $%.0f-$%.0f" % (py_mid[-1], py_lo[-1], py_hi[-1]))
print("sonnet-superseded central $%.0f" % py_sonnet[-1])
print("legacy $%.2f" % legacy_total)
