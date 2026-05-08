## Edison Scientific Integration

Integration with [Edison Scientific](https://edisonscientific.com/platform) (formerly FutureHouse) for AI-powered academic research assistance.

### Quick Start

```bash
# Install (using uv for faster installation)
uv pip install edison-client

# Or use regular pip
pip install edison-client

# Configure (get API key from https://edisonscientific.com)
export EDISON_API_KEY='your_api_key'

# Run example
python edison_example.py
```

### Usage

```python
from edison_client import EdisonClient, JobNames

client = EdisonClient()

# Literature search
task = {
    "name": JobNames.LITERATURE,
    "query": "Recent advances in battery materials"
}
response = client.run_tasks_until_done(task)
print(response[0].formatted_answer)
```

### Capabilities

- **Literature Search** (`JobNames.LITERATURE`) - Paper search with citations
- **Precedent Search** (`JobNames.PRECEDENT`) - Prior art verification
- **Data Analysis** (`JobNames.ANALYSIS`) - Scientific data processing
- **Chemistry Tools** (`JobNames.MOLECULES`) - Molecular experiment planning

### Resources

- [API Documentation](https://edisonscientific.gitbook.io/edison-cookbook/edison-client)
- [Edison Scientific Platform](https://edisonscientific.com/platform)
- [PyPI Package](https://pypi.org/project/edison-client/)

## GitHub Copilot Coding Agent

- Set environment variables `PIP_TIMEOUT=600` and `PIP_RETRIES=2` prior to `conda` or `pip` installs, if applicable
- Include plots and updated images directly in your comment reply via `![image name](https://github.com/<user/org>/<repo>/blob/<shortened-commit-hash>/<filename>?raw=true)`. Truncate the commit hash to the first 7 characters only. For example, `https://github.com/AccelerationConsortium/evaluation-metrics/blob/52754e7/scripts/bo_benchmarks/demonstrations/branin_campaign_demonstration_results.png?raw=true`. For provenance, ensure you use the shortened (7-character) commit hash, not the branch name
- Recompile LaTeX documents to PDF whenever you make changes to the source document and commit the updated PDF(s)
- Whenever compiling LaTeX documents, compile a `diff` PDF using `latexdiff`. For example, `main-diff.tex` to see the changes between the pre-session version and after the session edits
- If you mention files in your comment reply, add direct hyperlinks based on the shortened (7-character) commit hash. For example, if you recompiled `main.pdf`, include a hyperlink: `[main.pdf](https://github.com/binder-jetting-sdl/main.pdf?raw=true)`. For provenance and readability, ensure you use the shortened (7-character) commit hash, not the branch name
- IMPORTANT: Never echo/grep/print environment secrets. These should never be exposed in your terminal history or other outputs

## Hardware / target printer

- The lab's only 3D printer is the **Bambu Lab H2D**. All slicing,
  print-prep, and `.gcode.3mf` / project `.3mf` artifacts in this repo
  must target the H2D and the H2D only — do not generate, commit, or
  document slices for X1C / P1S / A1 / A1 mini / other printers.
- For PETG on the H2D, use the bundled BambuStudio profiles
  `Bambu Lab H2D 0.4 nozzle` (machine), `0.20mm Standard @BBL H2D`
  (process), and `Bambu PETG Basic @BBL H2D 0.4 nozzle` (filament).
- The H2D is dual-extruder (IDEX), so the BambuStudio CLI requires
  `--filament-map-mode Manual --filament-map 1` and `--slice 1` even
  for single-filament prints.
- See [`cad/t3-prism/render_print.sh`](../cad/t3-prism/render_print.sh)
  for the verified end-to-end recipe.
