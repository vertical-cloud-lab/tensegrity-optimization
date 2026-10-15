"""
Submit an Edison ANALYSIS comparing:
  - Ye et al. (2023): rigid PLA core wrapped by TPU soft skin (TPU OUTSIDE)
  - Our approach (Design F): soft TPU core/knot captive inside rigid PLA shell (TPU INSIDE)
"""
import os, sys, time, json
from pathlib import Path

os.environ.setdefault(
    "EDISON_PLATFORM_API_KEY", os.environ.get("EDISON_API_KEY", "")
)

from edison_client import EdisonClient, JobNames

api_key = os.environ.get("EDISON_PLATFORM_API_KEY")
if not api_key:
    raise RuntimeError("No Edison API key found")

client = EdisonClient(api_key=api_key)

REPO = Path(__file__).resolve().parents[2]
CAD_DIR = REPO / "cad/joint-design"
RENDERS_DIR = CAD_DIR / "renders"
ED_DIR = REPO / "edison-trajectories/joint-design"

TERMINAL = {"success", "failed", "cancelled", "error", "crashed"}

def upload(path, label):
    p = Path(path)
    if not p.exists():
        print(f"  SKIP (not found): {p}")
        return None
    uri = client.upload_file(str(p))
    print(f"  [{label}] → {uri}")
    return uri

# ── Upload files ────────────────────────────────────────────────────────────
print("Uploading files...")
file_uris = []
for path, label in [
    ("/tmp/t3_prism_sobol_batch.py",       "bo-script"),
    ("/tmp/manuscript-body.tex",            "manuscript"),
    ("/tmp/pr38_conversation_context.md",   "pr38-context"),
    (str(CAD_DIR / "F_captive_core.scad"),  "F-scad"),
    (str(CAD_DIR / "F_captive_core.md"),    "F-rationale"),
    (str(RENDERS_DIR / "F_captive_core_iso.png"),         "F-iso"),
    (str(RENDERS_DIR / "F_captive_core_section_X_iso.png"), "F-sec-X"),
    (str(RENDERS_DIR / "F_captive_core_section_Y_iso.png"), "F-sec-Y"),
    (str(RENDERS_DIR / "F_captive_core_section_Z_iso.png"), "F-sec-Z"),
    (str(ED_DIR / "README.md"),             "joint-design-README"),
]:
    uri = upload(path, label)
    if uri:
        file_uris.append(uri)

print(f"Uploaded {len(file_uris)} files\n")

# ── Query ────────────────────────────────────────────────────────────────────
QUERY = """
## Background

This project uses multi-material FDM (Bambu H2D, PLA struts + TPU 85A tendons) to print 
tensegrity-inspired unit cells optimized via Bayesian optimization.  Two use cases:
  (a) Lander / egg-drop demo (#16): omnidirectional impact, Bruceton n≥20 reuse drops
  (b) Uni-axial crutch-tip print: primarily axial cable loading

The current manuscript draft (lines 378-382, "manuscript-body.tex") states:
  "Following Ye et al. (ye2023multimaterial), the design uses a core-wrapping strategy
   in which each PLA strut is encapsulated by continuous TPU skin..."

However, @sgbaird confirmed (PR #20 review comment) that this description is WRONG —
the project has actually been doing the OPPOSITE: wrapping a TPU inner core with rigid PLA.

@me-madsen described the actual implementation:
  "The cables going to one end of a strut all connect to each other inside of that strut,
   then extend out from the strut, the strut acting as a kind of cage to the multiple
   outlets of cables."

## The two competing topologies

**Strategy A — Ye et al. "core-wrapping" (TPU OUTSIDE, PLA INSIDE)**
- Rigid PLA strut core → continuous soft TPU skin wraps the OUTSIDE
- TPU skin mechanically interlocks with PLA and prevents delamination under cyclic loading
- Ref: ye2023multimaterial; also khatri2024energy for energy absorption data

**Strategy B — Our "captive-core" (TPU INSIDE, PLA OUTSIDE) — Design F in attached files**
- Soft TPU 85A "knot" (Ø7.0 mm) lives entirely INSIDE a rigid PLA outer shell (Ø12.0 mm)
- Cable exits shell through a single Ø2.8 mm bore; core cannot escape → pull-out ratio 2.5×
- No chemical PLA-TPU bond required
- Layer-interlock teeth: 2 staggered rings of radial teeth prevent axial sliding (per @achris0520)
- Print-in-place: 0.5 mm radial gap around TPU core during printing
- See attached F_captive_core.scad, F_captive_core.md, and cross-section PNGs

## Research questions — please answer with specific citations (DOI where possible)

1. **Which topology (A or B) is better for our project goals, and why?**
   Answer separately for:
   (i)  Lander / egg-drop (omnidirectional impact, Bruceton n≥20 reuse)
   (ii) Uni-axial crutch-tip print (axial cable loading)

2. **Mechanical performance — what does the literature say?**
   (a) Pull-out / peel strength for Ye et al. core-wrapping topology (PLA+TPU FDM)?
   (b) Published data on print-in-place TPU-in-PLA encapsulation pull-out resistance?
   (c) How do layer-interlock / mechanical-tooth features compare to chemical adhesion
       for PLA-TPU bonds under cyclic loading?
   (d) What is the expected failure mode for each topology under repeated drop impact?

3. **Printability on Bambu H2D (0.4 mm nozzle, 0.2 mm layer, TPU 85A)**
   (a) Strategy A requires TPU on the outside of PLA — does this require specific print
       sequencing? Any known issues with TPU bridging or sagging on outer layers?
   (b) Strategy B requires printing TPU-inside-PLA with 0.5 mm radial gap — is this gap
       sufficient for print-in-place resolution with TPU 85A? Minimum recommended gap?

4. **Is there a hybrid approach that captures benefits of both?**
   Could core-wrapping (Strategy A) be combined with captive-core geometry (Strategy B)?
   E.g., captive TPU knot inside PLA shell AND TPU skin on the exterior strut?

5. **Manuscript correction (lines 378-395 of manuscript-body.tex)**
   The current text incorrectly cites Ye et al. core-wrapping as our approach.
   Please provide corrected text for lines 378-395 that:
   (a) Accurately describes our actual captive-core approach
   (b) Positions it relative to Ye et al. and other relevant prior art
   (c) Explains why we chose TPU-inside rather than TPU-outside for this application

Please cite all quantitative claims against attached files or peer-reviewed DOIs.
"""

