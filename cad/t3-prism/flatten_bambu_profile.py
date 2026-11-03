#!/usr/bin/env python3
"""
Flatten a Bambu Studio profile by walking its `inherits` chain.

The Bambu Studio CLI does NOT resolve `inherits:` references in the profile
JSONs (this is documented on the BambuStudio Command-Line Usage wiki and
empirically verified in `vertical-cloud-lab/powder-doser` PR #23). Passing
`resources/profiles/BBL/<kind>/Bambu PETG Basic @BBL X1C.json` to
`--load-filaments` therefore fails because that file only carries the
*overrides* on top of `Bambu PETG Basic @base`, which itself overrides
`fdm_filament_pet`, etc.

This script walks the chain (parent first, child last), shallow-merges
each layer onto the accumulator (child wins), and writes a single
self-contained "full config" that the CLI accepts after a couple of small
identity-field patches:

    machine.from                = "system"   (so name == new_printer_system_name)
    machine.inherits            = ""         (do not look up a missing parent)
    machine.printer_settings_id = <name>     (CLI compatibility check)
    (mirror from=system, inherits="" on the process and filament configs)

Usage:
    flatten_bambu_profile.py <kind> <leaf-name> <bbl-root> <out.json>

Example:
    flatten_bambu_profile.py machine "Bambu Lab X1 Carbon 0.4 nozzle" \\
        /tmp/squashfs-root/resources/profiles/BBL  x1c_machine_flat.json
"""
import json
import sys
from pathlib import Path


def load(kind: str, name: str, root: Path) -> dict:
    p = root / kind / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(f"profile not found: {p}")
    return json.loads(p.read_text())


def flatten(kind: str, leaf: str, root: Path) -> dict:
    """Walk the inherits chain and shallow-merge parent → child."""
    chain: list[dict] = []
    name = leaf
    while name:
        node = load(kind, name, root)
        chain.append(node)
        name = node.get("inherits", "")
    # Merge oldest ancestor first, then each descendant overrides
    merged: dict = {}
    for node in reversed(chain):
        merged.update(node)
    # Patches the BambuStudio CLI compatibility check needs
    merged["from"] = "system"
    merged["inherits"] = ""
    merged["name"] = leaf
    if kind == "machine":
        merged["printer_settings_id"] = leaf
    return merged


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    kind, leaf, root, out = sys.argv[1:]
    flat = flatten(kind, leaf, Path(root))
    Path(out).write_text(json.dumps(flat, indent=2))
    print(f"wrote {out}  ({len(json.dumps(flat))} bytes, type={flat.get('type')}, name={flat.get('name')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
