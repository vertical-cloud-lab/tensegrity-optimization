#!/usr/bin/env python3
"""1sne plate 1 (10-17): the CH5 cable fault drop by drop, and the
corny2 / corny7 / corny8 article spread (PR #86, @me-madsen, 10-19).

Two follow-ups to the 1sne check-in (``drop_test_1sne_checkin_analysis.py``):

1. **CH5 fault timeline.**  The CH5 cable has since broken.  Was it already
   disconnected by the fault hour (17:18 -> 18:17), or loose and working
   part of the time?  Each of the 180 captures is placed in recording order
   with three independent witnesses:
   - did the record hold an impact (the TP4 series table's CH4 peak);
   - did CH5 behave like a sensor (baseline steps and plateaus in the raw
     CH5 trace after the impact window, where a healthy capture only rings);
   - when did the trigger fire relative to the hoist's automatic ~41 s
     drop cadence (TP4 event times, 1 s resolution; a least-squares fit per
     cadence segment, ``t = a + P * slot + delta * [no-impact capture]``,
     with the impact-bearing captures as anchors).
2. **Article spread per design.**  Per article ("version": the first article
   from the round-4 plate plus the three plate-1 copies), T180 mean, sd and
   variance over the stabilized drops under two readings: all valid drops
   (the standing pipeline) and clean drops (seat gauge T1000/T180 < 1.145
   and recorded outside the CH5-fault hour).  Then the between-article
   spread per design, and what differs between the two prints: strut
   colour (issue #98 photos), slicer settings (the two project files
   compared key by key, when ``--r4-3mf``/``--p1-3mf`` are given) and
   build-plate position (PR #102 plate files).

Outputs (``data/drop-tests/1sne-checkin/figures/ch5-replicates/``):
``17_ch5_drop_strip.png``, ``18_ch5_fault_evidence.png``,
``19_corny2_t180_by_article.png``, ``20_corny7_t180_by_article.png``,
``21_corny8_t180_by_article.png``, ``22_plate_placement.png``,
``23_print_photos.jpg`` (with ``--photos``) and ``ch5_replicates.json``.

Usage:
    python scripts/analysis/drop_test_1sne_ch5_replicates_analysis.py \\
        --raw ROOT [--photos DIR] [--r4-3mf FILE --p1-3mf FILE]

ROOT holds one subfolder per 1sne session with the ``*_Signal<k>.csv``
captures (Box ids in ``data/drop-tests/1sne-checkin/raw/<id>/box-ids.json``).
DIR caches the issue #98 print-log photos (fetched from the public
attachment URLs below if missing).  The 3mf files are the round-4 project
at 9fba359 (``bo/slices/t3-prism-bo-round4.H2D-MM-PLAstruts-TPUcables.3mf``)
and the replicate plate-1 project
(``bo/replicate-study/t3-prism-replicate-sne-plate1.H2D-MM-PLAstruts-TPUcables.3mf``),
both on the PR #102 branch.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402
from drop_test_abc123_blind_analysis import parse_capture  # noqa: E402
from drop_test_1sne_checkin_analysis import (  # noqa: E402
    COLOR, DESIGNS, DIGIT, INK, INK2, MUTED, style)
from drop_test_round3_per_design_comparison import GAUGE_SUSPECT  # noqa: E402

OUT = DATA / "1sne-checkin"
FIG = OUT / "figures" / "ch5-replicates"
CORNY = DATA / "corny-checkin"

FIRST = {"corny2": "corny2", "corny7": "corny7", "corny8": "corny8"}
COPIES = {d: [f"1sne{d[-1]}{k}" for k in (1, 2, 3)] for d in DESIGNS}
BLOCK_DESIGNS = ("corny2", "corny7", "corny8")   # figure numbering 19/20/21
DIGIT_DESIGN = DIGIT

# Build-plate positions (x, y in mm; y = back of the bed).  Round-4 plate:
# PR #102 bo/t3-prism-bo-round4-plate.json @ 9fba359 (the file the corny
# plate was printed from), corny label -> trial from the round-4 print key.
# Plate 1: bo/replicate-study/t3-prism-replicate-print-key.csv.
R4_PLATE = {  # corny label: (trial, x, y, row-col)
    "corny1": (42, 246.6, 255.0, "back-right"), "corny2": (38, 246.6, 162.8, "middle-right"),
    "corny3": (45, 246.6, 67.8, "front-right"), "corny4": (44, 165.7, 255.0, "back-center"),
    "corny5": (40, 165.7, 162.8, "middle-center"), "corny6": (41, 165.7, 67.8, "front-center"),
    "corny7": (37, 69.8, 255.0, "back-left"), "corny8": (39, 69.8, 162.8, "middle-left"),
    "corny9": (43, 69.8, 67.8, "front-left")}
P1_PLATE = {
    "1sne71": (37, 66.9, 254.5, "back-left"), "1sne81": (39, 162.3, 254.5, "back-center"),
    "1sne21": (38, 244.1, 254.5, "back-right"), "1sne82": (39, 67.2, 160.0, "middle-left"),
    "1sne22": (38, 149.0, 160.0, "middle-center"), "1sne72": (37, 230.4, 160.0, "middle-right"),
    "1sne23": (38, 53.2, 65.5, "front-left"), "1sne73": (37, 134.6, 65.5, "front-center"),
    "1sne83": (39, 230.1, 65.5, "front-right")}
WIPE_TOWER = (287.0, 110.0)
BED = (350.0, 320.0)

# Print-log photos (issue #98: corny first articles posted 09-11 by @ctrhjk,
# comment 5637649574; plate-1 copies posted 10-17, comment 6240858848).
PHOTO_URLS = {
    "corny2": "https://github.com/user-attachments/assets/0ef28731-c20c-4cec-b85c-871e5d707a56",
    "corny7": "https://github.com/user-attachments/assets/3c0732df-8a09-402c-ad24-23e62ba04c88",
    "corny8": "https://github.com/user-attachments/assets/5c8dfc43-e902-4ba6-8a6c-318212cc70a2",
    "1sne21": "https://github.com/user-attachments/assets/bb8cbe7b-12cd-4d9f-9fc4-b05dcac556d6",
    "1sne22": "https://github.com/user-attachments/assets/504db558-705b-4b07-8825-4ab1ea758a95",
    "1sne23": "https://github.com/user-attachments/assets/e69788e6-8fb2-45af-b29e-c7efe4f4dcf0",
    "1sne71": "https://github.com/user-attachments/assets/e5836553-10fa-4c73-9725-4f79ec8fc1da",
    "1sne72": "https://github.com/user-attachments/assets/0e3e86b9-432b-4527-8fb1-ac0d51dc136f",
    "1sne73": "https://github.com/user-attachments/assets/ff3977f1-1924-4283-b9e7-86136a3e8542",
    "1sne81": "https://github.com/user-attachments/assets/91dcbdae-f082-484f-996e-eb8794b41ddd",
    "1sne82": "https://github.com/user-attachments/assets/ed79ea96-51f1-4391-af15-5b134aaae59e",
    "1sne83": "https://github.com/user-attachments/assets/5d3e9af9-2a24-4f9a-a029-8773462f8a47",
}
# Strut (PLA) colour per print batch, read off the issue #98 photos: the
# switch from white to black happened between the corny print (09-11) and
# the dran3 reprint (09-29), the first black batch.
STRUT_PLA = {"corny": "white", "1sne": "black"}
BATCH_PLA = {"drran (09-02)": "white", "2dran (09-05)": "white", "corny (09-11)": "white",
             "dran3 (09-29)": "black", "1sne/2sne/3sne (10-17)": "black"}

PERIOD0 = 41.35      # s, the hoist's automatic cycle (fits 41.2-41.5 within a session)
OFF_CADENCE_S = 3.0  # an interval this far from a whole number of cycles is not a drop
LEVEL = {"healthy": "#0ca30c"}
NO_IMPACT, FAULT_IMPACT = "#b8b6ae", "#7a5ad6"


# --------------------------------------------------------------------------
# CH5 per-capture metrics from the raw trace
# --------------------------------------------------------------------------
def ch5_metrics(path: Path) -> dict:
    t, ch, _ = parse_capture(path)
    dt = float(np.median(np.diff(t)))
    x = ch[:, 3]
    w = int(0.005 / dt)
    i15 = int(0.015 / dt)
    meds = np.array([np.median(x[i:i + w]) for i in range(i15, len(x) - w + 1, w)])
    return {
        "session": path.parent.name, "signal": int(path.stem.split("Signal")[1]),
        # largest jump between consecutive 5 ms medians, 15-100 ms: a healthy
        # channel only rings around its baseline here; a bad contact steps
        "ch5_step_g": float(np.abs(np.diff(meds)).max()),
        # where the channel sits before the trigger vs at the end of the record
        "ch5_pre_g": float(np.median(x[:int(0.0019 / dt)])),
        "ch5_tail_g": float(np.median(x[int(0.070 / dt):])),
        "ch5_max_sample_jump_g": float(np.abs(np.diff(x[int(0.012 / dt):])).max()),
    }


def raw_metrics(raw: Path, procs: int) -> dict:
    files = sorted(raw.glob("*/*_Signal*.csv"))
    with Pool(procs) as pool:
        rows = pool.map(ch5_metrics, files)
    return {(r["session"], r["signal"]): r for r in rows}


# --------------------------------------------------------------------------
# trigger timing vs the hoist's drop cadence
# --------------------------------------------------------------------------
def whole_cycles(dt: float) -> int | None:
    """Number of hoist cycles in an interval, or None if it is not a whole
    number of cycles (within 3 s)."""
    k = round(dt / PERIOD0)
    return k if k >= 1 and abs(dt - k * PERIOD0) <= OFF_CADENCE_S else None


def cadence_segments(ev: list[dict]) -> list[dict]:
    """Assign each event of one session to a cadence slot.

    Events whose spacing from the segment's last on-cadence event is not a
    whole number of cycles are triggers between drops, unless the next event
    confirms a new phase (a restarted hoist cycle), which opens a new
    segment."""
    t = [e["t"] for e in ev]
    seg, last = 0, 0
    out = [{**ev[0], "segment": 0, "slot": 0, "off_cadence": False}]
    for i in range(1, len(ev)):
        k = whole_cycles(t[i] - t[last])
        if k is not None:
            out.append({**ev[i], "segment": seg, "slot": out[last]["slot"] + k,
                        "off_cadence": False})
            last = i
        elif i + 1 < len(ev) and whole_cycles(t[i + 1] - t[i]) is not None:
            seg, last = seg + 1, i               # a new phase: restarted cycle
            out.append({**ev[i], "segment": seg, "slot": 0, "off_cadence": False})
        else:                                    # a trigger between drops
            out.append({**ev[i], "segment": seg, "slot": None, "off_cadence": True})
    return out


def fit_offset(evs: list[dict]) -> dict | None:
    """t = a + P * slot + delta * no_impact, over one cadence segment."""
    on = [e for e in evs if not e["off_cadence"]]
    imp = [e for e in on if e["impact"]]
    bad = [e for e in on if not e["impact"]]
    if len(imp) < 2 or len(bad) < 2:
        return None
    s = np.array([e["slot"] for e in on], float)
    y = np.array([e["t"] for e in on]) - on[0]["t"]
    d = np.array([0.0 if e["impact"] else 1.0 for e in on])
    X = np.column_stack([np.ones_like(s), s, d])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    dof = len(y) - 3
    s2 = float(res @ res / dof)
    cov = s2 * np.linalg.inv(X.T @ X)
    return {"n_impact": len(imp), "n_no_impact": len(bad), "period_s": float(beta[1]),
            "delta_s": float(beta[2]), "delta_se_s": float(np.sqrt(cov[2, 2])),
            "resid_sd_s": float(np.sqrt(s2))}


def timing(cen: list[dict]) -> dict:
    by = {}
    for r in cen:
        by.setdefault(r["session"], []).append(r)
    out, fits = {}, []
    for s, rows in by.items():
        rows = sorted(rows, key=lambda r: r["signal"])
        ev = [{"signal": r["signal"], "t": datetime.fromisoformat(r["local_time"]).timestamp(),
               "impact": r["class"] != "mistimed"} for r in rows]
        segs = cadence_segments(ev)
        sess = {"events": [{k: e[k] for k in ("signal", "segment", "slot", "off_cadence", "impact")}
                           for e in segs], "segments": {}}
        for g in sorted({e["segment"] for e in segs}):
            f = fit_offset([e for e in segs if e["segment"] == g])
            sess["segments"][g] = f
            if f is not None:
                fits.append((s, g, f))
        # residual of every event against the impact-anchored cadence of its
        # segment (None when the segment has fewer than two impact anchors)
        for g in sess["segments"]:
            on = [e for e in segs if e["segment"] == g and not e["off_cadence"]]
            imp = [e for e in on if e["impact"]]
            if len(imp) >= 2:
                fit = sess["segments"][g]
                # period from every on-cadence event (the hoist cycle does not
                # care whether the trigger was good); phase from the impacts
                P = fit["period_s"] if fit else np.polyfit([e["slot"] for e in on],
                                                          [e["t"] for e in on], 1)[0]
                a = np.mean([e["t"] - P * e["slot"] for e in imp])
                for e, rec in zip(segs, sess["events"]):
                    if e["segment"] != g:
                        continue
                    k = e["slot"] if e["slot"] is not None else round((e["t"] - a) / P)
                    rec["resid_s"] = float(e["t"] - (a + P * k))
        out[s] = sess
    w = np.array([1 / f["delta_se_s"] ** 2 for _, _, f in fits])
    dl = np.array([f["delta_s"] for _, _, f in fits])
    pooled = {"delta_s": float((w * dl).sum() / w.sum()), "se_s": float(np.sqrt(1 / w.sum())),
              "segments": [f"{s}:{g}" for s, g, _ in fits]}
    return {"sessions": out, "fits": {f"{s}:{g}": f for s, g, f in fits}, "pooled": pooled}


# --------------------------------------------------------------------------
# per-article statistics
# --------------------------------------------------------------------------
def stats(v: np.ndarray) -> dict | None:
    if len(v) == 0:
        return None
    sd = float(np.std(v, ddof=1)) if len(v) > 1 else None
    return {"n": int(len(v)), "mean": float(v.mean()), "sd": sd,
            "var": None if sd is None else sd ** 2,
            "cv_pct": None if sd is None else 100 * sd / float(v.mean()),
            "min": float(v.min()), "max": float(v.max())}


def article_drops(cen: list[dict], window: tuple[str, str]) -> dict:
    """Stabilized drops per article, flagged for knock and the fault hour."""
    loc = {(r["session"], r["signal"]): r["local_time"] for r in cen}
    arts = {}
    cm = json.loads((OUT / "figures" / "campaign_metrics.json").read_text())
    for s, v in cm["specimens"].items():
        arts[s] = [{"signal": r["signal"], "t180": r["t180"], "gauge": r["t1000"] / r["t180"],
                    "local_time": loc[(s, r["signal"])],
                    "in_fault": window[0] <= loc[(s, r["signal"])] <= window[1]}
                   for r in v["rows"]]
    cm0 = json.loads((CORNY / "figures" / "campaign_metrics.json").read_text())
    for d in DESIGNS:
        v = cm0["specimens"][d]
        arts[d] = [{"signal": r["signal"], "t180": r["t180"], "gauge": r["t1000"] / r["t180"],
                    "local_time": None, "in_fault": False} for r in v["rows"]]
    return arts


def readings(drops: list[dict]) -> dict:
    t = np.array([x["t180"] for x in drops])
    clean = np.array([x["gauge"] < GAUGE_SUSPECT and not x["in_fault"] for x in drops])
    seat = np.array([x["gauge"] < GAUGE_SUSPECT for x in drops])
    return {"all_valid": stats(t), "clean": stats(t[clean]), "gauge_clean_any_time": stats(t[seat]),
            "n_knock": int((~seat).sum()), "n_in_fault": int(sum(x["in_fault"] for x in drops))}


def design_spread(rd: dict, d: str, key: str, pooled=None) -> dict:
    """Between-article spread of the article means, and the drop-level
    decomposition (pooled within-article variance vs between-article)."""
    def block(ids):
        r = [(i, rd[i][key]) for i in ids if rd[i][key] is not None]
        if len(r) < 2:
            return None
        m = np.array([x["mean"] for _, x in r])
        n = np.array([x["n"] for _, x in r])
        within = [(x["n"] - 1, x["var"]) for _, x in r if x["var"] is not None]
        dof = sum(k for k, _ in within)
        w_var = sum(k * v for k, v in within) / dof if dof else None
        b_var = float(np.var(m, ddof=1))
        comp = None if w_var is None else max(b_var - w_var * float(np.mean(1 / n)), 0.0)
        return {"articles": [i for i, _ in r], "means": [round(float(x), 5) for x in m],
                "n_drops": [int(k) for k in n],
                "mean_of_means": float(m.mean()), "sd_between": float(np.sqrt(b_var)),
                "var_between": b_var, "range": float(m.max() - m.min()),
                "within_pooled_sd": None if w_var is None else float(np.sqrt(w_var)),
                "within_pooled_var": w_var,
                "between_component_sd": None if comp is None else float(np.sqrt(comp))}
    copies = COPIES[d]
    out = {"copies": block(copies), "copies_plus_first": block([FIRST[d]] + copies)}
    out["copies_pooled_drops"] = None if pooled is None else pooled(copies, key)
    first = rd[FIRST[d]][key]
    cm = [rd[i][key]["mean"] for i in copies if rd[i][key] is not None]
    if first is not None and cm:
        out["copies_with_reading"] = [i for i in copies if rd[i][key] is not None]
        out["first_minus_copies"] = first["mean"] - float(np.mean(cm))
        out["copies_vs_first_pct"] = 100 * (float(np.mean(cm)) / first["mean"] - 1)
    return out


# --------------------------------------------------------------------------
# slicer settings: round-4 project vs plate-1 project
# --------------------------------------------------------------------------
def compare_3mf(r4: Path, p1: Path) -> dict:
    def load(p):
        with zipfile.ZipFile(p) as z:
            cfg = json.loads(z.read("Metadata/project_settings.config"))
            ms = z.read("Metadata/model_settings.config").decode()
        parts = {}
        for body in re.findall(r"<object id=\"\d+\">(.*?)</object>", ms, re.S):
            name = re.search(r'key="name" value="([^"]+)"', body).group(1)
            for p_ in re.findall(r'<part id="\d+" subtype="normal_part">(.*?)</part>', body, re.S):
                pn = re.search(r'key="name" value="([^"]+)"', p_).group(1)
                dens = re.search(r'key="sparse_infill_density" value="([^"]+)"', p_)
                parts.setdefault(name, {})[pn] = dens.group(1) if dens else None
        return cfg, parts
    a, pa = load(r4)
    b, pb = load(p1)
    keys = sorted(set(a) | set(b))
    diff = [k for k in keys if a.get(k) != b.get(k)]
    show = ("nozzle_temperature", "nozzle_temperature_initial_layer", "textured_plate_temp",
            "textured_plate_temp_initial_layer", "filament_settings_id",
            "filament_max_volumetric_speed", "filament_flow_ratio", "fan_max_speed",
            "print_settings_id", "layer_height", "wall_loops", "curr_bed_type")
    trial = {"1sne7": "Trial 37", "1sne8": "Trial 39", "1sne2": "Trial 38"}
    infill = {}
    for name, parts in pb.items():
        ref = pa[trial[name[:5]]]
        infill[name] = {"plate1": sorted(parts.values()), "round4": sorted(ref.values()),
                        "same": sorted(parts.values()) == sorted(ref.values())}
    return {"n_keys": len(keys), "n_keys_differing": len(diff), "differing": diff,
            "settings": {k: a.get(k) for k in show},
            "per_part_infill_same_as_round4": all(v["same"] for v in infill.values()),
            "per_part_infill": infill}


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def fig_strip(cen, tim, window, path):
    """The evening as a drop strip: one row per session, one cell per TP4
    event, in recording order."""
    sessions = []
    for r in cen:
        if r["session"] not in sessions:
            sessions.append(r["session"])
    by = {s: {r["signal"]: r for r in cen if r["session"] == s} for s in sessions}
    off = {(s, e["signal"]) for s, v in tim["sessions"].items() for e in v["events"]
           if e["off_cadence"]}
    fig, ax = plt.subplots(figsize=(13, 5.3))
    for sp in ax.spines.values():
        sp.set_visible(False)
    for row, s in enumerate(sessions):
        y = len(sessions) - 1 - row
        evs = by[s]
        first, last = min(evs.values(), key=lambda r: r["signal"]), max(evs.values(),
                                                                         key=lambda r: r["signal"])
        ax.text(-0.6, y, f"{s}  ({DIGIT_DESIGN[s[4]]})", ha="right", va="center", fontsize=8.5,
                color=INK)
        ax.text(26.2, y, f"{first['local_time'][11:16]}-{last['local_time'][11:16]}",
                ha="left", va="center", fontsize=8, color=INK2)
        for k in range(1, max(evs) + 1):
            if k not in evs:
                ax.add_patch(plt.Rectangle((k - 0.4, y - 0.32), 0.8, 0.64, fill=False,
                                           ec=MUTED, lw=0.8, ls=(0, (2, 2))))
                continue
            r = evs[k]
            inw = window[0] <= r["local_time"] <= window[1]
            if (s, k) in off:
                ax.scatter(k, y, marker="*", s=120, color="#d03b3b", zorder=3)
            elif r["class"] == "mistimed":
                ax.scatter(k, y, marker="x", s=46, lw=1.6, color=MUTED, zorder=3)
            else:
                ax.scatter(k, y, marker="D" if inw else "s", s=58 if inw else 62, zorder=3,
                           color=FAULT_IMPACT if inw else INK2)
    # shade the fault hour, from its first mistimed capture to its last
    for s in sessions:
        y = len(sessions) - 1 - sessions.index(s)
        ks = [k for k, r in by[s].items() if window[0] <= r["local_time"] <= window[1]]
        if ks:
            ax.add_patch(plt.Rectangle((min(ks) - 0.5, y - 0.45), max(ks) - min(ks) + 1, 0.9,
                                       color="#f6e3e3", lw=0, zorder=0))
    y22 = len(sessions) - 1 - sessions.index("1sne22")
    ax.text(25.5, y22 + 0.12, f"CH5 fault hour\n{window[0][11:19]}-\n{window[1][11:19]}",
            ha="right", va="center", fontsize=7.5, color="#8f2a2a")
    ax.text(14.5, len(sessions) - 1 - sessions.index("1sne72") - 0.47,
            "events 10-14 missing from the export; the drop cadence restarted ~8 s out of phase",
            fontsize=7, color=INK2, va="top", ha="center")
    ax.text(5.5, len(sessions) - 1 - sessions.index("1sne83") - 0.47,
            "1 h 44 min pause after event 3, still clean afterwards", fontsize=7, color=INK2,
            va="top", ha="center")
    ax.set_xlim(-6.2, 29)
    ax.set_ylim(-0.9, len(sessions) + 0.1)
    ax.set_xticks(range(1, 26))
    ax.tick_params(axis="x", labelsize=7.5, colors=INK2)
    ax.set_yticks([])
    ax.set_xlabel("TP4 event number within the session (one event per drop, plus stray triggers)",
                  fontsize=8.5, color=INK)
    handles = [Line2D([], [], ls="", marker="s", color=INK2, ms=7,
                      label="impact recorded, CH5 healthy"),
               Line2D([], [], ls="", marker="D", color=FAULT_IMPACT, ms=6.5,
                      label="impact recorded inside the fault hour (CH5 suspect)"),
               Line2D([], [], ls="", marker="x", color=MUTED, ms=7, mew=1.6,
                      label="no impact in the record (trigger fired during the fall)"),
               Line2D([], [], ls="", marker="*", color="#d03b3b", ms=10,
                      label="trigger between drops (nothing hit the plate)")]
    ax.legend(handles=handles, fontsize=7.8, frameon=False, loc="lower center", ncol=2,
              bbox_to_anchor=(0.5, -0.30))
    ax.set_title("10-17, every capture in recording order: CH5 was intermittent for one hour, "
                 "then recovered fully", fontsize=10.5, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_timeline(cen, rawm, tim, window, path):
    idx = np.arange(len(cen))
    fig, axes = plt.subplots(3, 1, figsize=(13, 9.2), sharex=True,
                             gridspec_kw={"height_ratios": [1.15, 1.25, 1.25]})
    sess = [r["session"] for r in cen]
    spans, start = [], 0
    for k in range(1, len(sess) + 1):
        if k == len(sess) or sess[k] != sess[start]:
            spans.append((sess[start], start, k - 1))
            start = k
    i0 = next(i for i, r in enumerate(cen) if r["local_time"] >= window[0])
    i1 = max(i for i, r in enumerate(cen) if r["local_time"] <= window[1])
    for ax in axes:
        for j, (s, a, b) in enumerate(spans):
            if j % 2 == 0:
                ax.axvspan(a - 0.5, b + 0.5, color="#f0efec", lw=0, zorder=0)
        ax.axvspan(i0 - 0.5, i1 + 0.5, color="#f6e3e3", lw=0, zorder=0, alpha=0.75)
        style(ax)
    imp = np.array([r["class"] != "mistimed" for r in cen])
    inw = np.array([window[0] <= r["local_time"] <= window[1] for r in cen])

    ax = axes[0]
    y = np.array([max(abs(r["tp4_ch4_g"]), 1.0) for r in cen])
    ax.scatter(idx[imp & ~inw], y[imp & ~inw], s=16, color=INK2, zorder=3,
               label="impact in the record, CH5 healthy")
    ax.scatter(idx[imp & inw], y[imp & inw], s=26, marker="D", color=FAULT_IMPACT, zorder=3,
               label="impact in the record, inside the fault hour")
    ax.scatter(idx[~imp], y[~imp], s=26, marker="x", lw=1.2, color=MUTED, zorder=3,
               label="no impact in the record (mistimed trigger)")
    ax.scatter([], [], marker="*", s=60, color="#d03b3b", label="trigger between drops")
    ax.axhline(150, color="#c3c2b7", lw=0.9, ls="--", zorder=1)
    ax.text(len(cen) - 0.5, 175, "150 G live check", ha="right", fontsize=7, color=INK2)
    ax.set_yscale("log")
    ax.set_ylim(3, 2.5e4)
    ax.set_ylabel("top sensor peak\n(TP4 CH4, G)", fontsize=9, color=INK)
    for s, a, b in spans:
        ax.text((a + b) / 2, 3.3e4, f"{s}\n{cen[a]['local_time'][11:16]}", ha="center",
                va="bottom", fontsize=7.5, color=INK2)
    ax.text((i0 + i1) / 2, 1.0e4, f"CH5 fault hour {cen[i0]['local_time'][11:16]}-"
            f"{cen[i1]['local_time'][11:16]}: {int((~imp[i0:i1 + 1]).sum())} of "
            f"{i1 - i0 + 1} records hold no impact, {int(imp[i0:i1 + 1].sum())} do",
            ha="center", fontsize=8, color="#8f2a2a")
    handles, labels = ax.get_legend_handles_labels()

    ax = axes[1]
    st = np.array([rawm[(r["session"], r["signal"])]["ch5_step_g"] for r in cen])
    ax.scatter(idx[imp & ~inw], st[imp & ~inw], s=16, color=INK2, zorder=3)
    ax.scatter(idx[imp & inw], st[imp & inw], s=26, marker="D", color=FAULT_IMPACT, zorder=3)
    ax.scatter(idx[~imp], st[~imp], s=26, marker="x", lw=1.2, color=MUTED, zorder=3)
    healthy = st[imp & ~inw]
    ax.axhspan(0.05, healthy.max(), color=LEVEL["healthy"], alpha=0.08, lw=0)
    ax.text(1, healthy.max() * 1.15, f"healthy captures: {healthy.min():.1f}-{healthy.max():.1f} G "
            "(post-impact ringing and the brake catch)", fontsize=7, color=INK2)
    ax.set_yscale("log")
    ax.set_ylim(0.1, 3000)
    ax.set_ylabel("CH5 baseline step\n15-100 ms (G)", fontsize=9, color=INK)

    ax = axes[2]
    res = []
    for r in cen:
        ev = next(e for e in tim["sessions"][r["session"]]["events"] if e["signal"] == r["signal"])
        res.append((ev.get("resid_s"), ev["off_cadence"]))
    ylo, yhi = -2.6, 2.4
    stars = []
    for i, (rv, off) in enumerate(res):
        if off:
            ax.scatter(i, ylo + 0.3, s=70, marker="*", color="#d03b3b", zorder=4)
            stars.append(i)
            continue
        if rv is None:
            continue
        m, c, sz = (("o", INK2, 16) if imp[i] and not inw[i] else
                    ("D", FAULT_IMPACT, 26) if imp[i] else ("x", MUTED, 26))
        ax.scatter(i, rv, s=sz, marker=m, color=c, lw=1.2, zorder=3)
    ax.axhline(0, color="#c3c2b7", lw=0.9)
    ax.axhspan(-0.56, 0, color="#2a78d6", alpha=0.10, lw=0)
    ax.text(1, -1.55, "blue band: the 0.56 s free fall before impact. The sawtooth is the TP4's "
            "1 s timestamp rounding.", fontsize=7, color=INK2, va="center")
    for i in stars:
        r = cen[i]
        ax.text(i, ylo + 0.62, f"{r['session']} ev {r['signal']}", ha="center", fontsize=6.2,
                color=INK2, rotation=90, va="bottom")
    ax.text(max(stars) + 2, ylo + 0.3, "red stars: triggers between drops", fontsize=7,
            color=INK2, va="center")
    pooled = tim["pooled"]
    j72 = [i for i, r in enumerate(cen) if r["session"] == "1sne72" and r["signal"] >= 15]
    ax.text(np.mean(j72), 1.35, "1sne72 ev 15-25: no impact\nanchors (cadence restarted)",
            ha="center", fontsize=6.5, color=INK2, va="center")
    ax.text(1, yhi - 0.15, "trigger time minus the drop cadence anchored on the impacts. No-impact "
            f"triggers fire {abs(pooled['delta_s']):.2f} ± {pooled['se_s']:.2f} s before the impact "
            "on average\n(least squares over four sessions): the trigger fired during the fall, "
            "not at the impact.", fontsize=7.5, color=INK2, va="top")
    ax.set_ylim(ylo, yhi)
    ax.set_ylabel("trigger timing vs\ndrop cadence (s)", fontsize=9, color=INK)
    ax.set_xlabel("capture, in recording order (10-17; local time at session start)",
                  fontsize=9, color=INK)
    fig.suptitle("CH5 on 10-17, three witnesses per capture: healthy -> intermittent for one "
                 "hour -> healthy for the last 80 captures", fontsize=11, color=INK, y=0.995)
    fig.tight_layout(rect=(0, 0.04, 1, 0.985))
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=7.8, frameon=False)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_design(d, trial, drops, rd, spread, meta, path, span=0.34):
    """One design: every stabilized drop of every article, the article means
    ± 1 SD, and a stats table (mean, SD, variance, n) under each article."""
    ids = [FIRST[d]] + COPIES[d]
    fig, (ax, tab) = plt.subplots(2, 1, figsize=(10.5, 8.4),
                                  gridspec_kw={"height_ratios": [3.2, 1.25]})
    style(ax)
    rng = np.random.default_rng(7)
    allv = [x["t180"] for i in ids for x in drops[i]]
    mid = 0.5 * (min(allv) + max(allv))
    lo, hi = mid - span / 2, mid + span / 2
    for j, i in enumerate(ids):
        pts = drops[i]
        xs = j - 0.08 + rng.uniform(-0.15, 0.15, len(pts))
        for xx, p in zip(xs, pts):
            knock = p["gauge"] >= GAUGE_SUSPECT
            mk = "D" if p["in_fault"] else "o"
            ax.scatter(xx, p["t180"], s=30 if mk == "o" else 26, marker=mk, zorder=3,
                       color="none" if knock else COLOR[d], edgecolors=COLOR[d], lw=1.1)
        a = rd[i]["all_valid"]
        ax.errorbar(j + 0.24, a["mean"], yerr=a["sd"] or 0, fmt="_", ms=16, mew=2.2, color=INK,
                    capsize=4, lw=1.4, zorder=4)
        c = rd[i]["clean"]
        if c is not None:
            ax.scatter(j + 0.36, c["mean"], marker="<", s=42, color=COLOR[d], edgecolors=INK,
                       lw=0.6, zorder=5)
    first = rd[FIRST[d]]["all_valid"]["mean"]
    ax.axhline(first, color=COLOR[d], lw=0.9, ls=":", zorder=1)
    cp = spread["all_valid"]["copies"]
    ax.axhline(cp["mean_of_means"], color=INK2, lw=0.9, ls="--", zorder=1)
    ax.set_xticks(range(len(ids)))
    ax.set_xticklabels([meta[i] for i in ids], fontsize=7.6)
    ax.set_xlim(-0.55, 3.55)
    ax.set_ylim(lo, hi)
    ax.set_ylabel("T180 = TOP/CH5 (CFC-180) per stabilized drop\n"
                  f"(same {span:.2f} y-span on all three designs)", fontsize=8.6, color=INK)
    cpp = spread["all_valid"]["copies_plus_first"]
    ax.set_title(f"{d} (t{trial}): transmissibility by article. Between the 3 copies' means: "
                 f"SD {cp['sd_between']:.4f}, var {cp['var_between']:.2e}; with the first "
                 f"article: SD {cpp['sd_between']:.4f}, var {cpp['var_between']:.2e}",
                 fontsize=9.2, color=INK, loc="left")
    handles = [
        Line2D([], [], ls="", marker="o", color=COLOR[d], ms=6, label="clean-seat drop (gauge < 1.145)"),
        Line2D([], [], ls="", marker="o", mfc="none", mec=COLOR[d], ms=6,
               label="knock drop (gauge >= 1.145)"),
        Line2D([], [], ls="", marker="D", mfc="none", mec=COLOR[d], ms=5.5,
               label="diamond: recorded in the CH5-fault hour"),
        Line2D([], [], ls="-", marker="_", color=INK, ms=12, mew=2,
               label="article mean ± 1 SD, all valid drops"),
        Line2D([], [], ls="", marker="<", color=COLOR[d], mec=INK, ms=6,
               label="article mean, clean drops only"),
        Line2D([], [], ls=":", color=COLOR[d], lw=1.0, label=f"first article mean {first:.4f}"),
        Line2D([], [], ls="--", color=INK2, lw=1.0,
               label=f"mean of the 3 copies {cp['mean_of_means']:.4f}"),
    ]
    ax.legend(handles=handles, fontsize=7.2, frameon=False, loc="upper center", ncol=4,
              bbox_to_anchor=(0.5, 1.0))

    tab.set_xlim(-0.55, 3.55)
    tab.set_ylim(0, 1)
    tab.axis("off")
    rows = ["all valid drops", "  mean", "  SD", "  variance", "  n", "clean drops only",
            "  mean ± SD", "  variance", "  n"]
    for k, r in enumerate(rows):
        tab.text(-0.55, 0.95 - k * 0.112, r, fontsize=7.6, va="top", ha="left",
                 color=INK if not r.startswith("  ") else INK2,
                 fontweight="bold" if not r.startswith("  ") else "normal")
    for j, i in enumerate(ids):
        a, c = rd[i]["all_valid"], rd[i]["clean"]
        vals = ["", f"{a['mean']:.4f}", "-" if a["sd"] is None else f"{a['sd']:.4f}",
                "-" if a["var"] is None else f"{a['var']:.2e}", f"{a['n']}", ""]
        if c is None:
            vals += ["none", "", "0"]
        else:
            vals += [f"{c['mean']:.4f}" + ("" if c["sd"] is None else f" ± {c['sd']:.4f}"),
                     "-" if c["var"] is None else f"{c['var']:.2e}", f"{c['n']}"]
        for k, v in enumerate(vals):
            tab.text(j + 0.18, 0.95 - k * 0.112, v, fontsize=7.6, va="top", ha="center", color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_plates(rd, path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    for ax, (title, plate, ids, pla) in zip(axes, (
            ("Round-4 plate (corny1-9; print log 09-11; white PLA struts)", R4_PLATE,
             list(R4_PLATE), "white"),
            ("Replicate plate 1 (1sne##; print log 10-17; black PLA struts)", P1_PLATE,
             list(P1_PLATE), "black"))):
        ax.add_patch(plt.Rectangle((0, 0), *BED, fill=False, ec="#c3c2b7", lw=1.0))
        ax.add_patch(plt.Rectangle((WIPE_TOWER[0] - 5, WIPE_TOWER[1] - 30), 10, 60,
                                   fc="#e1e0d9", ec="#c3c2b7", lw=0.8))
        ax.text(WIPE_TOWER[0], WIPE_TOWER[1] - 38, "wipe\ntower", ha="center", va="top",
                fontsize=6.5, color=MUTED)
        for i in ids:
            trial, x, y, pos = plate[i]
            d = {37: "corny7", 39: "corny8", 38: "corny2"}.get(trial)
            if d is None:
                ax.scatter(x, y, s=500, color="#f0efec", ec="#c3c2b7", lw=0.8, zorder=2)
                ax.text(x, y, f"{i}\nt{trial}", ha="center", va="center", fontsize=6.5,
                        color=MUTED, zorder=3)
                continue
            ax.scatter(x, y, s=1500, color=COLOR[d], alpha=0.22, ec=COLOR[d], lw=1.4, zorder=2)
            a, c = rd[i]["all_valid"], rd[i]["clean"]
            lab = (f"{i}\nfirst article\nT180 {a['mean']:.3f}" if i == d else
                   f"{i}\n{d}\nT180 {a['mean']:.3f}" +
                   (f"\nclean {c['mean']:.3f}" if c is not None else "\nclean: none"))
            ax.text(x, y, lab, ha="center", va="center", fontsize=7, color=INK, zorder=3)
        if plate is P1_PLATE:   # where the first articles sat on the round-4 plate
            for d in DESIGNS:
                _, x, y, _ = R4_PLATE[d]
                ax.scatter(x, y, s=2600, facecolor="none", ec=COLOR[d], lw=1.1, ls=(0, (3, 2)),
                           zorder=1)
                ax.text(x, y + 30, f"{d}'s spot\non round 4", ha="center", va="bottom",
                        fontsize=6.3, color=INK2)
        ax.set_xlim(-8, BED[0] + 8)
        ax.set_ylim(-8, BED[1] + 8)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9, color=INK, loc="left")
        ax.text(BED[0] / 2, BED[1] + 3, "BACK", ha="center", va="bottom", fontsize=7, color=INK2)
        ax.text(BED[0] / 2, -3, "FRONT (door)", ha="center", va="top", fontsize=7, color=INK2)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
    fig.suptitle("Build-plate placement (x, y from the PR #102 plate files) with each article's "
                 "T180: all valid drops / clean drops", fontsize=10.5, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fetch_photos(dest: Path) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    got = {}
    for k, url in PHOTO_URLS.items():
        p = dest / f"{k}.jpg"
        if not p.exists():
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                p.write_bytes(r.read())
        got[k] = p
    return got


def fig_photos(photos: dict, rd, labels, path):
    from PIL import Image, ImageOps
    rows = [("corny2", BLOCK_DESIGNS[0]), ("corny7", BLOCK_DESIGNS[1]), ("corny8", BLOCK_DESIGNS[2])]
    fig, axes = plt.subplots(3, 4, figsize=(13, 16.2))
    for r, (d, _) in enumerate(rows):
        for c, i in enumerate([FIRST[d]] + COPIES[d]):
            ax = axes[r, c]
            im = ImageOps.exif_transpose(Image.open(photos[i]))
            im.thumbnail((900, 1200))
            ax.imshow(np.asarray(im))
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color(COLOR[d])
                sp.set_linewidth(2.0)
            ax.set_title(labels[i], fontsize=8.2, color=INK, loc="left")
    fig.suptitle("Print-log photos (issue #98): first articles (left, round-4 plate) vs "
                 "plate-1 copies. Struts: white PLA on the first articles, black on every copy.",
                 fontsize=10.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(path, dpi=110, pil_kwargs={"quality": 82})
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True, help="root with one folder per 1sne session")
    ap.add_argument("--photos", type=Path, default=None, help="cache dir for the #98 photos")
    ap.add_argument("--r4-3mf", type=Path, default=None)
    ap.add_argument("--p1-3mf", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=FIG)
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    cen = json.loads((OUT / "figures" / "capture_census.json").read_text())
    cen.sort(key=lambda r: r["local_time"])
    bad = [r["local_time"] for r in cen if r["class"] == "mistimed"]
    window = (min(bad), max(bad))
    rawm = raw_metrics(args.raw, args.procs)
    tim = timing(cen)

    # -- CH5 timeline: phases, recoveries, per-phase CH5 health -----------
    imp = [r["class"] != "mistimed" for r in cen]
    phase = ["before" if r["local_time"] < window[0] else
             "fault hour" if r["local_time"] <= window[1] else "after" for r in cen]
    seq = "".join("v" if ok else "x" for ok, ph in zip(imp, phase) if ph == "fault hour")
    runs_bad = [len(m) for m in re.findall(r"x+", seq)]
    runs_ok = [len(m) for m in re.findall(r"v+", seq)]
    per_phase = {}
    for ph in ("before", "fault hour", "after"):
        rr = [r for r, p in zip(cen, phase) if p == ph]
        good = [r for r in rr if r["class"] != "mistimed"]
        dev = [abs(100 * (r["in_raw_g"] / abs(r["tp4_ch5_g"]) - 1)) for r in good]
        st = [rawm[(r["session"], r["signal"])]["ch5_step_g"] for r in good]
        stb = [rawm[(r["session"], r["signal"])]["ch5_step_g"] for r in rr if r["class"] == "mistimed"]
        dvi = [r["tp4_ch5_dv_in_s"] for r in good]
        per_phase[ph] = {
            "first": rr[0]["local_time"], "last": rr[-1]["local_time"],
            "captures": len(rr), "with_impact": len(good), "no_impact": len(rr) - len(good),
            "ch5_vs_tp4_peak_dev_pct": {"median": float(np.median(dev)), "max": float(np.max(dev))},
            "ch5_step_g_impact_captures": {"median": float(np.median(st)), "max": float(np.max(st))},
            "ch5_step_g_no_impact_captures": None if not stb else
            {"median": float(np.median(stb)), "max": float(np.max(stb))},
            # the TP4's own CH5 delta-v reads low on knock captures, where it
            # integrates only the knock's 0.2 ms spike; the pipeline's full-pulse
            # delta-v is the physical one
            "tp4_ch5_dv_in_s_impact_captures": {"min": float(min(dvi)), "max": float(max(dvi))},
            "pipeline_in_dv_ms_impact_captures": {"min": float(min(r["in_dv_ms"] for r in good)),
                                                  "max": float(max(r["in_dv_ms"] for r in good))},
            "ch5_noise_floor_g_median": float(np.median([r["noise_floor_g"][3] for r in rr])),
        }
    suspect = [{"session": r["session"], "signal": r["signal"], "local_time": r["local_time"],
                "class": r["class"], "t180": r["t180"],
                "ch5_vs_tp4_peak_dev_pct": 100 * (r["in_raw_g"] / abs(r["tp4_ch5_g"]) - 1),
                **{k: rawm[(r["session"], r["signal"])][k] for k in ("ch5_step_g", "ch5_pre_g",
                                                                    "ch5_tail_g")}}
               for r, p in zip(cen, phase) if p == "fault hour" and r["class"] != "mistimed"]
    off = [{"session": s, "signal": e["signal"]} for s, v in tim["sessions"].items()
           for e in v["events"] if e["off_cadence"]]
    ch5 = {"fault_window": window, "phases": per_phase,
           "fault_hour_sequence": seq, "fault_hour_good_runs": runs_ok,
           "fault_hour_bad_runs": runs_bad,
           "recoveries_inside_window": len(runs_ok),
           "impact_captures_inside_window": suspect,
           "off_cadence_triggers": off, "timing": tim,
           "per_capture": [{**rawm[(r["session"], r["signal"])], "local_time": r["local_time"],
                            "class": r["class"], "phase": p,
                            "tp4_ch4_g": r["tp4_ch4_g"], "tp4_ch5_g": r["tp4_ch5_g"],
                            "tp4_ch5_ms": r["tp4_ch5_ms"], "tp4_ch5_dv_in_s": r["tp4_ch5_dv_in_s"]}
                           for r, p in zip(cen, phase)]}

    # -- article spread ------------------------------------------------------
    drops = article_drops(cen, window)
    rd = {i: readings(v) for i, v in drops.items()}

    def pooled(ids, key):
        sel = [x["t180"] for i in ids for x in drops[i]
               if key == "all_valid" or (x["gauge"] < GAUGE_SUSPECT and not x["in_fault"])]
        return stats(np.array(sel))
    spread = {d: {k: design_spread(rd, d, k, pooled) for k in ("all_valid", "clean")}
              for d in DESIGNS}
    p1 = json.loads((OUT / "params.json").read_text())
    p0 = json.loads((CORNY / "params.json").read_text())
    cm0 = json.loads((CORNY / "figures" / "campaign_metrics.json").read_text())
    meta, labels, articles = {}, {}, {}
    for d in DESIGNS:
        first_date = cm0["specimens"][d]["event_first"][5:10]
        r4 = R4_PLATE[d]
        meta[FIRST[d]] = (f"{d}\nfirst article\nwhite PLA · round-4 plate\n{r4[3]} · "
                          f"{p0[d]['mass_g']:.2f} g\ndropped {first_date}")
        labels[FIRST[d]] = (f"{d} (first article)\nwhite PLA · round-4 plate {r4[3]}\n"
                            f"{p0[d]['mass_g']:.2f} g · T180 {rd[d]['all_valid']['mean']:.3f}")
        articles[d] = {"article": d, "design": d, "version": "first article", "print": "round-4 plate",
                       "strut_pla": STRUT_PLA["corny"], "plate_pos": r4[3],
                       "plate_xy_mm": [r4[1], r4[2]], "mass_g": p0[d]["mass_g"],
                       "dropped": cm0["specimens"][d]["event_first"][:10], **rd[d]}
        for i in COPIES[d]:
            pp = P1_PLATE[i]
            c = rd[i]["clean"]
            meta[i] = (f"{i}\ncopy {i[-1]}\nblack PLA · plate 1\n{pp[3]} · {p1[i]['mass_g']:.2f} g\n"
                       "dropped 10-17")
            labels[i] = (f"{i} (plate-1 copy {i[-1]})\nblack PLA · plate 1 {pp[3]}\n"
                         f"{p1[i]['mass_g']:.2f} g · T180 {rd[i]['all_valid']['mean']:.3f}"
                         + (f" (clean {c['mean']:.3f})" if c else " (no clean drops)"))
            articles[i] = {"article": i, "design": d, "version": f"plate-1 copy {i[-1]}",
                           "print": "replicate plate 1", "strut_pla": STRUT_PLA["1sne"],
                           "plate_pos": pp[3], "plate_xy_mm": [pp[1], pp[2]],
                           "mass_g": p1[i]["mass_g"], "dropped": "2026-10-17", **rd[i]}
    # placement: distance of each copy from its first article's spot
    for d in DESIGNS:
        _, x0, y0, _ = R4_PLATE[d]
        for i in COPIES[d]:
            articles[i]["dist_from_first_article_spot_mm"] = float(np.hypot(P1_PLATE[i][1] - x0,
                                                                            P1_PLATE[i][2] - y0))

    settings = None
    if args.r4_3mf and args.p1_3mf:
        settings = compare_3mf(args.r4_3mf, args.p1_3mf)

    # -- figures -----------------------------------------------------------
    fig_strip(cen, tim, window, args.out / "17_ch5_drop_strip.png")
    fig_timeline(cen, rawm, tim, window, args.out / "18_ch5_fault_evidence.png")
    for k, d in enumerate(BLOCK_DESIGNS):
        fig_design(d, p0[d]["spec"][1:], drops, rd, spread[d], meta,
                   args.out / f"{19 + k}_{d}_t180_by_article.png")
    fig_plates(rd, args.out / "22_plate_placement.png")
    if args.photos is not None:
        fig_photos(fetch_photos(args.photos), rd, labels, args.out / "23_print_photos.jpg")

    out = {"note": "T180 = TOP/CH5 (CFC-180) over the stabilized drops of the standing "
                   "pipeline; 'clean' = seat gauge T1000/T180 < 1.145 and recorded outside "
                   "the CH5-fault hour. SD and variance use ddof = 1.",
           "ch5_fault": ch5, "articles": articles, "design_spread": spread,
           "strut_pla_by_batch": BATCH_PLA, "slicer_settings_round4_vs_plate1": settings,
           "plates": {"round4": R4_PLATE, "plate1": P1_PLATE, "wipe_tower_xy_mm": WIPE_TOWER}}
    (args.out / "ch5_replicates.json").write_text(json.dumps(out, indent=1, default=str))

    # -- console summary -----------------------------------------------------
    print("fault window", window)
    for ph, v in per_phase.items():
        print(f"  {ph:10s} {v['first'][11:]}-{v['last'][11:]}  captures {v['captures']:3d}  "
              f"impact {v['with_impact']:3d}  none {v['no_impact']:3d}  "
              f"CH5 vs TP4 median {v['ch5_vs_tp4_peak_dev_pct']['median']:.2f} % "
              f"max {v['ch5_vs_tp4_peak_dev_pct']['max']:.2f} %  "
              f"step (impact) max {v['ch5_step_g_impact_captures']['max']:.1f} G")
    print("  fault-hour sequence", seq, "good runs", runs_ok, "bad runs", runs_bad)
    print("  off-cadence triggers", off)
    for k, f in tim["fits"].items():
        print(f"  timing {k}: delta {f['delta_s']:+.2f} ± {f['delta_se_s']:.2f} s  "
              f"(P {f['period_s']:.3f} s, {f['n_impact']} anchors, {f['n_no_impact']} no-impact)")
    print(f"  pooled delta {tim['pooled']['delta_s']:+.2f} ± {tim['pooled']['se_s']:.2f} s")
    def f(v, spec):
        return "-" if v is None else format(v, spec)
    for d in DESIGNS:
        for i in [FIRST[d]] + COPIES[d]:
            a, c = rd[i]["all_valid"], rd[i]["clean"]
            print(f"{d} {i:7s} all n {a['n']:2d} mean {a['mean']:.4f} sd {f(a['sd'], '.5f')} "
                  f"var {f(a['var'], '.2e')} | clean " + ("none" if c is None else
                  f"n {c['n']:2d} mean {c['mean']:.4f} sd {f(c['sd'], '.5f')} var {f(c['var'], '.2e')}"))
        for k in ("all_valid", "clean"):
            s = spread[d][k]
            cp, cf = s["copies"], s["copies_plus_first"]
            print(f"   {k}: between copies sd {f(cp and cp['sd_between'], '.5f')} "
                  f"(within pooled {f(cp and cp['within_pooled_sd'], '.5f')}); with first "
                  f"{f(cf and cf['sd_between'], '.5f')}; copies vs first "
                  f"{f(s.get('copies_vs_first_pct'), '+.2f')} %")
    if settings:
        print("3mf:", settings["n_keys"], "keys,", settings["n_keys_differing"], "differ; infill same:",
              settings["per_part_infill_same_as_round4"])
    print(f"figures + json -> {args.out}")


if __name__ == "__main__":
    main()
