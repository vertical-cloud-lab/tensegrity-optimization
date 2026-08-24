"""Build the combined "one AI bucket" figures and summary stats for issue #103.

Lumps Claude (measured per-run cost from Actions logs) and GitHub Copilot
(duration-based AI-credits estimate at Opus-class rates, per sgbaird's note
that Copilot sessions almost always ran the latest, Opus-class model) into a
single "AI" series. Produces:

- ai_combined_by_week.png: weekly AI cost and weekly AI sessions, one series
  each, with a calendar-month band beneath.
- ai_combined_running_cost.png: cumulative AI cost (central line plus the
  estimate's uncertainty band) against what was actually paid.

Copilot per-minute rates are the Opus-class band from make_running_cost.py:
coding agent $0.167 to $0.333/min (central $0.25), code review scaled from the
measured review-density rates by the same 5/3 Opus/Sonnet price ratio. Claude
costs are not estimates; every value comes from the run's own execution log.
"""

import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["text.parse_math"] = False
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

HERE = Path(__file__).parent
WEEK1 = date(2026, 3, 9)  # repo creation
END = date(2026, 8, 24)

CODING_LO, CODING_MID, CODING_HI = 1 / 6, 0.25, 1 / 3
REVIEW_LO, REVIEW_MID, REVIEW_HI = 21 / 45 * 5 / 3, 26 / 45 * 5 / 3, 31 / 45 * 5 / 3

SURFACE = "#fcfcfb"
BLUE = "#2a78d6"      # the single combined "AI" series
ORANGE = "#eb6834"    # actually paid
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"

# Human trigger acts for Copilot (mentions + issue assignments), from the
# issue #103 crawl of all issue/PR timelines. Used to allocate the Copilot
# cost estimate across users (GitHub logs no per-session trigger actor).
COPILOT_TRIGGERS = {"sgbaird": 168, "sgbaird-alt": 53, "sgbaird-yolo": 28, "ctrhjk": 3}


def week_of(d):
    return (d - WEEK1).days // 7 + 1


def week_x(d):
    return (d - WEEK1).days / 7 + 1


def load(name):
    with open(HERE / name) as f:
        return list(csv.DictReader(f))


def parse_date(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).date()


claude = [(parse_date(r["date_utc"]), float(r["cost_usd"]), r["trigger_actor"])
          for r in load("claude_runs.csv")]
copilot = [(parse_date(r["date_utc"]), float(r["minutes"]), r["kind"])
           for r in load("copilot_sessions.csv")]


def copilot_cost(minutes, kind, lo, mid, hi):
    rate = {"lo": lo, "mid": mid, "hi": hi}
    return {k: minutes * (rate[k] if kind == "coding-agent" else
                          {"lo": REVIEW_LO, "mid": REVIEW_MID, "hi": REVIEW_HI}[k])
            for k in rate}


# One combined event stream: (date, cost_lo, cost_mid, cost_hi)
events = [(d, c, c, c) for d, c, _ in claude]
for d, m, kind in copilot:
    cc = copilot_cost(m, kind, CODING_LO, CODING_MID, CODING_HI)
    events.append((d, cc["lo"], cc["mid"], cc["hi"]))
events.sort()

# Weekly aggregates
wk_lo, wk_mid, wk_hi = defaultdict(float), defaultdict(float), defaultdict(float)
wk_n = defaultdict(int)
for d, lo, mid, hi in events:
    w = week_of(d)
    wk_lo[w] += lo
    wk_mid[w] += mid
    wk_hi[w] += hi
    wk_n[w] += 1
weeks = list(range(1, week_of(END) + 1))


def style_axis(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, labelsize=12.5)


