"""Ringdown damping (zeta_pct): what the bench measures, what the sim can resolve.

The PR #86/#102 campaign summary carries two ringdown channels per article,
``fn_hz`` and ``zeta_pct``, fit to the post-impact free vibration of the top
vertex.  The measured ``zeta_pct`` spans 6.4 to 31 percent across the batch
(4.9x), is article-intrinsic, and is nearly independent of ``t180`` -- which
is why it was proposed as a second objective.  This script asks the two
follow-up questions:

1. What does the *measured* ``zeta_pct`` correlate with, across the design
   axes and the other measured channels?  (n = 6 to 8, so hypothesis-level.)
2. How well can the drop-tower analogue (``drop_tower_sim``) resolve it?
   Concretely: extract a simulated ringdown (fn, zeta) from the raw
   post-release traces the same way the bench does, then separate the two
   things that set it -- the *design* (geometry, tendon stiffness, inertia)
   at fixed material damping, and the material-damping *input dial*
   (``cable_zeta``, the hard-coded 0.02 until now) at fixed design.

Method notes:

* The ringdown is fit on the **raw** (unfiltered) relative acceleration
  ``a_top - a_ch5`` after the mat releases the carriage: the CFC-180 corner
  sits at ~300 Hz, on top of the measured 294-468 Hz band, so the filtered
  traces cannot carry a ringdown fit.
* After mat release everything is ballistic for ~0.6 s, so a 0.2 s window is
  clean free vibration with only the article's own dampers active.  The fit
  is a single damped cosine ``A exp(-s t) cos(2 pi f t + phi)``, initialized
  from the FFT peak and the log-envelope slope; ``zeta = s / sqrt(s^2 +
  (2 pi f)^2)``.  An R^2 is reported so a multi-modal or non-exponential
  decay is visible rather than silently averaged.

Run::

    python zeta_analysis.py            # all parts, writes CSVs + PNG
    python zeta_analysis.py --n-sobol 48
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

import drop_tower_sim as dts
from bo_evaluator import parameterization_to_design
from print_infill import scale_design

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "pr102"
OUT = HERE / "outputs"

PARAM_NAMES = ["R_mm", "H_mm", "twist_deg", "strut_d_mm", "cable_d_mm"]
G = 9.80665
RINGDOWN_DURATION_S = 0.20
RELEASE_MARGIN_S = 0.002


# --------------------------------------------------------------------------
# measured data
# --------------------------------------------------------------------------

def load_articles() -> pd.DataFrame:
    """The campaign summary, one row per article, design coords where mapped."""
    results = pd.read_csv(DATA / "t3-prism-bo-batch-drop-results.csv",
                          dtype={"spec": "string"})
    design = pd.read_csv(DATA / "t3-prism-bo-batch.csv").set_index("specimen")

    rows = []
    for _, r in results.iterrows():
        spec = None if pd.isna(r["spec"]) else str(r["spec"]).strip()
        rec = {
            "specimen": r["specimen"], "spec": spec,
            "mapped": bool(spec) and not pd.isna(r["mass_g"]),
            "mass_g": float(r["mass_g"]) if not pd.isna(r["mass_g"]) else np.nan,
            "t180": float(r["t180_mean"]),
            "t1000": float(r["t1000_mean"]),
            "e_rebound": float(r["e_rebound_mean"]),
            "fn_hz": float(r["fn_hz_mean"]) if not pd.isna(r["fn_hz_mean"]) else np.nan,
            "fn_hz_sd": float(r["fn_hz_sd"]) if not pd.isna(r["fn_hz_sd"]) else np.nan,
            "zeta_pct": (float(r["zeta_pct_mean"])
                         if not pd.isna(r["zeta_pct_mean"]) else np.nan),
            "zeta_pct_sd": (float(r["zeta_pct_sd"])
                            if not pd.isna(r["zeta_pct_sd"]) else np.nan),
            "dv_health": r["dv_health"],
        }
        if rec["mapped"]:
            if spec == "S0":
                params = dict(dts.S0_BASE_PARAMS)
            else:
                base = design.loc[int(spec)]
                params = {n: float(base[n]) for n in PARAM_NAMES}
            rec.update(params)
        rows.append(rec)
    return pd.DataFrame(rows)


def measured_correlations(articles: pd.DataFrame) -> pd.DataFrame:
    """Spearman of measured zeta_pct against design axes and other channels."""
    from scipy import stats

    rows = []
    y = articles["zeta_pct"].to_numpy(dtype=float)
    cands = PARAM_NAMES + ["mass_g", "t180", "t1000", "e_rebound", "fn_hz"]
    for cand in cands:
        x = articles[cand].to_numpy(dtype=float)
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() < 4:
            continue
        rho, p = stats.spearmanr(x[ok], y[ok])
        rows.append({"observable": cand, "n": int(ok.sum()),
                     "spearman_rho": float(rho), "spearman_p": float(p)})
    return pd.DataFrame(rows).sort_values("spearman_p").reset_index(drop=True)


# --------------------------------------------------------------------------
# simulated ringdown
# --------------------------------------------------------------------------

def ringdown_fit(t: np.ndarray, a: np.ndarray, *, fmin: float = 20.0) -> dict:
    """Fit ``A exp(-s t) cos(2 pi f t + phi)`` to a free-decay trace.

    The raw decay is multi-modal, so the fit works the way a bench modal fit
    does: find the dominant spectral line, isolate it with a zero-phase
    band-pass (0.5 to 2x the line), trim the filter edge transients and the
    decayed-to-noise tail, then fit the damped cosine.  ``dominant_frac`` is
    the fraction of raw spectral energy inside the fitted band, so a heavily
    multi-modal decay is visible rather than silently averaged.
    """
    from scipy.optimize import curve_fit
    from scipy.signal import butter, filtfilt, hilbert

    seg = a - float(np.mean(a))
    dt = float(t[1] - t[0])
    fs = 1.0 / dt

    # dominant frequency from the FFT peak above fmin
    sp = np.abs(np.fft.rfft(seg * np.hanning(seg.size))) ** 2
    fr = np.fft.rfftfreq(seg.size, dt)
    mask = fr >= fmin
    f0 = float(fr[mask][np.argmax(sp[mask])])
    band = (max(fmin, 0.5 * f0), min(2.0 * f0, 0.45 * fs))
    in_band = (fr >= band[0]) & (fr <= band[1])
    dominant_frac = float(np.sum(sp[in_band]) / max(np.sum(sp[mask]), 1e-30))

    # isolate the mode, drop the filtfilt edges
    b, a_c = butter(2, band, btype="bandpass", fs=fs)
    iso = filtfilt(b, a_c, seg)
    edge = int(0.05 * iso.size)
    iso, tt = iso[edge:-edge], t[edge:-edge] - t[edge]

    # fit only while the envelope is above 2 percent of its start
    env = np.abs(hilbert(iso))
    live = np.nonzero(env >= 0.02 * float(np.max(env[:max(env.size // 10, 1)])))[0]
    stop = int(live.max()) + 1 if live.size else iso.size
    iso, tt, env = iso[:stop], tt[:stop], env[:stop]

    s0, logA0 = np.polyfit(tt, np.log(np.maximum(env, 1e-12)), 1)
    s0 = max(-float(s0), 1.0)
    A0 = float(np.exp(logA0))

    def model(x, A, s, f, phi):
        return A * np.exp(-s * x) * np.cos(2.0 * math.pi * f * x + phi)

    try:
        popt, _ = curve_fit(
            model, tt, iso, p0=[A0, s0, f0, 0.0],
            bounds=([0.0, 0.0, band[0], -math.pi],
                    [np.inf, np.inf, band[1], math.pi]),
            maxfev=20000)
        A, s, f, phi = (float(v) for v in popt)
    except Exception:
        A, s, f, phi = A0, s0, f0, 0.0
    pred = model(tt, A, s, f, phi)
    ss_res = float(np.sum((iso - pred) ** 2))
    ss_tot = float(np.sum(iso ** 2)) or 1e-12
    wd = 2.0 * math.pi * f
    zeta = s / math.sqrt(s * s + wd * wd)
    return {"fn_hz": f, "zeta": zeta, "zeta_pct": 100.0 * zeta,
            "r2": 1.0 - ss_res / ss_tot, "dominant_frac": dominant_frac,
            "n_cycles": float(tt[-1] * f), "amp0_g": A}


def simulate_ringdown(design, *, article_mass_g: float,
                      cable_zeta: float = dts.DEFAULT_CABLE_ZETA) -> dict:
    """One drop, long window, ringdown fit on the raw post-release traces."""
    res = dts.simulate(design, article_mass_g=article_mass_g,
                       cable_zeta=cable_zeta, duration_s=RINGDOWN_DURATION_S)
    if not res["ok"]:
        return {"ok": False}
    contact = res["f_mat"] > 0.0
    if not contact.any():
        return {"ok": False}
    start = int(np.max(np.nonzero(contact)[0])) + int(
        RELEASE_MARGIN_S / dts.SIM_DT_S)
    rel = res["a_out_raw_g"][start:] - res["a_in_raw_g"][start:]
    fit = ringdown_fit(res["t"][start:], rel)
    return {"ok": True, **{f"sim_{k}": v for k, v in fit.items()},
            "sim_t180": res["t180"], "sim_e_rebound": res["e_rebound"],
            "sim_in_180_g": res["in_180_g"]}


def _printed_design(params: dict, target_mass_g: float):
    scale = dts.mass_model().solve_scale_for_printed_mass(dict(params),
                                                          target_mass_g)
    return scale_design(parameterization_to_design(params), scale)


# --------------------------------------------------------------------------
# parts
# --------------------------------------------------------------------------

def articles_sim(articles: pd.DataFrame,
                 cable_zeta: float = dts.DEFAULT_CABLE_ZETA) -> pd.DataFrame:
    """Simulated ringdown for every mapped article, at its weighed mass."""
    rows = []
    for _, r in articles[articles["mapped"]].iterrows():
        params = {n: float(r[n]) for n in PARAM_NAMES}
        design = _printed_design(params, float(r["mass_g"]))
        res = simulate_ringdown(design, article_mass_g=float(r["mass_g"]),
                                cable_zeta=cable_zeta)
        rows.append({"specimen": r["specimen"], **params,
                     "mass_g": float(r["mass_g"]),
                     "meas_fn_hz": r["fn_hz"], "meas_zeta_pct": r["zeta_pct"],
                     "meas_t180": r["t180"], "meas_e_rebound": r["e_rebound"],
                     **{k: v for k, v in res.items() if k != "ok"}})
    return pd.DataFrame(rows)


def damping_transfer(params: dict, article_mass_g: float,
                     grid=(0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8)
                     ) -> pd.DataFrame:
    """Sim modal zeta as a function of the material-damping input dial."""
    design = _printed_design(params, article_mass_g)
    rows = []
    for cz in grid:
        res = simulate_ringdown(design, article_mass_g=article_mass_g,
                                cable_zeta=cz)
        rows.append({"cable_zeta_in": cz,
                     **{k: v for k, v in res.items() if k != "ok"}})
    return pd.DataFrame(rows)


def sobol_response(n: int, target_mass_g: float,
                   cable_zeta: float = dts.DEFAULT_CABLE_ZETA,
                   seed: int = 0) -> pd.DataFrame:
    """Design response of the simulated ringdown at fixed material damping."""
    from scipy.stats import qmc

    box = {"R_mm": (25.0, 40.0), "H_mm": (60.0, 110.0),
           "twist_deg": (40.0, 80.0), "strut_d_mm": (6.0, 12.0),
           "cable_d_mm": (3.0, 5.5)}
    sob = qmc.Sobol(d=len(box), scramble=True, seed=seed)
    u = sob.random(n)
    lo = np.array([b[0] for b in box.values()])
    hi = np.array([b[1] for b in box.values()])
    pts = lo + u * (hi - lo)

    rows = []
    for x in pts:
        params = dict(zip(box.keys(), (float(v) for v in x)))
        try:
            design = _printed_design(params, target_mass_g)
            res = simulate_ringdown(design, article_mass_g=target_mass_g,
                                    cable_zeta=cable_zeta)
        except Exception:
            res = {"ok": False}
        rows.append({**params, **{k: v for k, v in res.items() if k != "ok"}})
    return pd.DataFrame(rows)


def invert_article_damping(articles_sim_df: pd.DataFrame,
                           articles: pd.DataFrame) -> pd.DataFrame:
    """Per article: the cable_zeta input that reproduces the measured zeta.

    Uses bisection in log space on the (monotone) transfer.  Where no input in
    [1e-3, 2.0] reaches the measured value, the bracketing end is reported and
    flagged.  Then re-scores t180/e_rebound at the fitted damping, so the
    'inject the measured ringdown loss' idea can be tested against the
    fixed-0.02 baseline.
    """
    rows = []
    for _, r in articles_sim_df.iterrows():
        target = r["meas_zeta_pct"]
        if not np.isfinite(target):
            continue
        params = {n: float(r[n]) for n in PARAM_NAMES}
        design = _printed_design(params, float(r["mass_g"]))

        def sim_zeta(cz: float) -> float:
            res = simulate_ringdown(design, article_mass_g=float(r["mass_g"]),
                                    cable_zeta=cz)
            return res.get("sim_zeta_pct", np.nan)

        lo, hi = 1e-3, 2.0
        z_lo, z_hi = sim_zeta(lo), sim_zeta(hi)
        converged = np.isfinite(z_lo) and np.isfinite(z_hi) \
            and (z_lo - target) * (z_hi - target) < 0
        if converged:
            for _ in range(12):
                mid = math.sqrt(lo * hi)
                z_mid = sim_zeta(mid)
                if not np.isfinite(z_mid):
                    converged = False
                    break
                if (z_mid - target) * (z_lo - target) < 0:
                    hi = mid
                else:
                    lo, z_lo = mid, z_mid
            cz_fit = math.sqrt(lo * hi)
        else:
            cz_fit = lo if abs(z_lo - target) < abs(z_hi - target) else hi
        res = simulate_ringdown(design, article_mass_g=float(r["mass_g"]),
                                cable_zeta=cz_fit)
        rows.append({"specimen": r["specimen"], "meas_zeta_pct": target,
                     "cable_zeta_fit": cz_fit, "converged": bool(converged),
                     "sim_zeta_pct_at_fit": res.get("sim_zeta_pct", np.nan),
                     "sim_fn_hz_at_fit": res.get("sim_fn_hz", np.nan),
                     "sim_t180_at_fit": res.get("sim_t180", np.nan),
                     "sim_e_rebound_at_fit": res.get("sim_e_rebound", np.nan),
                     "meas_t180": r["meas_t180"],
                     "meas_e_rebound": r["meas_e_rebound"],
                     "sim_t180_base": r["sim_t180"],
                     "sim_e_rebound_base": r["sim_e_rebound"]})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# figure
# --------------------------------------------------------------------------

def make_figure(articles, art_sim, transfer, sobol, invert, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12.5, 9.5))

    # (a) measured vs simulated zeta per article
    ax = axes[0, 0]
    m = art_sim.dropna(subset=["meas_zeta_pct"]).sort_values("meas_zeta_pct")
    xpos = np.arange(len(m))
    sd = articles.set_index("specimen").loc[m["specimen"], "zeta_pct_sd"]
    ax.bar(xpos - 0.2, m["meas_zeta_pct"], width=0.4, yerr=sd.fillna(0.0),
           label="measured", color="#3465a4", capsize=3)
    ax.bar(xpos + 0.2, m["sim_zeta_pct"], width=0.4,
           label="simulated (cable_zeta = 0.02)", color="#f57900")
    ax.set_xticks(xpos, m["specimen"], rotation=30)
    ax.set_ylabel("ringdown damping ratio (%)")
    ax.set_title("(a) measured vs simulated ringdown damping")
    ax.legend()

    # (b) measured vs simulated fn
    ax = axes[0, 1]
    ax.bar(xpos - 0.2, m["meas_fn_hz"], width=0.4, color="#3465a4",
           label="measured")
    ax.bar(xpos + 0.2, m["sim_fn_hz"], width=0.4, color="#f57900",
           label="simulated")
    ax.set_xticks(xpos, m["specimen"], rotation=30)
    ax.set_ylabel("ringdown frequency (Hz)")
    ax.set_title("(b) the mode families do not match")
    ax.legend()

    # (c) input dial transfer
    ax = axes[1, 0]
    ax.plot(transfer["cable_zeta_in"] * 100.0, transfer["sim_zeta_pct"],
            "o-", color="#f57900", label="simulated modal zeta")
    zmin = float(np.nanmin(articles["zeta_pct"]))
    zmax = float(np.nanmax(articles["zeta_pct"]))
    ax.axhspan(zmin, zmax, color="#3465a4", alpha=0.15,
               label=f"measured band ({zmin:.1f} to {zmax:.1f} %)")
    ax.set_xscale("log")
    ax.set_xlabel("cable_zeta input (%) [material damping dial]")
    ax.set_ylabel("simulated modal zeta (%)")
    ax.set_title("(c) sim zeta vs the material-damping input (S0 design)")
    ax.legend()

    # (d) design response at fixed material damping
    ax = axes[1, 1]
    ok = sobol.dropna(subset=["sim_zeta_pct"])
    ax.scatter(ok["sim_fn_hz"], ok["sim_zeta_pct"], s=18, alpha=0.7,
               color="#f57900", label=f"Sobol designs (n = {len(ok)})")
    mm = m.dropna(subset=["meas_fn_hz"])
    ax.scatter(mm["meas_fn_hz"], mm["meas_zeta_pct"], s=45, marker="s",
               color="#3465a4", label="measured articles")
    ax.set_xlabel("ringdown frequency (Hz)")
    ax.set_ylabel("ringdown damping ratio (%)")
    ax.set_title("(d) design response, cable_zeta fixed at 0.02")
    ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n-sobol", type=int, default=48)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    OUT.mkdir(exist_ok=True)

    articles = load_articles()
    meas = measured_correlations(articles)
    meas.to_csv(OUT / "zeta_measured_correlations.csv", index=False)
    print("measured zeta_pct correlations:")
    print(meas.to_string(index=False))

    print("\nsimulating mapped articles ...")
    art_sim = articles_sim(articles)
    art_sim.to_csv(OUT / "zeta_articles_sim.csv", index=False)
    print(art_sim[["specimen", "meas_fn_hz", "sim_fn_hz", "meas_zeta_pct",
                   "sim_zeta_pct", "sim_r2"]].to_string(index=False))

    print("\ndamping-input transfer (S0 design) ...")
    transfer = damping_transfer(dict(dts.S0_BASE_PARAMS),
                                dts.DEFAULT_PRINTED_MASS_TARGET_G)
    transfer.to_csv(OUT / "zeta_damping_transfer.csv", index=False)
    print(transfer[["cable_zeta_in", "sim_zeta_pct", "sim_fn_hz",
                    "sim_t180", "sim_e_rebound", "sim_r2"]].to_string(index=False))

    print(f"\nSobol design response (n = {args.n_sobol}) ...")
    sobol = sobol_response(args.n_sobol, dts.DEFAULT_PRINTED_MASS_TARGET_G,
                           seed=args.seed)
    sobol.to_csv(OUT / "zeta_sobol_response.csv", index=False)
    ok = sobol.dropna(subset=["sim_zeta_pct"])
    print(f"  sim zeta span: {ok['sim_zeta_pct'].min():.2f} to "
          f"{ok['sim_zeta_pct'].max():.2f} %; "
          f"fn span {ok['sim_fn_hz'].min():.0f} to {ok['sim_fn_hz'].max():.0f} Hz")

    print("\nper-article damping inversion ...")
    invert = invert_article_damping(art_sim, articles)
    invert.to_csv(OUT / "zeta_article_inversion.csv", index=False)
    print(invert.to_string(index=False))

    # cross-checks: does the sim ringdown carry any measured signal?
    from scipy import stats
    checks = []
    m = art_sim.dropna(subset=["meas_zeta_pct", "sim_zeta_pct"])
    rho, p = stats.spearmanr(m["sim_zeta_pct"], m["meas_zeta_pct"])
    checks.append({"check": "spearman(sim_zeta, meas_zeta)", "n": len(m),
                   "value": float(rho), "p": float(p)})
    mf = art_sim.dropna(subset=["meas_fn_hz", "sim_fn_hz"])
    rho, p = stats.spearmanr(mf["sim_fn_hz"], mf["meas_fn_hz"])
    checks.append({"check": "spearman(sim_fn, meas_fn)", "n": len(mf),
                   "value": float(rho), "p": float(p)})
    for axis in PARAM_NAMES:
        rho, p = stats.spearmanr(ok[axis], ok["sim_zeta_pct"])
        checks.append({"check": f"spearman(sobol {axis}, sim_zeta)",
                       "n": len(ok), "value": float(rho), "p": float(p)})
    d_t180 = (invert["sim_t180_at_fit"] - invert["sim_t180_base"]).abs() \
        / invert["sim_t180_base"]
    d_ereb = (invert["sim_e_rebound_at_fit"]
              - invert["sim_e_rebound_base"]).abs() / invert["sim_e_rebound_base"]
    checks.append({"check": "median |dt180|/t180 from zeta injection",
                   "n": len(invert), "value": float(d_t180.median()),
                   "p": float(d_t180.max())})
    checks.append({"check": "median |de_reb|/e_reb from zeta injection",
                   "n": len(invert), "value": float(d_ereb.median()),
                   "p": float(d_ereb.max())})
    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(OUT / "zeta_cross_checks.csv", index=False)
    print("\ncross-checks (p column holds max for the injection rows):")
    print(checks_df.to_string(index=False))

    make_figure(articles, art_sim, transfer, sobol, invert,
                OUT / "zeta_analysis.png")
    print(f"\nwrote {OUT / 'zeta_analysis.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
