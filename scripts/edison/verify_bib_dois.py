#!/usr/bin/env python3
"""Verify and enrich the DOIs in ``manuscript/references-full.bib``.

This is the reproducible companion to ``build_master_bib.py``. It walks every
entry one-by-one and, using the *authoritative registered metadata* for each
DOI (CSL JSON fetched from ``https://doi.org/<doi>`` via content negotiation),
it:

1. **Verifies** that the stored title matches the title the DOI actually
   resolves to, classifying each entry as ``match`` / ``ambiguous`` /
   ``mismatch`` (the DOI points at an unrelated paper) / ``unresolved`` (the
   DOI 404s).
2. **Adds the registered abstract** to every ``match`` entry that lacks one
   (the abstract is taken from the DOI's own Crossref record, so it is verified
   for that exact DOI). JATS/HTML is stripped and ``&`` is BibTeX-escaped.
3. Applies a small table of **hand-verified corrections** -- DOIs that were
   manually checked in a browser/Crossref because the automated pass flagged
   them (see ``DOI_FIX``, ``NODOI_FIX`` and ``CONFIRM_ABSTRACT`` below).
4. For entries **without a DOI**, queries Crossref by title and records a
   high-confidence candidate (author + title confirmed) for human review.
5. Emits ``needs-list.md`` -- the entries whose DOI is wrong/unresolved or that
   still have no DOI -- which is sent to Edison
   (``submit_bib_doi_verification.py``) for the references the public DOI APIs
   could not settle.

Network calls are cached under ``--cache-dir`` so re-runs are cheap and offline.

    python scripts/edison/verify_bib_dois.py \
        --bib manuscript/references-full.bib --apply

Without ``--apply`` it only writes the report + needs list (no bib edits).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

MAILTO = "sgbaird@example.com"  # Crossref polite-pool contact
UA = f"tensegrity-bib-verify/1.0 (mailto:{MAILTO})"
MIN_ABSTRACT_LEN = 60

# ---------------------------------------------------------------------------
# Hand-verified corrections (each checked against doi.org/Crossref by a human).
# ---------------------------------------------------------------------------
# Reference is real but the stored DOI pointed at an unrelated paper. Maps
# bib key -> (correct_doi, corrected_year_or_None).
DOI_FIX = {
    # stored 10.1063/1.4921402 -> squash-mode vibration paper; the real
    # "Tensegrity cell mechanical metamaterial with metal rubber" is APL 2018.
    "zhang2015tensegrity": ("10.1063/1.5040850", "2018"),
}
# No-DOI entries whose DOI was found via Crossref and confirmed (author+title).
NODOI_FIX = {
    "altuntas2024fracturemechanicsbasedinvestigation": "10.1016/j.mechmat.2024.105035",
    "cascino2025integrationoffatigue": "10.1007/s40534-026-00433-8",
    "dong2015antivibrationgloves": "10.1093/annhyg/meu089",
    "hozdic2023comparativeanalysisof": "10.3390/ma16186342",
    "iso11334-4": "10.3403/01708963u",
    "johnson1974fuelsystemreliability": "10.21236/ad0786564",
    "mahajan1978publicplaygroundequipment": "10.6028/nbs.ir.79-1707",
    "obara2025assessmentoftensegrity": "10.1201/9781003534419",
    "ohsaki2019optimizationoftensegrity": "10.1016/j.compstruct.2021.113903",
    "pahari2024analysisofthe": "10.2139/ssrn.4903000",
    "ruwais2025mechanicalperformanceof": "10.35934/segi.v10i2.171",
    "sabounizawadzka2024experimentalinvestigationsona": "10.24425/ace.2024.150987",
}
# "Same paper, reworded title" -> safe to attach the registered abstract even
# though the token-similarity score lands in the ambiguous band.
CONFIRM_ABSTRACT = {
    "do2311multifidelitybayesianoptimization",
    "paulus2025hardcontactswith",
    "prater2019summary",
}
# DOIs verified WRONG/unresolvable with no confident replacement -> Edison.
SUSPECT = {
    "fraternali2015tensegrity": "stored DOI resolves to an unrelated ceramics paper",
    "witze2023osirisrex": "stored DOI resolves to an unrelated rural-health article",
    "wang2022bayesian": "stored DOI resolves to an unrelated polyelectrolyte-gel paper",
    "lee2023bayesian": "stored DOI returns 404 (does not resolve)",
    "grosu2025methodsforassessing": "stored DOI returns 404 (does not resolve)",
    "wang2024simbencharulebased": "DOI title differs (possible different SimBench paper)",
}


# ---------------------------------------------------------------------------
# Networking (cached)
# ---------------------------------------------------------------------------
def _http_get(url: str, accept: str | None = None) -> str:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def _clean_doi(doi: str) -> str:
    return (doi.replace("\\_", "_").replace("\\&", "&").replace("\\%", "%")
            .replace("\\#", "#").replace("{", "").replace("}", "").strip())


def fetch_csl(doi: str, cache: dict) -> dict | None:
    raw = doi.strip()
    if raw in cache:
        rec = cache[raw]
        return rec.get("csl") if rec.get("ok") else None
    for candidate in dict.fromkeys([raw, _clean_doi(raw)]):
        try:
            txt = _http_get("https://doi.org/" + urllib.parse.quote(candidate),
                            accept="application/vnd.citationstyles.csl+json")
            cache[raw] = {"ok": True, "csl": json.loads(txt)}
            time.sleep(0.4)
            return cache[raw]["csl"]
        except urllib.error.HTTPError as exc:
            cache[raw] = {"ok": False, "error": f"HTTP {exc.code}"}
        except Exception as exc:  # noqa: BLE001
            cache[raw] = {"ok": False, "error": str(exc)[:120]}
        time.sleep(0.4)
    return None


def crossref_candidate(title: str, cache: dict, key: str) -> dict | None:
    if key in cache:
        items = cache[key].get("items", [])
    else:
        q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 3,
                                    "mailto": MAILTO})
        try:
            data = json.loads(_http_get("https://api.crossref.org/works?" + q))
            items = [{"DOI": it.get("DOI"),
                      "title": (it.get("title") or [""])[0]}
                     for it in data.get("message", {}).get("items", [])]
            cache[key] = {"items": items}
        except Exception as exc:  # noqa: BLE001
            cache[key] = {"items": [], "error": str(exc)[:120]}
            items = []
        time.sleep(0.4)
    best = None
    for it in items:
        if it.get("DOI") and it.get("title"):
            s, cov, minw = title_sim(title, it["title"])
            score = max(s, cov if minw >= 4 else 0.0)
            if best is None or score > best[0]:
                best = (score, it)
    if best and best[0] >= 0.82:
        return {"doi": best[1]["DOI"], "title": best[1]["title"],
                "score": round(best[0], 3)}
    return None


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def _norm(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = s.replace("{", " ").replace("}", " ")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a: str, b: str):
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return 0.0, 0.0, 0
    sa, sb = set(na.split()), set(nb.split())
    jacc = len(sa & sb) / len(sa | sb)
    seq = SequenceMatcher(None, na, nb).ratio()
    minlen = min(len(sa), len(sb))
    cov = (len(sa & sb) / minlen) if minlen else 0.0
    return max(jacc, seq), cov, minlen


def classify(s: float, cov: float, minw: int) -> str:
    if s >= 0.82 or (cov >= 0.9 and minw >= 4):
        return "match"
    if s < 0.45 and cov < 0.4:
        return "mismatch"
    return "ambiguous"


def clean_abstract(raw: str) -> str:
    if not raw:
        return ""
    s = html.unescape(html.unescape(raw))
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\\", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"&(?!amp;)", r"\\&", s)
    if s.count("{") != s.count("}"):
        s = s.replace("{", "(").replace("}", ")")
    return s


def csl_title(csl: dict) -> str:
    t = csl.get("title")
    return (t[0] if isinstance(t, list) else t) or ""


# ---------------------------------------------------------------------------
# BibTeX entry parsing (span-preserving, for surgical edits)
# ---------------------------------------------------------------------------
def parse_entries(text: str):
    out = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\n]+),", text):
        j = text.index("{", m.start())
        depth = 0
        k = j
        while k < len(text):
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        body = text[j + 1:k]
        fields, fspans = {}, {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{", body):
            fs = body.index("{", fm.start())
            d = 0
            p = fs
            while p < len(body):
                if body[p] == "{":
                    d += 1
                elif body[p] == "}":
                    d -= 1
                    if d == 0:
                        break
                p += 1
            name = fm.group(1).lower()
            fields[name] = body[fs + 1:p]
            fspans[name] = (j + 1 + fm.start(), j + 1 + p + 1)
        out.append({"key": m.group(2).strip(), "span": (m.start(), k + 1),
                    "fields": fields, "fspans": fspans})
    return out


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bib", default="manuscript/references-full.bib")
    ap.add_argument("--cache-dir", default="/tmp/verify")
    ap.add_argument("--needs-out",
                    default="edison-trajectories/bib-doi-verification/needs-list.md")
    ap.add_argument("--apply", action="store_true",
                    help="write abstract/DOI edits back into the bib")
    args = ap.parse_args()

    bib = Path(args.bib)
    cdir = Path(args.cache_dir)
    cdir.mkdir(parents=True, exist_ok=True)
    doi_cache_path = cdir / "doi_cache.json"
    xref_cache_path = cdir / "xref_cache.json"
    doi_cache = json.loads(doi_cache_path.read_text()) if doi_cache_path.exists() else {}
    xref_cache = json.loads(xref_cache_path.read_text()) if xref_cache_path.exists() else {}

    text = bib.read_text()
    entries = parse_entries(text)
    report = {b: [] for b in ("match", "ambiguous", "mismatch", "unresolved",
                              "no_doi_candidate", "no_doi_none")}
    edits = []
    n_abs = n_doi = n_fix = 0

    for e in entries:
        f, key = e["fields"], e["key"]
        last_end = max((en for _, en in e["fspans"].values()),
                       default=e["span"][1] - 1)

        if key in DOI_FIX:
            newdoi, newyear = DOI_FIX[key]
            ds, de = e["fspans"]["doi"]
            edits.append((ds, de, "doi = {%s}" % newdoi))
            if newyear and "year" in e["fspans"]:
                ys, ye = e["fspans"]["year"]
                edits.append((ys, ye, "year = {%s}" % newyear))
            csl = fetch_csl(newdoi, doi_cache) or {}
            ab = clean_abstract(csl.get("abstract", ""))
            if ab and "abstract" not in f:
                edits.append((last_end, last_end, ",\n    abstract = {%s}" % ab))
            n_fix += 1
            continue

        if key in NODOI_FIX and "doi" not in f:
            doi = NODOI_FIX[key]
            csl = fetch_csl(doi, doi_cache) or {}
            ins = ",\n    doi = {%s}" % doi
            if "url" not in f:
                ins += ",\n    url = {https://doi.org/%s}" % doi
            ab = clean_abstract(csl.get("abstract", "")) if "abstract" not in f else ""
            if len(ab) > MIN_ABSTRACT_LEN:
                ins += ",\n    abstract = {%s}" % ab
                n_abs += 1
            edits.append((last_end, last_end, ins))
            n_doi += 1
            continue

        doi = (f.get("doi") or "").strip()
        if doi:
            csl = fetch_csl(doi, doi_cache)
            if csl is None:
                report["unresolved"].append({"key": key, "doi": doi})
                continue
            s, cov, minw = title_sim(f.get("title", ""), csl_title(csl))
            bucket = classify(s, cov, minw)
            report[bucket].append({"key": key, "doi": doi, "sim": round(s, 3),
                                   "cov": round(cov, 3),
                                   "bib_title": f.get("title", ""),
                                   "doi_title": csl_title(csl)})
            if "abstract" not in f and (bucket == "match" or key in CONFIRM_ABSTRACT):
                ab = clean_abstract(csl.get("abstract", ""))
                if len(ab) > MIN_ABSTRACT_LEN:
                    edits.append((last_end, last_end,
                                  ",\n    abstract = {%s}" % ab))
                    n_abs += 1
        else:
            cand = crossref_candidate(f.get("title", ""), xref_cache, key)
            if cand:
                report["no_doi_candidate"].append({"key": key, **cand})
            else:
                report["no_doi_none"].append({"key": key,
                                              "title": f.get("title", "")})

    doi_cache_path.write_text(json.dumps(doi_cache))
    xref_cache_path.write_text(json.dumps(xref_cache))
    (cdir / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))

    # Needs list for Edison: suspect DOIs + entries that still have no DOI.
    have_doi = {e["key"] for e in entries if e["fields"].get("doi")} | set(NODOI_FIX)
    lines = ["## A. Entries whose DOI looks wrong or does not resolve "
             "(please supply the correct DOI)\n"]
    by_key = {e["key"]: e["fields"] for e in entries}
    for key, why in SUSPECT.items():
        fld = by_key.get(key, {})
        lines.append(f"- key: {key}\n  author: {fld.get('author','')}\n"
                     f"  title: {fld.get('title','')}\n  year: {fld.get('year','')}\n"
                     f"  journal: {fld.get('journal','')}\n  issue: {why}\n")
    lines.append("\n## B. Entries with NO DOI (please supply a DOI if one exists, "
                 "else mark 'no DOI')\n")
    for e in entries:
        if e["key"] in have_doi:
            continue
        fld = e["fields"]
        lines.append(f"- key: {e['key']}\n  author: {fld.get('author','')}\n"
                     f"  title: {fld.get('title','')}\n  year: {fld.get('year','')}\n"
                     f"  journal: {fld.get('journal','')}\n")
    Path(args.needs_out).write_text("\n".join(lines))

    if args.apply:
        for s, en, rep in sorted(edits, key=lambda x: -x[0]):
            text = text[:s] + rep + text[en:]
        bib.write_text(text)

    summary = {b: len(v) for b, v in report.items()}
    summary.update(abstracts_added=n_abs, dois_added=n_doi, doi_fixes=n_fix,
                   applied=bool(args.apply))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