def month_band(ax, y=-0.22, h=0.085):
    months = [(3, "Mar"), (4, "Apr"), (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Aug")]
    for i, (m, name) in enumerate(months):
        nxt = date(2026, m + 1, 1)
        x0 = max(week_x(date(2026, m, 1)), 0.4)
        x1 = min(week_x(nxt), 25.6)
        ax.add_patch(Rectangle((x0, y), x1 - x0, h, transform=ax.get_xaxis_transform(),
                               clip_on=False, facecolor="#f0efec" if i % 2 == 0 else "#e3e2da",
                               edgecolor=SURFACE, linewidth=2))
        ax.text((x0 + x1) / 2, y + h / 2, name, transform=ax.get_xaxis_transform(),
                ha="center", va="center", fontsize=12.5, color=INK2, clip_on=False)
    ax.text(0.4, y - 0.05, "2026", transform=ax.get_xaxis_transform(),
            ha="left", va="top", fontsize=12, color=MUTED, clip_on=False)


# ---------------------------------------------------------------- by-week figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9.6), dpi=120, sharex=True,
                               gridspec_kw={"height_ratios": [3, 2], "hspace": 0.32})
fig.patch.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    style_axis(ax)

xs = weeks
ax1.bar(xs, [wk_mid[w] for w in xs], width=0.72, color=BLUE, zorder=3)
# Uncertainty whisker where the Copilot estimate contributes a range
for w in xs:
    if wk_hi[w] - wk_lo[w] > 1:
        ax1.plot([w, w], [wk_lo[w], wk_hi[w]], color=INK2, linewidth=1.6,
                 solid_capstyle="butt", zorder=4)
peak = max(xs, key=lambda w: wk_mid[w])
ax1.text(peak, wk_hi[peak] + 18, "$%s" % format(round(wk_mid[peak]), ","),
         ha="center", fontsize=13, color=INK)
may_peak = max(range(1, 14), key=lambda w: wk_mid[w])
ax1.text(may_peak, wk_hi[may_peak] + 18, "$%s" % format(round(wk_mid[may_peak]), ","),
         ha="center", fontsize=13, color=INK)
ax1.set_ylabel("AI cost, USD per week", fontsize=14, color=INK2)
ax1.set_title("Cost (API/credit-equivalent dollars; whiskers span the Copilot estimate range)",
              fontsize=13.5, color=INK2, loc="left", pad=10)

ax2.bar(xs, [wk_n[w] for w in xs], width=0.72, color=BLUE, zorder=3)
npeak = max(xs, key=lambda w: wk_n[w])
ax2.text(npeak, wk_n[npeak] + 1.5, str(wk_n[npeak]), ha="center", fontsize=13, color=INK)
ax2.set_ylabel("AI sessions per week", fontsize=14, color=INK2)
ax2.set_xlabel("Project week (week 1 begins Mar 9, 2026)", fontsize=14, color=INK2)
ax2.set_title("Agentic sessions (Claude runs + Copilot coding agent sessions + code reviews)",
              fontsize=13.5, color=INK2, loc="left", pad=10)
ax2.set_xlim(0.4, 25.6)
ax2.set_xticks(range(1, 26))
month_band(ax2)

fig.text(0.065, 0.97, "AI usage by project week, all agents in one bucket",
         fontsize=23, fontweight="bold", color=INK, va="top")
fig.text(0.065, 0.925,
         "Claude and GitHub Copilot combined. Claude is measured per-run cost from Actions logs; "
         "Copilot is the Opus-class AI-credits estimate\n($0.17 to $0.33 per agent-minute, central $0.25).",
         fontsize=13, color=INK2, va="top")
fig.subplots_adjust(left=0.065, right=0.97, top=0.815, bottom=0.13)
fig.savefig(HERE / "ai_combined_by_week.png", facecolor=SURFACE)
plt.close(fig)

# ---------------------------------------------------------- running cost figure
def cumulative(pairs):
    pairs = sorted(pairs)
    xs, ys, t = [], [], 0.0
    for d, v in pairs:
        t += v
        xs.append(week_x(d))
        ys.append(t)
    return xs, ys


cx, c_lo = cumulative([(d, lo) for d, lo, _, _ in events])
_, c_mid = cumulative([(d, mid) for d, _, mid, _ in events])
_, c_hi = cumulative([(d, hi) for d, _, _, hi in events])

paid = [(date(2026, 6, 29), 200.0), (date(2026, 7, 29), 200.0)]
paid += [(d, 0.04) for d, _, _ in copilot]
px, py = cumulative(paid)

end_x = week_x(END)


def extend(xs, ys):
    return xs + [end_x], ys + [ys[-1]]


fig, ax = plt.subplots(figsize=(16, 8.6), dpi=120)
fig.patch.set_facecolor(SURFACE)
style_axis(ax)

bx, blo = extend(cx, c_lo)
_, bhi = extend(cx, c_hi)
ax.fill_between(bx, blo, bhi, step="post", color=BLUE, alpha=0.13, linewidth=0)
mx, my = extend(cx, c_mid)
ax.step(mx, my, where="post", color=BLUE, linewidth=2.8)
qx, qy = extend(px, py)
ax.step(qx, qy, where="post", color=ORANGE, linewidth=2.4)

ax.text(end_x + 0.25, my[-1],
        "All AI, API/credit-\nequivalent ≈ $%s\n(est. $%s to $%s)"
        % tuple(format(round(v), ",") for v in (my[-1], c_lo[-1], c_hi[-1])),
        color=BLUE, fontsize=15, va="center")
ax.text(end_x + 0.25, qy[-1], "Actually paid\n≈ $%.0f" % qy[-1],
        color="#c14e20", fontsize=15, va="center")

ax.legend(handles=[
    Line2D([], [], color=BLUE, linewidth=2.8,
           label="All AI usage (Claude measured + Copilot estimated)"),
    Patch(facecolor=BLUE, alpha=0.13, label="Copilot estimate uncertainty"),
    Line2D([], [], color=ORANGE, linewidth=2.4,
           label="Actually paid (Claude Max fees + Copilot premium requests)"),
], loc="upper left", frameon=False, fontsize=13, labelcolor=INK2)

fig.text(0.065, 0.965, "Running cost of AI usage, all agents in one bucket",
         fontsize=23, fontweight="bold", color=INK, va="top")
fig.text(0.065, 0.918,
         "Cumulative since repo creation. One combined series: measured Claude run costs plus the "
         "Opus-class AI-credits estimate for Copilot sessions.\nThe paid line is two Claude Max cycles "
         "($400) plus 258 legacy premium requests (about $10).",
         fontsize=13, color=INK2, va="top")
ax.set_xlabel("Project week", fontsize=14, color=INK2)
ax.set_ylabel("Cumulative cost, USD", fontsize=14, color=INK2)
ax.set_xlim(0.4, 25.6)
ax.set_ylim(0, None)
ax.set_xticks(range(1, 26))
month_band(ax, y=-0.15, h=0.055)
fig.subplots_adjust(left=0.065, right=0.80, top=0.845, bottom=0.185)
fig.savefig(HERE / "ai_combined_running_cost.png", facecolor=SURFACE)
plt.close(fig)

# ------------------------------------------------------------------ summary stats
copilot_total = {k: sum(copilot_cost(m, kind, CODING_LO, CODING_MID, CODING_HI)[k]
                        for _, m, kind in copilot) for k in ("lo", "mid", "hi")}
claude_total = sum(c for _, c, _ in claude)
print("claude runs %d  total $%.2f" % (len(claude), claude_total))
print("copilot sessions %d  est $%.0f ($%.0f-$%.0f)"
      % (len(copilot), copilot_total["mid"], copilot_total["lo"], copilot_total["hi"]))
print("combined events %d  central $%.2f  range $%.2f-$%.2f"
      % (len(events), c_mid[-1], c_lo[-1], c_hi[-1]))
print("actually paid $%.2f" % py[-1])

monthly = defaultdict(lambda: [0.0, 0])
for d, _, mid, _ in events:
    monthly[d.strftime("%Y-%m")][0] += mid
    monthly[d.strftime("%Y-%m")][1] += 1
for m in sorted(monthly):
    print("month %s  $%8.2f  %3d sessions" % (m, *monthly[m]))

per_user = defaultdict(lambda: [0, 0.0])  # sessions triggered, cost
for _, c, actor in claude:
    per_user[actor][0] += 1
    per_user[actor][1] += c
n_trig = sum(COPILOT_TRIGGERS.values())
for u, n in COPILOT_TRIGGERS.items():
    share = n / n_trig
    per_user[u][0] += round(share * len(copilot))
    per_user[u][1] += share * copilot_total["mid"]
for u, (n, c) in sorted(per_user.items(), key=lambda kv: -kv[1][1]):
    print("user %-14s %4d sessions  $%8.2f" % (u, n, c))

peak_wk = max(weeks, key=lambda w: wk_mid[w])
print("peak week %d: $%.0f over %d sessions" % (peak_wk, wk_mid[peak_wk], wk_n[peak_wk]))
print("busiest week by sessions: week %d with %d" % (npeak, wk_n[npeak]))
