#!/usr/bin/env python3
"""Why the replicate copies weigh more than their first articles: print
files vs print batch, and the white -> black strut PLA switch
(PR #86, @me-madsen, 10-19).

The 27 plate-1/2/3 copies of corny2, corny7 and corny8 weigh 0.47-0.87 g
more than their first articles (+2.4 to +4.3 %).  The first articles have
white PLA struts and the copies black.  This script answers three things:

1. **Do the print models differ?**  ``--compare A.3mf B.3mf`` compares two
   Bambu Studio projects part by part: SHA-256 of each mesh's vertex and
   triangle arrays, its signed volume, the component and build transforms
   (any scale or rotation), every per-part and per-object setting, and
   every ``project_settings.config`` key.  Writes ``print_model_check.json``.
2. **Is each article told to extrude the same material?**
   ``--gcode KEY=PROJECT.3mf,PLATE.gcode`` (repeatable) reads a headless
   Bambu Studio slice and sums the filament deposited per object and per
   tool (E moves with XY motion, flow ratio included), with brim and
   support kept apart because they are removed before weighing.  Writes
   ``commanded_volumes.json``.  KEY is one of ``round1`` (the lab's
   as-printed r2d2 project), ``round3``, ``round4`` or ``plate1``.
3. **Where did the grams come from?**  The default mode fits, for every
   print batch with at least two designs,

       mass_with_label = rho_PLA * V_PLA + rho_TPU * V_TPU

   where V is the commanded volume of each material.  rho is then "grams on
   the scale per commanded cm^3": 1.24 (PLA) or 1.21 (TPU) for a perfect
   extrusion at the data-sheet density and nominal 1.75 mm filament.  It
   also regresses the round-3 paired mass steps (same nine designs printed
   white, white, then black) on each design's PLA/TPU split, so a step
   carried by the PLA shows up as a slope against the PLA share.

The masses are the issue #98 print-log values (``print_masses.csv``; the
print keys record them with the label on).  A label of fixed mass adds the
same amount to every article, and because every design here commands about
the same total volume (16.9-17.8 cm^3), it moves rho_PLA and rho_TPU up
together by about L / 17.5 g per cm^3.  It cannot create a PLA-only step.

Outputs (``data/drop-tests/1sne-checkin/figures/print-mass/``):
``28_print_mass_by_material.png`` and ``print_mass_colour.json``.

Usage:
    python scripts/analysis/drop_test_print_mass_colour_analysis.py
    python scripts/analysis/drop_test_print_mass_colour_analysis.py \\
        --compare round4.3mf plate1.3mf --compare round3.3mf dran3.3mf
    python scripts/analysis/drop_test_print_mass_colour_analysis.py \\
        --gcode round4=round4.3mf,out_r4/plate_1.gcode ...

The 3mf projects are on the PR #102 branch (``claude/issue-98-20260821-0103``):
round 4 at 9fba359 (``bo/slices/t3-prism-bo-round4.H2D-MM-PLAstruts-TPUcables.3mf``),
plate 1 (``bo/replicate-study/t3-prism-replicate-sne-plate1.H2D-MM-PLAstruts-TPUcables.3mf``),
round 3 and dran3 (``bo/slices/t3-prism-bo-round3...3mf``,
``bo/replicate-study/t3-prism-dran3...3mf``) and the lab's as-printed
round-1 project (``bo/slices/t3-prism-bo-round1.H2D-MM-PLAstruts-TPUcables_manual-supports.3mf``).
Slice with Bambu Studio v02.07.01.62 (``AppRun --slice 0 --debug 1
--outputdir OUT FILE.3mf``).  The round-3 project only slices headless
after copying the eight H2D machine-state keys in ``ROUND3_PATCH_KEYS``
from the round-4 project; none of them changes what an article is told to
extrude.  Round 1 and the patched round 3 end with a nozzle-reach warning
(their layouts predate the reach check) but write complete G-code.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402
from drop_test_1sne_checkin_analysis import INK, INK2, MUTED, style  # noqa: E402

OUT = DATA / "1sne-checkin" / "print-mass"
FIG = DATA / "1sne-checkin" / "figures" / "print-mass"
MASSES = OUT / "print_masses.csv"
COMMANDED = OUT / "commanded_volumes.json"
MODEL_CHECK = OUT / "print_model_check.json"

NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
FIL_AREA_MM2 = math.pi * (1.75 / 2) ** 2
RHO_TDS = {"pla": 1.24, "tpu": 1.21}     # Bambu PLA Basic TDS (ISO 1183); TPU as in bo/t3_prism_mass_model.py
ROUND3_PATCH_KEYS = ("extruder_ams_count", "extruder_nozzle_stats", "filament_map", "filament_map_mode",
                     "flush_multiplier", "flush_volumes_matrix", "flush_volumes_vector", "nozzle_volume_type")
# print order; recipe = what the project file sets for the struts / cables
BATCHES = {
    "r2d2": dict(label="r2d2\n08-24", recipe="round 1: PLA 220 C 30 mm3/s, TPU flow ratio 1.1, lab's support-painted file"),
    "drran": dict(label="drran\n09-02", recipe="round 3: PLA 217 C 20.5 mm3/s, TPU 244 C 3.6 mm3/s"),
    "2dran": dict(label="2dran\n09-05", recipe="round 3 (same file)"),
    "corny": dict(label="corny\n09-11", recipe="round 4: PLA 226 C 29.5 mm3/s, TPU 236 C 2.6 mm3/s"),
    "dran3": dict(label="dran3\n09-29", recipe="round 3 (same file)"),
    "1sne": dict(label="1sne\n10-17", recipe="round 4 (same file)"),
    "2sne": dict(label="2sne\n10-17", recipe="round 4 (same file, same gcode as 1sne)"),
    "3sne": dict(label="3sne\n10-17", recipe="round 4 (same file, same gcode as 1sne)"),
}
FIRST = {38: "corny2", 37: "corny7", 39: "corny8"}
PLACEMENT = {"name", "matrix", "source_file", "source_object_id", "source_volume_id",
             "source_offset_x", "source_offset_y", "source_offset_z"}
IDENTITY = "1 0 0 0 1 0 0 0 1 | 1 0 0 0 1 0 0 0 1"   # component | build-item rotation-scale blocks
SERIES = {"drran->2dran": "#2a78d6", "2dran->dran3": "#eb6834"}   # categorical slots 1-2


# --------------------------------------------------------------------------
# 1. project comparison
# --------------------------------------------------------------------------
def _project(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        sub = ET.fromstring(z.read("3D/Objects/object_1.model"))
        top = ET.fromstring(z.read("3D/3dmodel.model"))
        ms = ET.fromstring(z.read("Metadata/model_settings.config"))
        proj = json.loads(z.read("Metadata/project_settings.config"))
    meshes = {}
    for obj in sub.iter(NS + "object"):
        mesh = obj.find(NS + "mesh")
        if mesh is None:
            continue
        v = np.array([[float(p.get(k)) for k in "xyz"] for p in mesh.find(NS + "vertices")])
        t = np.array([[int(p.get(k)) for k in ("v1", "v2", "v3")] for p in mesh.find(NS + "triangles")])
        a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
        meshes[obj.get("id")] = dict(
            sha256=hashlib.sha256(v.tobytes() + t.tobytes()).hexdigest()[:16],
            volume_mm3=float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0),
            n_tri=len(t), extent_mm=(v.max(0) - v.min(0)).round(3).tolist())
    comps = {o.get("id"): [(c.get("objectid"), c.get("transform")) for c in o.find(NS + "components")]
             for o in top.iter(NS + "object") if o.find(NS + "components") is not None}
    builds = {i.get("objectid"): i.get("transform") for i in top.iter(NS + "item")}
    parts = {}
    malformed = 0
    for o in ms.findall("object"):
        oname = next(m.get("value") for m in o.findall("metadata") if m.get("key") == "name")
        ometa = {m.get("key"): m.get("value") for m in o.findall("metadata") if m.get("key") != "name"}
        for k, p in enumerate(o.findall("part")):
            pm = {m.get("key"): m.get("value") for m in p.findall("metadata")}
            malformed += "np.float64" in pm.get("matrix", "")
            sub_id, ctf = comps[o.get("id")][k]
            key = re.search(r"(t\d\d-(?:struts|cables))", pm["name"]).group(1)
            parts.setdefault(key, []).append(dict(
                object=oname, mesh=meshes[sub_id],
                settings={kk: vv for kk, vv in pm.items() if kk not in PLACEMENT},
                object_settings=ometa,
                rot_scale=" ".join(ctf.split()[:9]) + " | " + " ".join(builds[o.get("id")].split()[:9])))
    return dict(parts=parts, project=proj, malformed_matrix_strings=malformed)


def compare_projects(a: Path, b: Path) -> dict:
    pa, pb = _project(a), _project(b)
    rows, ok = [], True
    for key in sorted(set(pa["parts"]) & set(pb["parts"])):
        ref = pa["parts"][key][0]
        for p in pa["parts"][key][1:] + pb["parts"][key]:
            same = dict(mesh=p["mesh"]["sha256"] == ref["mesh"]["sha256"],
                        part_settings=p["settings"] == ref["settings"],
                        object_settings=p["object_settings"] == ref["object_settings"],
                        no_scale_or_rotation=p["rot_scale"] == IDENTITY and ref["rot_scale"] == IDENTITY)
            ok &= all(same.values())
            rows.append(dict(part=key, object_a=ref["object"], object_b=p["object"], **same,
                             volume_mm3=round(p["mesh"]["volume_mm3"], 3), sha256=p["mesh"]["sha256"],
                             settings=p["settings"]))
    keys = set(pa["project"]) | set(pb["project"])
    diff = sorted(k for k in keys if pa["project"].get(k) != pb["project"].get(k))
    return dict(a=a.name, b=b.name, parts_compared=len(rows), all_parts_identical=ok,
                project_keys=len(keys), project_keys_differing=diff,
                filament_density=pa["project"].get("filament_density"),
                filament_flow_ratio=pa["project"].get("filament_flow_ratio"),
                filament_colour_in_file=pa["project"].get("filament_colour"),
                malformed_matrix_strings=dict(a=pa["malformed_matrix_strings"], b=pb["malformed_matrix_strings"]),
                parts=rows)


# --------------------------------------------------------------------------
# 2. commanded volumes from a headless slice
# --------------------------------------------------------------------------
def _trial_of(key: str, name: str) -> int:
    if key == "round1":                          # "Specimen 0X" -> source trial 10 + X
        return 10 + int(re.search(r"(\d+)$", name).group(1))
    if key == "plate1":                          # 1sne<design digit><copy>
        return {"7": 37, "8": 39, "2": 38}[name[4]]
    return int(re.search(r"(\d+)$", name).group(1))   # "Trial NN"


def commanded_from_gcode(key: str, project: Path, gcode: Path) -> dict:
    with zipfile.ZipFile(project) as z:
        ms = ET.fromstring(z.read("Metadata/model_settings.config"))
        sha = hashlib.sha256(project.read_bytes()).hexdigest()[:12]
    names = {o.get("id"): next(m.get("value") for m in o.findall("metadata") if m.get("key") == "name")
             for o in ms.findall("object")}
    label = {}
    for mi in ms.find("plate").findall("model_instance"):
        d = {m.get("key"): m.get("value") for m in mi.findall("metadata")}
        label[int(d["identify_id"])] = names[d["object_id"]]
    num = re.compile(r"([XYE])(-?\d*\.?\d+)")
    acc = defaultdict(float)
    tool, feature, obj = 0, None, None
    with open(gcode) as fh:
        for line in fh:
            if line.startswith("; start printing object, unique label id:"):
                obj = int(line.rsplit(":", 1)[1])
            elif line.startswith("; stop printing object, unique label id:"):
                obj = None
            elif line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
            elif line.rstrip() in ("T0", "T1"):        # T255 / T65535 only appear in the end gcode
                tool = int(line[1])
            elif obj is not None and line.startswith(("G1 ", "G2 ", "G3 ")):
                d = dict(num.findall(line.split(";", 1)[0]))
                if "E" in d and float(d["E"]) > 0 and ("X" in d or "Y" in d or line[1] != "1"):
                    part = "brim" if feature == "Brim" else "support" if (feature or "").startswith("Support") else "article"
                    acc[(obj, "pla" if tool == 0 else "tpu", part)] += float(d["E"])
    objs = {}
    for (o, mat, part), e in acc.items():
        r = objs.setdefault(label[o], {"trial": _trial_of(key, label[o])})
        r[f"{mat}_{part}_cm3"] = round(r.get(f"{mat}_{part}_cm3", 0.0) + e * FIL_AREA_MM2 / 1000, 5)
    return dict(project=project.name, sha256_12=sha, gcode=gcode.name, objects=objs)


# --------------------------------------------------------------------------
# 3. the fits
# --------------------------------------------------------------------------
def _lsq(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    s2 = float(r @ r) / (len(y) - X.shape[1])
    return beta, np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X))), math.sqrt(s2), r


def load_inputs() -> tuple[list[dict], dict]:
    with open(MASSES) as fh:
        masses = [dict(r, trial=int(r["trial"]), mass=float(r["mass_g_with_label"])) for r in csv.DictReader(fh)]
    cv = json.loads(COMMANDED.read_text())
    cmd = {}
    for key in ("round1", "round3", "round4"):
        for o in cv["projects"][key]["objects"].values():
            cmd[o["trial"]] = (o["pla_article_cm3"], o["tpu_article_cm3"])
    return masses, cmd


def analyse(masses: list[dict], cmd: dict) -> dict:
    res = dict(batches={}, steps={}, label_sensitivity={}, first_vs_copies={})
    for b in BATCHES:
        rows = [r for r in masses if r["batch"] == b]
        X = np.array([cmd[r["trial"]] for r in rows]); y = np.array([r["mass"] for r in rows])
        beta, se, sd, resid = _lsq(X, y)
        ideal = X @ np.array([RHO_TDS["pla"], RHO_TDS["tpu"]])
        res["batches"][b] = dict(
            strut_pla=rows[0]["strut_pla"], print_log_date=rows[0]["print_log_date"], n=len(rows),
            designs=sorted({r["trial"] for r in rows}), recipe=BATCHES[b]["recipe"],
            rho_pla=beta[0], rho_pla_se=se[0], rho_tpu=beta[1], rho_tpu_se=se[1], resid_sd_g=sd,
            mass_over_ideal=float(y.sum() / ideal.sum()),
            residuals_g={r["article"]: round(float(e), 3) for r, e in zip(rows, resid)})
    for colour in ("white", "black"):
        v = [x["rho_pla"] for x in res["batches"].values() if x["strut_pla"] == colour]
        w = [x["rho_tpu"] for x in res["batches"].values() if x["strut_pla"] == colour]
        res[f"{colour}_batches"] = dict(n=len(v), rho_pla_mean=float(np.mean(v)), rho_pla_sd=float(np.std(v, ddof=1)),
                                        rho_tpu_mean=float(np.mean(w)), rho_tpu_sd=float(np.std(w, ddof=1)))
    wb, bb = res["white_batches"], res["black_batches"]
    gap = bb["rho_pla_mean"] - wb["rho_pla_mean"]
    se_gap = math.sqrt(wb["rho_pla_sd"] ** 2 / wb["n"] + bb["rho_pla_sd"] ** 2 / bb["n"])
    res["pla_step_white_to_black"] = dict(delta=gap, pct=100 * gap / wb["rho_pla_mean"], welch_t=gap / se_gap)
    # round-3 paired steps (the same nine designs, three prints)
    by = {b: {r["trial"]: r["mass"] for r in masses if r["batch"] == b} for b in ("drran", "2dran", "dran3")}
    for a, b in (("drran", "2dran"), ("2dran", "dran3"), ("drran", "dran3")):
        ts = sorted(by[a])
        X = np.array([cmd[t] for t in ts]); y = np.array([by[b][t] - by[a][t] for t in ts])
        beta, se, sd, _ = _lsq(X, y)
        share = X[:, 0] / X.sum(1)
        res["steps"][f"{a}->{b}"] = dict(
            mean_g=float(y.mean()), d_rho_pla=beta[0], d_rho_pla_se=se[0], d_rho_tpu=beta[1], d_rho_tpu_se=se[1],
            contrast_pla_minus_tpu=beta[0] - beta[1], resid_sd_g=sd, corr_pla_share=float(np.corrcoef(share, y)[0, 1]),
            per_design={f"t{t}": dict(pla_share=round(float(s), 4), delta_g=round(float(d), 3))
                        for t, s, d in zip(ts, share, y)})
    ts = sorted(by["2dran"]); X = np.array([cmd[t] for t in ts])
    for L in (0.0, 0.1, 0.2):
        y = np.array([by["dran3"][t] - by["2dran"][t] - L for t in ts])
        beta, *_ = _lsq(X, y)
        res["label_sensitivity"][f"label +{L:.1f} g"] = dict(
            d_rho_pla_pct=100 * beta[0] / res["batches"]["2dran"]["rho_pla"],
            d_rho_tpu_pct=100 * beta[1] / res["batches"]["2dran"]["rho_tpu"])
    # first articles vs the 27 copies, split with the batch rhos
    copies = [r for r in masses if r["batch"] in ("1sne", "2sne", "3sne")]
    Xc = np.array([cmd[r["trial"]] for r in copies]); yc = np.array([r["mass"] for r in copies])
    rc, rc_se, _, _ = _lsq(Xc, yc)
    cb = res["batches"]["corny"]
    for t, name in FIRST.items():
        first = next(r["mass"] for r in masses if r["article"] == name)
        cm = [r["mass"] for r in copies if r["trial"] == t]
        pla, tpu = cmd[t]
        res["first_vs_copies"][name] = dict(
            trial=t, first_g=first, copies_mean_g=float(np.mean(cm)), copies_sd_g=float(np.std(cm, ddof=1)),
            gain_g=float(np.mean(cm) - first), gain_pct=float(100 * (np.mean(cm) / first - 1)),
            commanded_pla_cm3=pla, commanded_tpu_cm3=tpu,
            explained_by_pla_g=pla * (rc[0] - cb["rho_pla"]), explained_by_tpu_g=tpu * (rc[1] - cb["rho_tpu"]),
            first_resid_vs_corny_fit_g=cb["residuals_g"][name])
    res["copies_pooled_fit"] = dict(rho_pla=rc[0], rho_pla_se=rc_se[0], rho_tpu=rc[1], rho_tpu_se=rc_se[1])
    return res


# --------------------------------------------------------------------------
# figure
# --------------------------------------------------------------------------
def figure(res: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 5.0), gridspec_kw={"width_ratios": [1.15, 1.15, 1.0]})
    names = list(BATCHES)
    x = np.arange(len(names))
    fill_handles = [Line2D([], [], ls="", marker="o", ms=8, mfc="white", mec=INK, mew=1.4, label="white strut PLA"),
                    Line2D([], [], ls="", marker="o", ms=8, mfc=INK, mec=INK, label="black strut PLA")]
    for ax, mat, ttl in ((axes[0], "pla", "PLA struts: steps up at the colour switch"),
                         (axes[1], "tpu", "TPU cables: moves job to job, no colour pattern")):
        style(ax)
        if mat == "pla":   # group means only where the claim is made
            for colour in ("white", "black"):
                idx = [i for i, b in enumerate(names) if res["batches"][b]["strut_pla"] == colour]
                m = res[f"{colour}_batches"]["rho_pla_mean"]
                ax.hlines(m, min(idx) - 0.3, max(idx) + 0.3, color=MUTED, lw=1.0, ls="--", zorder=1)
                if colour == "black":
                    ax.text(min(idx) - 0.3, m + 0.0035, f"black mean {m:.3f}", fontsize=7.2, color=INK2, va="bottom")
                else:
                    ax.text(max(idx) + 0.3, m - 0.0035, f"white mean {m:.3f}", fontsize=7.2, color=INK2,
                            va="top", ha="right")
        for i, b in enumerate(names):
            r = res["batches"][b]
            fc = "white" if r["strut_pla"] == "white" else INK
            ax.errorbar(i, r[f"rho_{mat}"], yerr=r[f"rho_{mat}_se"], fmt="o", ms=8, mfc=fc, mec=INK, mew=1.4,
                        ecolor=INK2, elinewidth=1.1, capsize=3, zorder=3)
            ax.annotate(f"{r[f'rho_{mat}']:.3f}", (i, r[f"rho_{mat}"]), xytext=(9, 4), textcoords="offset points",
                        fontsize=7.2, color=INK2)
        ax.axhline(RHO_TDS[mat], color=INK2, lw=0.9, ls=":", zorder=1)
        ax.text(len(names) - 0.2, RHO_TDS[mat] + 0.003, f"perfect extrusion at the data-sheet density "
                f"({RHO_TDS[mat]:.2f})", fontsize=7, color=INK2, va="bottom", ha="right")
        ax.set_xticks(x, [BATCHES[b]["label"] for b in names], fontsize=7.6)
        ax.set_xlim(-0.6, len(names) - 0.1)
        ax.set_ylabel(f"{mat.upper()} on the scale per commanded cm³ (g/cm³)", fontsize=8.6, color=INK)
        ax.set_title(ttl, fontsize=9.5, color=INK, loc="left")
        ax.legend(handles=fill_handles, loc="lower right", fontsize=7.6, frameon=False)
    axes[0].set_ylim(1.12, 1.255)
    axes[1].set_ylim(0.98, 1.26)
    ax = axes[2]
    style(ax)
    for step, colour in SERIES.items():
        s = res["steps"][step]
        pts = sorted((v["pla_share"], v["delta_g"]) for v in s["per_design"].values())
        sx, sy = np.array(pts).T
        k, c0 = np.polyfit(sx, sy, 1)
        ax.plot(sx, sy, "o", ms=8, color=colour, mec="white", mew=1.5, zorder=3)
        ax.plot(sx[[0, -1]], c0 + k * sx[[0, -1]], color=colour, lw=2, zorder=2)
        txt = "white → white" if step == "drran->2dran" else "white → black"
        ax.annotate(f"{step}\n({txt})", (sx[-1], c0 + k * sx[-1]), xytext=(6, 0), textcoords="offset points",
                    fontsize=7.4, color=INK, va="center")
    ax.legend(handles=[Line2D([], [], color=c, lw=2, marker="o", ms=7, mec="white",
                              label=f"{s} ({'white → white' if s == 'drran->2dran' else 'white → black'})")
                       for s, c in SERIES.items()], loc="upper left", fontsize=7.4, frameon=False)
    ax.axhline(0, color="#c3c2b7", lw=0.9)
    ax.set_xlim(0.54, 0.86)
    ax.set_xlabel("PLA share of the commanded volume (round-3 design)", fontsize=8.6, color=INK)
    ax.set_ylabel("mass change, same design (g)", fontsize=8.6, color=INK)
    ax.set_title("Round 3: the same nine designs, printed three times", fontsize=9.5, color=INK, loc="left")
    fig.suptitle("Per commanded cm³, the black strut PLA put about 4 % more mass on the scale than the white "
                 "did; the TPU term moves between print jobs with no colour pattern", fontsize=10.5, color=INK, x=0.01,
                 ha="left", y=1.0)
    fig.text(0.01, -0.04, "Fit per batch: mass with label = ρ_PLA·V_PLA + ρ_TPU·V_TPU, V = slicer-commanded "
             "volume per article (Bambu Studio v02.07.01.62, brim and support excluded). Error bars ±1 SE. "
             "r2d2 is round 1 (other designs, other recipe); drran/2dran/dran3 share one file, corny/1sne/2sne/3sne another.",
             fontsize=7.2, color=INK2, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--compare", nargs=2, action="append", type=Path, metavar=("A.3mf", "B.3mf"))
    ap.add_argument("--gcode", action="append", metavar="KEY=PROJECT.3mf,PLATE.gcode")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    if args.compare:
        out = [compare_projects(a, b) for a, b in args.compare]
        MODEL_CHECK.write_text(json.dumps(out, indent=1) + "\n")
        for c in out:
            print(f"{c['a']} vs {c['b']}: {c['parts_compared']} parts, identical={c['all_parts_identical']}, "
                  f"project keys {c['project_keys']} ({len(c['project_keys_differing'])} differ), "
                  f"malformed matrix strings {c['malformed_matrix_strings']}")
        return
    if args.gcode:
        cv = dict(slicer="Bambu Studio v02.07.01.62 AppImage CLI (--slice 0 --debug 1)",
                  units="cm3 of 1.75 mm filament fed (E x filament area); the flow ratio is already in E",
                  round3_patched_keys=list(ROUND3_PATCH_KEYS), projects={})
        for spec in args.gcode:
            key, paths = spec.split("=", 1)
            proj, gcode = (Path(p) for p in paths.split(","))
            cv["projects"][key] = commanded_from_gcode(key, proj, gcode)
        COMMANDED.write_text(json.dumps(cv, indent=1) + "\n")
        print(f"wrote {COMMANDED}")
        return
    masses, cmd = load_inputs()
    res = analyse(masses, cmd)
    if MODEL_CHECK.exists():
        res["print_model_check"] = [{k: v for k, v in c.items() if k != "parts"} for c in json.loads(MODEL_CHECK.read_text())]
    cv = json.loads(COMMANDED.read_text())
    if "plate1" in cv["projects"]:
        dev = []
        for o in cv["projects"]["plate1"]["objects"].values():
            ref = cmd[o["trial"]]
            dev += [100 * (o["pla_article_cm3"] / ref[0] - 1), 100 * (o["tpu_article_cm3"] / ref[1] - 1)]
        res["plate1_vs_round4_commanded_max_abs_pct"] = float(np.max(np.abs(dev)))
    figure(res, FIG / "28_print_mass_by_material.png")
    (FIG / "print_mass_colour.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    for b, r in res["batches"].items():
        print(f"{b:6s} {r['strut_pla']:5s} rho_PLA {r['rho_pla']:.3f}+-{r['rho_pla_se']:.3f}  "
              f"rho_TPU {r['rho_tpu']:.3f}+-{r['rho_tpu_se']:.3f}  resid {r['resid_sd_g']:.3f} g  "
              f"mass/ideal {r['mass_over_ideal']:.3f}")
    print("PLA step white->black:", {k: round(v, 4) for k, v in res["pla_step_white_to_black"].items()})
    for k, s in res["steps"].items():
        print(f"{k}: mean {s['mean_g']:+.3f} g, dPLA {s['d_rho_pla']:+.4f}+-{s['d_rho_pla_se']:.4f}, "
              f"dTPU {s['d_rho_tpu']:+.4f}+-{s['d_rho_tpu_se']:.4f}, corr(share) {s['corr_pla_share']:+.2f}")
    for k, v in res["first_vs_copies"].items():
        print(k, {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()})
    print("label sensitivity:", res["label_sensitivity"])


if __name__ == "__main__":
    main()