# ── Submit task ──────────────────────────────────────────────────────────────
print("Submitting Edison ANALYSIS task...")
task_id = client.create_task(
    {"name": JobNames.ANALYSIS, "query": QUERY},
    files=file_uris,
)
print(f"Task submitted: {task_id}\n")

# Save submission record
record = {
    "task_id": task_id,
    "job_name": JobNames.ANALYSIS,
    "query_summary": "TPU-inside vs TPU-outside topology comparison for PLA+TPU tensegrity joints",
    "file_uris": file_uris,
    "status": "submitted",
}
sub_path = ED_DIR / f"TPU-topology-comparison-SUBMITTED.json"
sub_path.write_text(json.dumps(record, indent=2) + "\n")
print(f"Submission record: {sub_path}\n")

# ── Poll until done ──────────────────────────────────────────────────────────
print("Polling for results (up to 20 min)...")
MAX_WAIT = 20 * 60
POLL_INTERVAL = 30
start = time.time()

while True:
    elapsed = time.time() - start
    if elapsed > MAX_WAIT:
        print(f"\nPolling timed out after {int(elapsed)}s.")
        sys.exit(1)
    try:
        task = client.get_task(task_id=task_id)
        status = task.status
        print(f"  [{int(elapsed):4d}s] status = {status}", flush=True)
        if status in TERMINAL:
            break
    except Exception as e:
        print(f"  [{int(elapsed):4d}s] poll error: {e}")
    time.sleep(POLL_INTERVAL)

print(f"\nFinal status: {status}")

# ── Extract and save result ──────────────────────────────────────────────────
answer = task.answer if hasattr(task, "answer") else None

# Build markdown output
md_lines = [
    f"# Edison ANALYSIS — TPU-inside vs TPU-outside topology comparison",
    f"",
    f"**Task ID**: `{task_id}`  ",
    f"**Status**: `{status}`  ",
    f"**Job**: `{JobNames.ANALYSIS}`",
    f"",
    f"## Answer",
    f"",
    answer or "(no answer extracted)",
]
md_text = "\n".join(md_lines)

md_path = ED_DIR / f"TPU-topology-comparison-{task_id[:8]}.md"
json_path = ED_DIR / f"TPU-topology-comparison-{task_id[:8]}.json"

md_path.write_text(md_text + "\n")

full_record = {**record, "status": status, "answer": answer}
json_path.write_text(json.dumps(full_record, indent=2) + "\n")

print(f"\nMarkdown: {md_path}")
print(f"JSON:     {json_path}")
print("\n=== ANSWER (first 3000 chars) ===")
print((answer or "(none)")[:3000])
if answer and len(answer) > 3000:
    print(f"\n... [{len(answer)} chars total — see {md_path} for full text]")
