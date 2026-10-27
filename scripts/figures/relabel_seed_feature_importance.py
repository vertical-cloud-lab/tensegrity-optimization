"""Re-render the seed-state feature-importance figure (SI fig:si-sensitivity)
with the second objective titled "E_reb, mass-weighted rebound (mJ per drop)".

Uses the campaign branch's own plotting function on its committed
importance table (no Ax, no refit), so only the panel title changes.
Provenance: run 2026-10-27 against claude/issue-98-20260821-0103 at 65ff978
(checked out as a worktree) with pandas + matplotlib only.

Usage:
    git worktree add /tmp/campaign 65ff978
    python3 scripts/figures/relabel_seed_feature_importance.py /tmp/campaign/bo
"""
import sys
from pathlib import Path

import pandas as pd

bo_dir = Path(sys.argv[1])
out = Path(__file__).resolve().parents[2] / "figures" / "bo" / "t3-prism-bo-round1-feature-importance.png"
sys.path.insert(0, str(bo_dir))

import t3_prism_bo_campaign as C  # noqa: E402
import t3_prism_bo_diagnostics as D  # noqa: E402

# keep the committed face (Open Sans) so only the title strip changes
rest = [f for f in C.FIG_RC["font.sans-serif"] if f != "Open Sans"]
C.FIG_RC["font.sans-serif"][:] = ["Open Sans"] + rest
D.METRIC_LABEL[C.obj1_name] = "t180\n(filtered peak-accel. ratio)"
D.METRIC_LABEL[C.obj2_name] = "$E_{\\mathrm{reb}}$, mass-weighted rebound\n(mJ per drop)"
D.render_feature_importance(
    pd.read_csv(bo_dir / "t3-prism-bo-round1-feature-importance.csv"), out, n_articles=7)
print(f"wrote {out}")
