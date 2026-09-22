"""Audit whether recorded print covariates could improve surrogate accuracy.

Follow-up to reprint_reliability_ceiling.py, which showed the surrogate sits
at the print-to-print reliability ceiling. This script asks whether the
covariates the lab already has (or can pull) explain any of the residual:

  - per-article visual-defect notes  (issue #98 print logs / committed keys)
  - chamber RH at print              (rh_pct_at_print in the print keys)
  - outdoor temperature and RH near the BYU engineering building at print
    time                             (Open-Meteo ERA5 archive snapshot)
  - TPU spool age and drying state   (documented events only: new roll
    2026-07-13 on PR #35, drying + 0.6 mm high-flow nozzle 2026-08-17 on
    issue #96; undocumented swaps cannot be ruled out)

Reads committed snapshots only:
  manuscript/data/t3-prism-bo-batch-print-key.csv    (seed articles)
  manuscript/data/t3-prism-bo-round1-print-key.csv   (r2d2c, physical batch 2)
  manuscript/data/t3-prism-bo-round3-print-key.csv   (drran + 2dran)
  manuscript/data/t3-prism-bo-round4-print-key.csv   (corny, physical batch 4)
  manuscript/data/t3-prism-bo-round5-logocv.csv      (held-out predictions)
  manuscript/data/t3-prism-bo-round3-repeatability.csv (nine reprint pairs)
  manuscript/data/byu-eb-weather-hourly.csv          (hourly T/RH, local time)

Writes:
  manuscript/data/t3-prism-article-print-covariates.csv
  figures/analysis/print-covariate-audit.png

Print-session windows are reconstructed from the GitHub record (all local
dates, America/Denver); sources in SESSIONS below. Seed windows are the
weakest link: the six late seed articles are bounded by the issue #96 jam
resolution (2026-08-17 23:07 UTC) and their issue #98 log entries
(2026-08-19), while bag26v predates RH logging and is only bounded to a
two-week window, so its weather join is close to meaningless and is flagged.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "manuscript/data"
OUT_CSV = DATA / "t3-prism-article-print-covariates.csv"
OUT_FIG = ROOT / "figures/analysis/print-covariate-audit.png"

BLUE = "#1f77b4"
ORANGE = "#e8590c"
GRAY = "0.45"

# Print sessions: (window_start, window_end, window_quality, chamber_rh_pct,
# tpu_nozzle_mm, source). Dates are local (America/Denver), inclusive.
SESSIONS = {
    "seed-s0": ("2026-07-29", "2026-07-29", "day", np.nan, 0.4,
                "bpx68c print timelapse posted 2026-07-29 (PR #35 c5121885731 era); RH not yet logged"),
    "seed-early": ("2026-07-28", "2026-08-11", "wide-window", np.nan, 0.4,
                   "bag26v predates the #98 log (entry 2026-08-12 backfilled, RH unknown); print date unrecorded"),
    "seed-late": ("2026-08-17", "2026-08-19", "window", 8.0, 0.6,
                  "six articles printed after the #96 jam fix + 0.6 mm TPU nozzle install "
                  "(2026-08-17 23:07 UTC) and logged on #98 2026-08-19; sgbaird transcript "
                  "2026-08-17 confirms only 2-3 batch articles existed before the fix"),
    "r2d2c": ("2026-08-21", "2026-08-24", "window", 11.0, 0.6,
              "plate printed 2026-08-21 to 08-24 (process-media index); #98 logs 2026-08-24"),
    "drran": ("2026-09-01", "2026-09-02", "day", 11.0, 0.6,
              "#98 log 2026-09-02 16:39 UTC; ~15 h nine-article plate implies a 09-01 start"),
    "2dran": ("2026-09-04", "2026-09-05", "day", 11.0, 0.6,
              "#98 log 2026-09-05 19:34 UTC; drop sessions same day 20:30 UTC"),
    "corny": ("2026-09-10", "2026-09-11", "day", 7.0, 0.6,
              "#98 log 2026-09-11 16:41 UTC"),
}

# Documented TPU history (PR #35 / issue #96). No spool swap is documented
# after 2026-07-13; spool age assumes that spool stayed loaded, which the
# record cannot confirm.
TPU_ROLL_OPENED = pd.Timestamp("2026-07-13")
TPU_DRIED = [pd.Timestamp("2026-06-29"), pd.Timestamp("2026-08-17")]

SEED_SESSION = {"bpx68c": "seed-s0", "bag26v": "seed-early"}
SEED_LATE = {"6lhxfy", "6nheas", "9hhbkp", "ajhby6", "autv5r", "nvxsrv"}

MOISTURE_WORDS = ("bubble", "pore")


def classify_defect(text: str) -> tuple[int, int]:
    """(any_defect, moisture_signature) from a print-log defect note."""
    t = (text or "").strip().lower()
    if t in ("", "none", "nan") or t.startswith("none major") or t.startswith("no major"):
        return 0, 0
    return 1, int(any(w in t for w in MOISTURE_WORDS))


def load_articles() -> pd.DataFrame:
    frames = []
    seed = pd.read_csv(DATA / "t3-prism-bo-batch-print-key.csv")
    seed = seed.rename(columns={"mass_g": "mass_g_with_label"})
    seed["session"] = [SEED_SESSION.get(a, "seed-late" if a in SEED_LATE else "seed-other")
                       for a in seed.print_id]
    seed["pred_printed_mass_g"] = np.nan
    frames.append(seed[["print_id", "session", "mass_g_with_label",
                        "pred_printed_mass_g", "rh_pct_at_print", "defects"]])
    for fname, session_of in [
        ("t3-prism-bo-round1-print-key.csv", lambda a: "r2d2c"),
        ("t3-prism-bo-round3-print-key.csv", lambda a: "2dran" if a.startswith("2dran") else "drran"),
        ("t3-prism-bo-round4-print-key.csv", lambda a: "corny"),
    ]:
        key = pd.read_csv(DATA / fname)
        key["session"] = [session_of(a) for a in key.print_id]
        frames.append(key[["print_id", "session", "mass_g_with_label",
                           "pred_printed_mass_g", "rh_pct_at_print", "defects"]])
    df = pd.concat(frames, ignore_index=True)
    df["rh_pct_at_print"] = pd.to_numeric(df.rh_pct_at_print, errors="coerce")
    flags = [classify_defect(d) for d in df.defects.fillna("")]
    df["any_defect"] = [f[0] for f in flags]
    df["moisture_defect"] = [f[1] for f in flags]
    return df


def join_weather(df: pd.DataFrame) -> pd.DataFrame:
    wx = pd.read_csv(DATA / "byu-eb-weather-hourly.csv", parse_dates=["time_local"])
    rows = []
    for s, (d0, d1, quality, rh, nozzle, _src) in SESSIONS.items():
        t0, t1 = pd.Timestamp(d0), pd.Timestamp(d1) + pd.Timedelta(hours=23)
        w = wx[(wx.time_local >= t0) & (wx.time_local <= t1)]
        mid = t0 + (t1 - t0) / 2
        rows.append({
            "session": s, "window_start": d0, "window_end": d1,
            "window_quality": quality, "chamber_rh_recorded_pct": rh,
            "tpu_nozzle_mm": nozzle,
            "outdoor_temp_mean_C": w.temperature_2m_C.mean(),
            "outdoor_temp_max_C": w.temperature_2m_C.max(),
            "outdoor_rh_mean_pct": w.relative_humidity_2m_pct.mean(),
            "tpu_roll_age_days": (mid - TPU_ROLL_OPENED).days,
            "days_since_tpu_dried": min((mid - d).days for d in TPU_DRIED if d <= mid),
        })
    return df.merge(pd.DataFrame(rows), on="session", how="left")


def eta_squared(groups: list[np.ndarray]) -> tuple[float, float, float]:
    allv = np.concatenate(groups)
    grand = allv.mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    sst = ((allv - grand) ** 2).sum()
    f, p = stats.f_oneway(*groups)
    return ssb / sst, f, p


def main() -> None:
    cov = join_weather(load_articles())

    logo = pd.read_csv(DATA / "t3-prism-bo-round5-logocv.csv")
    for metric, col in [("t180", "t180"), ("e_reb_mJ", "ereb")]:
        d = logo[logo.metric == metric].set_index("print_id")
        cov[f"{col}_obs"] = cov.print_id.map(d.observed)
        cov[f"{col}_resid"] = cov.print_id.map(d.observed - d.predicted)
        cov[f"{col}_z"] = cov.print_id.map((d.observed - d.predicted) / d.predicted_sem)
    fit = cov[cov.t180_obs.notna()].copy()
    fit["mass_offset_g"] = fit.mass_g_with_label - fit.pred_printed_mass_g

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fit.to_csv(OUT_CSV, index=False, float_format="%.5f")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}  ({len(fit)} articles in the LOGO fit)")

    print("\n=== 1. Session-level ceiling: how much residual lives between print sessions ===")
    main_sessions = ["seed-late", "r2d2c", "drran", "2dran", "corny"]
    for col, label in [("t180_resid", "t180"), ("ereb_resid", "rebound (mJ)")]:
        groups = [fit.loc[fit.session == s, col].values for s in main_sessions]
        eta2, f, p = eta_squared(groups)
        allv = np.concatenate(groups)
        rmse_tot = np.sqrt((allv ** 2).mean())
        within = np.concatenate([g - g.mean() for g in groups])
        rmse_within = np.sqrt((within ** 2).mean() + (allv.mean()) ** 2)
        print(f"  {label}: between-session eta^2 = {eta2:.2f} (F={f:.2f}, p={p:.3f}) "
              f"over {len(allv)} articles in 5 sessions")
        print(f"    session means: "
              + ", ".join(f"{s} {g.mean():+.4f}" for s, g in zip(main_sessions, groups)))
        print(f"    LOGO RMSE {rmse_tot:.4f} -> {rmse_within:.4f} if a session covariate "
              f"were perfect ({100 * (1 - rmse_within / rmse_tot):.0f}% better, best case)")

    print("\n=== 2. Visual defects (recorded per article in the #98 logs) ===")
    for col, label in [("t180_resid", "t180"), ("ereb_resid", "rebound")]:
        a = fit.loc[fit.any_defect == 1, col]
        b = fit.loc[fit.any_defect == 0, col]
        for name, x, y in [("signed", a, b), ("absolute", a.abs(), b.abs())]:
            u, p = stats.mannwhitneyu(x, y)
            print(f"  {label} {name} residual, defect (n={len(a)}) vs clean (n={len(b)}): "
                  f"medians {x.median():+.4f} / {y.median():+.4f}, Mann-Whitney p={p:.2f}")
    r, p = stats.pearsonr(fit.any_defect, fit.t180_resid.abs())
    print(f"  point-biserial |t180 resid| ~ any_defect: r={r:+.2f} (p={p:.2f}), "
          f"variance share r^2={100 * r * r:.0f}%")
    top = fit.reindex(fit.t180_resid.abs().sort_values(ascending=False).index).head(6)
    print("  largest |t180 residual| articles vs their defect notes:")
    for row in top.itertuples():
        note = (row.defects or "none") if isinstance(row.defects, str) else "none"
        print(f"    {row.print_id:7s} resid {row.t180_resid:+.3f}  [{row.session}]  {note[:70]}")
    dr = fit[fit.session == "drran"]
    print(f"  within-drran bubbles vs clean t180 resid medians: "
          f"{dr.loc[dr.moisture_defect == 1, 't180_resid'].median():+.4f} vs "
          f"{dr.loc[dr.moisture_defect == 0, 't180_resid'].median():+.4f} "
          f"(bubble articles: {', '.join(dr.loc[dr.moisture_defect == 1, 'print_id'])})")

    print("\n=== 3. Chamber RH / outdoor weather / TPU age: collinear with session ===")
    sess = fit[fit.session.isin(main_sessions)].groupby("session").agg(
        t180_resid=("t180_resid", "mean"), ereb_resid=("ereb_resid", "mean"),
        chamber=("chamber_rh_recorded_pct", "first"),
        temp=("outdoor_temp_mean_C", "first"), orh=("outdoor_rh_mean_pct", "first"),
        roll=("tpu_roll_age_days", "first")).loc[main_sessions]
    print(sess.round(3).to_string())
    order = np.arange(len(sess))
    for name, v in [("outdoor temp", sess.temp), ("outdoor RH", sess.orh),
                    ("TPU roll age", sess.roll)]:
        r = stats.pearsonr(order, v).statistic
        print(f"  {name} vs session order: r={r:+.2f}"
              f"  -> indistinguishable from any other time-ordered effect at n=5 sessions")
    print("  chamber RH takes 3 values (8, 11, 7) locked to session; drran vs 2dran both "
          "recorded ~11% yet only drran shows tendon bubbles, so the recorded RH does not "
          "even separate the one moisture event in-record")

    print("\n=== 4. The one clean session contrast: drran -> 2dran (same nine designs) ===")
    pairs = pd.read_csv(DATA / "t3-prism-bo-round3-repeatability.csv")
    dt = pairs.t180_delta
    print(f"  t180 delta: median {dt.median():+.4f}, {sum(dt > 0)}/9 positive "
          f"(sign test p={stats.binomtest(int(sum(dt > 0)), 9).pvalue:.3f}); mean {dt.mean():+.4f}")
    s1, s2 = (fit[fit.session == s].iloc[0] for s in ("drran", "2dran"))
    print("  covariate deltas across that contrast (every one of these 'explains' it):")
    print(f"    outdoor temp {s2.outdoor_temp_mean_C - s1.outdoor_temp_mean_C:+.1f} C, "
          f"outdoor RH {s2.outdoor_rh_mean_pct - s1.outdoor_rh_mean_pct:+.0f}%, "
          f"TPU roll age +3 d, chamber RH +0%, "
          f"mean printed mass {fit[fit.session == '2dran'].mass_offset_g.mean() - fit[fit.session == 'drran'].mass_offset_g.mean():+.2f} g, "
          f"defect notes 4 bubble articles -> 0")
    print("  one contrast, five changed covariates: attribution is impossible without "
          "replicates across more sessions (the planned Sec. 3.5 study)")

    print("\n=== 5. Article-level process covariate: as-printed mass offset ===")
    m = fit[fit.mass_offset_g.notna()].copy()
    m["mass_ctr"] = m.mass_offset_g - m.groupby("session").mass_offset_g.transform("mean")
    for col in ("t180_resid", "ereb_resid"):
        r1 = stats.pearsonr(m.mass_offset_g, m[col])
        r2 = stats.pearsonr(m.mass_ctr, m[col])
        print(f"  {col} ~ mass offset: raw r={r1.statistic:+.2f} (p={r1.pvalue:.2f}); "
              f"within-session r={r2.statistic:+.2f} (p={r2.pvalue:.2f})  [n={len(m)}]")

    make_figure(fit, sess, pairs, main_sessions)


def make_figure(fit, sess, pairs, main_sessions) -> None:
    import matplotlib.dates as mdates

    wx = pd.read_csv(DATA / "byu-eb-weather-hourly.csv", parse_dates=["time_local"])
    daily = wx.set_index("time_local").resample("D").mean()

    fig, axes = plt.subplots(2, 2, figsize=(12.6, 8.6))
    fig.suptitle("What the recorded print covariates can and cannot explain "
                 "(44 LOGO-CV articles)", fontsize=12.5, y=0.985)

    # A: timeline
    ax = axes[0, 0]
    ax.plot(daily.index, daily.temperature_2m_C, color=ORANGE, lw=1.4,
            label="outdoor temp (daily mean, C)")
    ax.set_ylabel("outdoor temperature (C)", color=ORANGE)
    ax.set_ylim(14, 33)
    ax.tick_params(axis="y", labelcolor=ORANGE)
    ax2 = ax.twinx()
    ax2.plot(daily.index, daily.relative_humidity_2m_pct, color=BLUE, lw=1.4)
    ax2.set_ylabel("outdoor RH (%)", color=BLUE)
    ax2.tick_params(axis="y", labelcolor=BLUE)
    band_labels = {"seed-s0": "s0", "seed-late": "seed\nlate", "r2d2c": "r2d2c",
                   "drran": "drran", "2dran": "2dran", "corny": "corny"}
    for i, s in enumerate(["seed-s0"] + main_sessions):
        d0, d1 = SESSIONS[s][0], SESSIONS[s][1]
        ax.axvspan(pd.Timestamp(d0), pd.Timestamp(d1) + pd.Timedelta(hours=23),
                   color="0.78", alpha=0.5, zorder=0)
        rh = SESSIONS[s][3]
        mid = pd.Timestamp(d0) + (pd.Timestamp(d1) - pd.Timestamp(d0)) / 2
        txt = band_labels[s] + ("" if np.isnan(rh) else f"\n{rh:.0f}%")
        y = 32.6 if s not in ("2dran",) else 29.9
        ax.annotate(txt, xy=(mid, y), fontsize=7, ha="center", va="top", color="0.2")
    for when, txt in [(TPU_ROLL_OPENED, "new TPU roll\n(PR #35)"),
                      (pd.Timestamp("2026-08-17"), "TPU dried +\n0.6 mm nozzle (#96)")]:
        ax.axvline(when, color="0.3", ls="--", lw=0.9)
        ax.annotate(txt, xy=(when, 14.4), xytext=(3, 2),
                    textcoords="offset points", fontsize=7, color="0.25", va="bottom")
    ax.set_title("Print sessions (bands, chamber RH%) on the BYU-area\n"
                 "weather record: sessions, weather and spool age move together",
                 fontsize=9.5)
    ax.margins(x=0.01)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    for label in ax.get_xticklabels():
        label.set_fontsize(7.5)

    # B: t180 residual by session
    ax = axes[0, 1]
    rng = np.random.default_rng(0)
    for i, s in enumerate(main_sessions):
        g = fit[fit.session == s]
        x = i + rng.uniform(-0.14, 0.14, len(g))
        colors = np.where(g.any_defect == 1, ORANGE, BLUE)
        ax.scatter(x, g.t180_resid, s=42, facecolors="none", edgecolors=colors, lw=1.5)
        ax.hlines(g.t180_resid.mean(), i - 0.24, i + 0.24, color="0.2", lw=2)
    ax.axhline(0, color="0.6", ls="--", lw=0.9)
    for pid, dx in [("drran7", 0.0), ("r2d2c3", 0.0), ("6lhxfy", 0.0)]:
        row = fit[fit.print_id == pid]
        if len(row):
            i = main_sessions.index(row.session.iloc[0])
            ax.annotate(pid, xy=(i + dx, row.t180_resid.iloc[0]), xytext=(6, 0),
                        textcoords="offset points", fontsize=8, color="0.25", va="center")
    ax.set_xticks(range(len(main_sessions)))
    ax.set_xticklabels([s.replace("seed-", "seed\n") for s in main_sessions], fontsize=8.5)
    ax.set_ylabel("t180 held-out residual (observed - predicted)")
    ax.text(0.985, 0.985, "orange = defect note, blue = clean",
            transform=ax.transAxes, fontsize=8, color="0.3", ha="right", va="top")
    groups = [fit.loc[fit.session == s, "t180_resid"].values for s in main_sessions]
    eta2, _, p = eta_squared(groups)
    ax.set_title(f"Residual by print session (bars = session means):\n"
                 f"between-session share eta$^2$ = {eta2:.2f} (p = {p:.2f})", fontsize=9.5)

    # C: residual by defect class
    ax = axes[1, 0]
    classes = [("none recorded", (fit.any_defect == 0), BLUE),
               ("defect, other", (fit.any_defect == 1) & (fit.moisture_defect == 0), ORANGE),
               ("bubbles/pores\n(moisture signature)", fit.moisture_defect == 1, "#9467bd")]
    for i, (lab, mask, c) in enumerate(classes):
        g = fit[mask]
        x = i + rng.uniform(-0.13, 0.13, len(g))
        ax.scatter(x, g.t180_resid, s=42, facecolors="none", edgecolors=c, lw=1.5)
        ax.hlines(g.t180_resid.median(), i - 0.22, i + 0.22, color="0.2", lw=2)
    ax.axhline(0, color="0.6", ls="--", lw=0.9)
    for pid in ("drran7", "r2d2c3", "corny4"):
        row = fit[fit.print_id == pid].iloc[0]
        i = 2 if row.moisture_defect else (1 if row.any_defect else 0)
        ax.annotate(pid, xy=(i, row.t180_resid), xytext=(7, 0),
                    textcoords="offset points", fontsize=8, color="0.25", va="center")
    u, p = stats.mannwhitneyu(fit.loc[fit.any_defect == 1, "t180_resid"].abs(),
                              fit.loc[fit.any_defect == 0, "t180_resid"].abs())
    ax.set_xticks(range(3))
    ax.set_xticklabels([c[0] for c in classes], fontsize=8.5)
    ax.set_ylabel("t180 held-out residual")
    ax.set_title(f"Defect notes vs residual (any-defect |resid| p = {p:.2f}):\n"
                 "the largest outlier, r2d2c3, logged clean", fontsize=9.5)

    # D: pair deltas with covariate attribution box
    ax = axes[1, 1]
    order = pairs.t180_delta.sort_values().index
    bubble1 = {"drran3", "drran5", "drran6", "drran7"}
    cols = ["#9467bd" if pairs.loc[i, "print_1"] in bubble1 else BLUE for i in order]
    ax.bar(range(len(order)), pairs.loc[order, "t180_delta"], color=cols, width=0.62)
    ax.axhline(0, color="0.4", lw=0.9)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(pairs.loc[order, "print_1"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("t180: reprint minus first print")
    ax.set_title("The one clean session contrast, drran to 2dran: 8/9 shifted up\n"
                 "(purple = first print logged tendon bubbles)", fontsize=9.5)
    ax.text(0.97, 0.05,
            "changed across this contrast:\noutdoor temp, outdoor RH,\nspool +3 d, "
            "printed mass +0.27 g,\nbubbles 4 -> 0; chamber RH same\n"
            "one contrast cannot attribute",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color="0.25",
            bbox=dict(facecolor="white", alpha=0.9, edgecolor="0.8", pad=3))

    for ax in axes.flat:
        ax.grid(color="0.93", lw=0.7)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0, 0].spines["right"].set_visible(True)

    fig.tight_layout(rect=(0, 0, 1, 0.965), h_pad=2.2, w_pad=2.0)
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG, dpi=200)
    print(f"\nwrote {OUT_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
