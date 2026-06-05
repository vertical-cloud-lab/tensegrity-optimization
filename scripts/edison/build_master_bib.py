#!/usr/bin/env python3
"""Synthesize a master BibTeX library from every Edison trajectory + committed
``.bib`` file across all branches of this repository.

Some Edison tasks are committed only as ``*-SUBMITTED.json`` placeholders (the
task id and attachments, but no results). Where the underlying job is a
``LITERATURE_HIGH`` (PaperQA) task, its completed result can be re-fetched via
the Edison API and dumped into the ``--json-dir`` so its references are folded
in too::

    from edison_client import EdisonClient
    c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
    open(out, "w").write(c.get_task(task_id).model_dump_json())

The script is intentionally input-driven so it is reproducible:

1. Collect every ``edison-trajectories/**/*.json`` blob from every branch
   (deduplicated by content hash) into a working directory, e.g.::

       for b in $(git branch -r | grep -v HEAD | sed 's# *origin/##'); do
         git ls-tree -r --name-only "origin/$b" | grep 'edison-trajectories.*\\.json$' \\
           | while read f; do
               git show "origin/$b:$f" > "/tmp/edison_all/$(basename "$f")" 2>/dev/null
             done
       done

   (a small Python helper that dedupes by ``sha1`` is used in practice).

2. Collect every committed project ``.bib`` file the same way (excluding the
   ``sterling-cv/`` personal-publication lists, which are a CV artifact rather
   than project/Edison literature).

3. Run::

       python scripts/edison/build_master_bib.py \\
           --json-dir /tmp/edison_all --bib-dir /tmp/bibsrc \\
           --out manuscript/references-full.bib

Reference data is extracted from two complementary representations that the
PaperQA (``LITERATURE_HIGH``) and crow (``ANALYSIS``) jobs emit:

* **Inline ``BibTex:`` blocks** inside the agent-state message contents -- the
  richest source (explicit ``author``/``title``/``journal``/``doi`` fields and
  frequently a following ``Abstract:`` block).
* **Numbered ``References`` lists** inside the ``formatted_answer`` field --
  used as a fallback for tasks whose raw evidence blocks were not retained, so
  that no cited key is dropped.

Entries are deduplicated by citation key (and, secondarily, by DOI). When the
same key appears in multiple sources the richest record wins, and the union of
the source task IDs is recorded in a leading comment so each entry is
traceable.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# --- BibTeX block parsing ----------------------------------------------------

ENTRY_RE = re.compile(r"@(\w+)\s*\{", re.M)
FIELD_RE = re.compile(r'(\w+)\s*=\s*(?:"(.*?)"|\{(.*?)\})\s*,?\s*$', re.S | re.M)


def _balanced_block(text: str, start: int):
    """Return (substring, end_index) of a ``@type{...}`` entry starting at
    ``start`` (index of '@') by counting braces."""
    brace = text.find("{", start)
    if brace == -1:
        return None
    depth = 0
    i = brace
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1], i + 1
        i += 1
    return None


def parse_bib_entries(text: str):
    """Yield (entry_type, key, fields_dict) for every @-entry in ``text``."""
    for m in ENTRY_RE.finditer(text):
        block = _balanced_block(text, m.start())
        if not block:
            continue
        raw, _ = block
        etype = m.group(1).lower()
        if etype in ("comment", "string", "preamble"):
            continue
        head = raw[: raw.find("{") + 1]
        body = raw[len(head) : -1]
        keymatch = re.match(r"\s*([^,\s]+)\s*,", body)
        if not keymatch:
            continue
        key = keymatch.group(1).strip()
        fieldtext = body[keymatch.end() :]
        fields = {}
        for fm in FIELD_RE.finditer(fieldtext):
            name = fm.group(1).lower()
            val = fm.group(2) if fm.group(2) is not None else fm.group(3)
            if val is not None:
                fields[name] = " ".join(val.split())
        yield etype, key, fields


# --- JSON walking ------------------------------------------------------------

def all_strings(obj):
    out = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            out.append(o)

    walk(obj)
    return out


def find_fields(obj, name):
    out = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == name and isinstance(v, str):
                    out.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(obj)
    return out


ABSTRACT_RE = re.compile(
    r"Abstract:\s*\n(.*?)(?:\n\s*\n(?:Relevant Snippet|BibTex|Valid Text Names)|\Z)",
    re.S,
)


def extract_from_json(path: Path):
    """Return list of (etype, key, fields) extracted from one trajectory JSON."""
    try:
        data = json.load(open(path))
    except Exception:
        return []
    task_id = data.get("task_id") or data.get("id") or path.stem
    results = []
    seen_local = set()

    for content in all_strings(data):
        if "BibTex:" not in content:
            continue
        for m in re.finditer(r"@\w+\s*\{", content):
            blk = _balanced_block(content, m.start())
            if not blk:
                continue
            raw, end = blk
            entries = list(parse_bib_entries(raw))
            if not entries:
                continue
            etype, key, fields = entries[0]
            tail = content[end : end + 4000]
            am = ABSTRACT_RE.match(tail.lstrip("\n"))
            if not am:
                am = ABSTRACT_RE.search(tail[:2500])
            if am:
                abstract = " ".join(am.group(1).split())
                if 40 < len(abstract) < 6000:
                    fields.setdefault("abstract", abstract)
            fields["_task"] = task_id
            sig = (key, fields.get("doi", ""))
            if sig in seen_local:
                continue
            seen_local.add(sig)
            results.append((etype, key, fields))

    if results:
        return results

    # Fallback: parse numbered References list from formatted_answer
    for fa in find_fields(data, "formatted_answer"):
        results.extend(parse_numbered_refs(fa, task_id))
        if results:
            break
    return results


NUMREF_RE = re.compile(
    r"^\s*\d+\.\s*\(([^)]+?)\s+pages[^)]*\):\s*(.*?)(?=\n\s*\d+\.\s*\(|\Z)",
    re.S | re.M,
)


def parse_numbered_refs(text: str, task_id: str):
    out = []
    idx = text.rfind("\nReferences")
    region = text[idx:] if idx != -1 else text
    seen = set()
    for m in NUMREF_RE.finditer(region):
        key = m.group(1).strip()
        if key in seen:
            continue
        seen.add(key)
        body = " ".join(m.group(2).split())
        fields = {"_task": task_id}
        doi = re.search(r"doi:(\S+?)(?:\.\s|\s|$)", body)
        if doi:
            fields["doi"] = doi.group(1).rstrip(".")
        url = re.search(r"URL:\s*(\S+?),", body)
        if url:
            fields["url"] = url.group(1)
        year = re.search(r"\b(19|20)\d{2}\b", body)
        if year:
            fields["year"] = year.group(0)
        body = re.sub(r"This article has [\d,]+ citations?\.?", "", body).strip()
        # Split authors / title / venue. Author lists contain internal initials
        # ("J.", "N.G."), so a period-after-lowercase heuristic alone is unreliable
        # when surnames are ALL CAPS or non-Latin. The citation key encodes the
        # title start (<surname><year><titlewords>), so use it to locate the
        # author/title boundary robustly, falling back to the heuristic.
        title_start = None
        km = re.match(r"^[^\d]*\d{4}(.+)$", key)
        if km and km.group(1):
            stub = km.group(1)
            norm_chars = []  # (lowercased alnum char, original index)
            for i, ch in enumerate(body):
                if ch.isalnum():
                    norm_chars.append((ch.lower(), i))
            norm = "".join(c for c, _ in norm_chars)
            pos = norm.find(stub[: min(len(stub), 24)])
            if pos != -1:
                title_start = norm_chars[pos][1]
        if title_start is not None:
            fields["author"] = body[:title_start].strip().rstrip(".,").strip()
            rest = body[title_start:]
            tb = re.search(r"(?<=[a-z0-9)])\.\s+(?=[A-Z0-9])", rest)
            if tb:
                fields["title"] = rest[: tb.start() + 1].strip().rstrip(".")
                venue = rest[tb.end():]
            else:
                fields["title"] = rest.strip().rstrip(".")
                venue = ""
        else:
            boundaries = [mm.start() + 1 for mm in re.finditer(r"(?<=[a-z])\.\s+(?=[A-Z0-9])", body)]
            if len(boundaries) >= 2:
                fields["author"] = body[: boundaries[0]].strip().rstrip(".")
                fields["title"] = body[boundaries[0] + 1 : boundaries[1]].strip().rstrip(".")
                venue = body[boundaries[1] + 1 :]
            elif len(boundaries) == 1:
                fields["author"] = body[: boundaries[0]].strip().rstrip(".")
                venue = body[boundaries[0] + 1 :]
            else:
                venue = body
        jrest = re.split(r",?\s*(?:pages|URL:|doi:|\d{1,4}:)", venue)[0]
        # Strip a trailing ", <Month> <Year>" or ", <Year>" date tail.
        jrest = re.sub(
            r",?\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s*(?:19|20)\d{2}\.?\s*$",
            "",
            jrest,
        )
        jrest = jrest.strip().rstrip(",.")
        if jrest and jrest.lower() != "unknown journal" and not re.fullmatch(r"\d{4}", jrest):
            fields["journal"] = jrest
        out.append(("article", key, fields))
    return out


# --- merge / scoring ---------------------------------------------------------

RICH_FIELDS = ("author", "title", "journal", "year", "doi", "abstract", "volume", "pages")


def richness(fields: dict) -> int:
    return sum(2 if f == "abstract" else 1 for f in RICH_FIELDS if fields.get(f))


def norm_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def merge(into: dict, etype, key, fields):
    nk = norm_key(key)
    doi = fields.get("doi", "").lower().strip()
    existing_k = None
    if nk in into:
        existing_k = nk
    elif doi:
        for k2, (_et2, _key2, f2) in into.items():
            if f2.get("doi", "").lower().strip() == doi:
                existing_k = k2
                break
    if existing_k is None:
        into[nk] = (etype, key, dict(fields))
        return
    et2, key2, f2 = into[existing_k]
    tasks = set()
    for src in (f2, fields):
        for t in str(src.get("_task", "")).split(","):
            t = t.strip()
            if t:
                tasks.add(t)
    if richness(fields) > richness(f2):
        merged = dict(f2)
        merged.update({k: v for k, v in fields.items() if v})
        winner_key, winner_type = key, etype
    else:
        merged = dict(fields)
        merged.update({k: v for k, v in f2.items() if v})
        winner_key, winner_type = key2, et2
    if not merged.get("abstract"):
        for src in (f2, fields):
            if src.get("abstract"):
                merged["abstract"] = src["abstract"]
                break
    merged["_task"] = ", ".join(sorted(tasks))
    into[existing_k] = (winner_type, winner_key, merged)


# --- emit --------------------------------------------------------------------

FIELD_ORDER = [
    "author", "title", "year", "journal", "booktitle", "volume", "number",
    "issue", "pages", "month", "publisher", "institution", "doi", "url",
    "issn", "isbn", "note", "abstract",
]


def _clean_value(val: str) -> str:
    if not isinstance(val, str):
        return val
    val = (
        val.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&#39;", "'")
    )
    # Escape a bare ampersand for BibTeX without double-escaping existing \&.
    val = re.sub(r"(?<!\\)&", r"\\&", val)
    return val


def emit(entries: dict) -> str:
    lines = [
        "% =====================================================================",
        "% references-full.bib -- MASTER synthesized bibliography",
        "%",
        "% Auto-generated by scripts/edison/build_master_bib.py from every Edison",
        "% trajectory (LITERATURE_HIGH + ANALYSIS) and every committed project",
        "% .bib file across all branches of this repository. Do not edit by hand;",
        "% re-run the generator to refresh. The curated manuscript bibliography",
        "% used by the asmejour build remains manuscript/references.bib.",
        "%",
        f"% Total entries: {len(entries)}",
        "% =====================================================================",
        "",
    ]
    for nk in sorted(entries):
        etype, key, fields = entries[nk]
        tasks = fields.get("_task", "")
        if tasks:
            lines.append(f"% source: {tasks}")
        lines.append(f"@{etype}{{{key},")
        keys = [f for f in FIELD_ORDER if f in fields and fields[f]]
        keys += [
            f for f in fields
            if f not in FIELD_ORDER and not f.startswith("_") and fields[f]
        ]
        for i, f in enumerate(keys):
            val = _clean_value(fields[f])
            comma = "," if i < len(keys) - 1 else ""
            lines.append(f"    {f} = {{{val}}}{comma}")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-dir", required=True)
    ap.add_argument("--bib-dir", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    entries: dict = {}
    n_json = n_bib = 0

    for p in sorted(Path(args.json_dir).rglob("*.json")):
        recs = extract_from_json(p)
        if recs:
            n_json += 1
        for etype, key, fields in recs:
            merge(entries, etype, key, fields)

    if args.bib_dir:
        for p in sorted(Path(args.bib_dir).glob("*.bib")):
            if "sterling-cv" in p.name:
                continue  # personal CV publication list, not project literature
            n_bib += 1
            text = p.read_text(errors="replace")
            for etype, key, fields in parse_bib_entries(text):
                fields["_task"] = f"committed:{p.name}"
                merge(entries, etype, key, fields)

    out = Path(args.out)
    out.write_text(emit(entries))
    n_abs = sum(1 for _, (_, _, f) in entries.items() if f.get("abstract"))
    print(f"trajectories with refs: {n_json}; committed bibs: {n_bib}")
    print(f"unique entries: {len(entries)}; with abstracts: {n_abs}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
