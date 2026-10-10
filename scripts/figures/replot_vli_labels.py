"""Re-render the four campaign figures whose second-objective axis read
"Rebound energy", with the velocity-loss-index wording, using the campaign
branch's own plotting functions on the committed CSVs (no Ax, no refit).

Provenance: run 2026-10-10 against the campaign branch
claude/issue-98-20260821-0103 at e9f5e2d (checked out as a worktree), with
pandas + matplotlib only. The regenerated front-evolution table matched
manuscript/data/t3-prism-bo-front-evolution.csv exactly, and a pixel diff
against the previous PNGs is confined to the relabeled title strip.

Usage:
    git worktree add /tmp/campaign <campaign commit>
    python scripts/figures/replot_vli_labels.py /tmp/campaign/bo \
        manuscript/data/t3-prism-bo-round5-logocv.csv \
        manuscript/data/t3-prism-bo-round5-logocv-diagnostics.json /tmp/out
"""
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

bo_dir, logocv_csv, logocv_json, out_dir = (Path(a) for a in sys.argv[1:5])
out_dir.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(bo_dir))

import t3_prism_bo_campaign as C  # noqa: E402
import t3_prism_bo_diagnostics as D  # noqa: E402

MINUS, DOWN = "−", C.ARROW_DOWN
TWO_LINE = f"Mass-weighted 1 {MINUS} velocity loss index\n(mJ per drop, {DOWN} is better)"
ONE_LINE = f"Mass-weighted 1 {MINUS} VLI (mJ per drop)"
STACKED = f"Mass-weighted 1 {MINUS} VLI\n(mJ per drop)"


def use_font(face):
    # the committed PNGs were rendered in Lato (scatter/parity figures) and
    # Open Sans (importance bars); pin the same face so only the label changes
    rest = [f for f in C.FIG_RC["font.sans-serif"] if f != face]
    C.FIG_RC["font.sans-serif"][:] = [face] + rest


# 1. batch-4 predicted vs measured (campaign script, --measured-round4)
use_font("Lato")
C.Y_LABEL = TWO_LINE
C.main(["--measured-round4", "--no-animation"])
shutil.copy(bo_dir / "figures" / "t3-prism-bo-round4-predicted-vs-actual.png",
            out_dir / "t3-prism-bo-round4-predicted-vs-actual.png")

# 2. front evolution (standalone script; label is inline, so patch a copy)
src = (bo_dir / "t3_prism_front_evolution.py").read_text()
old = ('ax.set_ylabel("Rebound energy to payload /\\n(mJ per drop, "\n'
       '                      f"{ARROW_DOWN} is better)"')
assert src.count(old) == 1, "front-evolution label not found"
patched = bo_dir / "_front_evolution_vli.py"
patched.write_text(src.replace(old, f"ax.set_ylabel({TWO_LINE!r}"))
# in-process, so the pinned face (shared FIG_RC dict) applies; Open Sans
# has no U+2193 and renders tofu
import importlib  # noqa: E402
use_font("Lato")
importlib.import_module("_front_evolution_vli").main()
shutil.copy(bo_dir / "figures" / "t3-prism-bo-front-evolution.png",
            out_dir / "t3-prism-bo-front-evolution.png")
shutil.copy(bo_dir / "t3-prism-bo-front-evolution.csv",
            out_dir / "t3-prism-bo-front-evolution.csv")

# 3. round-5 leave-one-design-out CV
D.METRIC_TITLE[C.obj2_name] = ONE_LINE
D.render_loocv(pd.read_csv(logocv_csv), json.loads(logocv_json.read_text()),
               out_dir / "t3-prism-bo-round5-logocv.png", n_articles=44,
               note=D.LOGOCV_NOTE)

# 4. seed-state feature importance
use_font("Open Sans")
D.METRIC_LABEL[C.obj2_name] = STACKED
# keep the committed left-panel title (the campaign code has since renamed it)
D.METRIC_LABEL[C.obj1_name] = "t180\n(filtered peak-accel. ratio)"
D.render_feature_importance(
    pd.read_csv(bo_dir / "t3-prism-bo-round1-feature-importance.csv"),
    out_dir / "t3-prism-bo-round1-feature-importance.png", n_articles=7)
print("done")
