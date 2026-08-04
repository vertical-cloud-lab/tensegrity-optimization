"""Onshape REST: upload the T3-prism print STLs so dimensions can be verified
manually in Onshape before printing (PR #35 comment 4896509287; workflow
adapted from powder-doser PR #7 `cad/meta-tools/onshape_upload_assembly.py`).

Uploads the three production STLs (struts / struts+scaffold / cables) plus the
fused single-material body to a public document owned by the "Vertical Cloud
Lab" Onshape classroom, then reads each imported Part Studio's bounding box
back through the API and prints it in millimetres — a programmatic check that
the STL imported at mm scale (Onshape reports bounding boxes in metres; a
unit mix-up shows up as a 1000x error immediately).

Reads ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY from env (HMAC-signed REST).
Real document/element ids are printed to stdout only and never committed.

Overrides (same conventions as the powder-doser script)::

    ONSHAPE_TARGET_DOC_NAME=<doc name>   # default: Tensegrity T3-prism (PR #35)
    ONSHAPE_OWNER_NAME=<classroom name>  # default: Vertical Cloud Lab
    ONSHAPE_OWNER_ID=<companyId>         # takes precedence over name
    ONSHAPE_PUBLIC=0                     # opt out of public visibility

Run with::

    python3 cad/t3-prism/onshape_upload_t3prism.py

Any other set of STLs (e.g. the per-specimen BO batch pairs) can be pushed to
their own document without editing the file::

    python3 cad/t3-prism/onshape_upload_t3prism.py \\
        --doc-name "T3-prism Sobol batch 01 (PR #35)" --jobs 6 \\
        --stl spec00-struts=bo/per-specimen-stls/t3-prism-bo-spec00-struts.stl \\
        --stl spec00-cables=bo/per-specimen-stls/t3-prism-bo-spec00-cables.stl
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import datetime
import hashlib
import hmac
import json
import os
import pathlib
import secrets
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com")
HERE = pathlib.Path(__file__).resolve().parent

TARGET_DOC_NAME = os.environ.get(
    "ONSHAPE_TARGET_DOC_NAME", "Tensegrity T3-prism (PR #35)"
)
OWNER_NAME = os.environ.get("ONSHAPE_OWNER_NAME", "Vertical Cloud Lab")
OWNER_ID = os.environ.get("ONSHAPE_OWNER_ID")
OWNER_TYPE = int(os.environ.get("ONSHAPE_OWNER_TYPE", "1"))  # 1 = COMPANY


def _truthy(val: str) -> bool:
    return val.strip().lower() not in ("", "0", "false", "no", "off")


IS_PUBLIC = _truthy(os.environ.get("ONSHAPE_PUBLIC", "1"))

# The three STLs the team prints from (PR #35 comment 4815672887) plus the
# fused single-material body for reference.
STLS = [
    ("t3-prism-struts", HERE / "t3-prism-struts.stl"),
    ("t3-prism-struts-scaffold", HERE / "t3-prism-struts-scaffold.stl"),
    ("t3-prism-cables", HERE / "t3-prism-cables.stl"),
    ("t3-prism-full", HERE / "t3-prism.stl"),
]


def _sign(method: str, secret_key: bytes, access_key: str, path: str,
          query: str, ctype: str) -> dict:
    nonce = secrets.token_hex(13)[:25]
    date = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    sig_str = "\n".join([method, nonce, date, ctype, path, query, ""]).lower()
    sig = base64.b64encode(
        hmac.new(secret_key, sig_str.encode("utf-8"), hashlib.sha256).digest()
    ).decode()
    return {
        "Date": date,
        "On-Nonce": nonce,
        "Authorization": f"On {access_key}:HmacSHA256:{sig}",
        "Content-Type": ctype,
        "Accept": "application/json",
    }


def signed(method: str, access: str, secret: bytes, path: str,
           query: str = "", body: bytes | None = None,
           ctype: str = "application/json"):
    headers = _sign(method, secret, access, path, query, ctype)
    url = BASE + path + (("?" + query) if query else "")
    req = urllib.request.Request(url, method=method, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def multipart_signed(access: str, secret: bytes, path: str, fields: dict,
                     file_name: str, file_bytes: bytes):
    boundary = "----onshape" + uuid.uuid4().hex
    ctype = f"multipart/form-data; boundary={boundary}"
    parts = []
    for k, v in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; "
            f"name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        )
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"{file_name}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n".encode()
        + file_bytes
        + f"\r\n--{boundary}--\r\n".encode()
    )
    body = b"".join(parts)
    headers = _sign("POST", secret, access, path, "", ctype)
    headers["Accept"] = "application/json;charset=UTF-8;qs=0.09"
    req = urllib.request.Request(BASE + path, method="POST", data=body,
                                 headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def _resolve_owner(access: str, sk: bytes) -> tuple[str | None, int]:
    if OWNER_ID:
        return OWNER_ID, OWNER_TYPE
    if not OWNER_NAME:
        return None, 0
    code, body = signed("GET", access, sk, "/api/v6/companies")
    if code == 200:
        for c in json.loads(body).get("items", []):
            if c.get("name") == OWNER_NAME:
                return c["id"], 1
    code, body = signed("GET", access, sk, "/api/v6/teams")
    if code == 200:
        for t in json.loads(body).get("items", []):
            if t.get("name") == OWNER_NAME:
                return t["id"], 2
    print(f"  [owner] no company/team named {OWNER_NAME!r}; "
          "falling back to user-owned")
    return None, 0


def _resolve_doc(access: str, sk: bytes) -> tuple[str, str, bool, str]:
    """Return (did, wid, created, owner_label) for TARGET_DOC_NAME,
    creating it (classroom-owned, public) on first run."""
    owner_id, owner_type = _resolve_owner(access, sk)
    owner_label = (f"{OWNER_NAME} (companyId=<redacted>, type={owner_type})"
                   if owner_id else "calling user")

    def _scan(filter_id: int, extra: str = "") -> str | None:
        offset = 0
        while True:
            q = (f"filter={filter_id}&limit=20&offset={offset}"
                 f"&sortColumn=modifiedAt&sortOrder=desc{extra}")
            code, body = signed("GET", access, sk, "/api/v6/documents", q)
            if code != 200:
                return None
            page = json.loads(body)
            for doc in page.get("items", []):
                if doc.get("name") == TARGET_DOC_NAME:
                    return doc["id"]
            if not page.get("next") and len(page.get("items", [])) < 20:
                return None
            offset += 20

    did = _scan(0)
    if did is None and owner_id:
        did = _scan(7, f"&owner={owner_id}&ownerType={owner_type}")

    if did is not None:
        code, body = signed("GET", access, sk, f"/api/v6/documents/{did}")
        if code != 200:
            raise SystemExit(f"GET /documents/<did> HTTP {code}: {body[:200]!r}")
        wid = json.loads(body)["defaultWorkspace"]["id"]
        return did, wid, False, owner_label

    doc_payload: dict = {
        "name": TARGET_DOC_NAME,
        "description": ("T3-prism print STLs (PLA struts / PLA struts+scaffold"
                        " / TPU cables) for manual dimension verification "
                        "before printing. Auto-created by "
                        "cad/t3-prism/onshape_upload_t3prism.py (PR #35)."),
        "isPublic": IS_PUBLIC,
    }
    if owner_id:
        doc_payload["ownerId"] = owner_id
        doc_payload["ownerType"] = owner_type
    code, body = signed("POST", access, sk, "/api/v6/documents", "",
                        body=json.dumps(doc_payload).encode("utf-8"))
    if code not in (200, 201):
        raise SystemExit(f"POST /documents HTTP {code}: {body[:300]!r}")
    j = json.loads(body)
    return j["id"], j["defaultWorkspace"]["id"], True, owner_label


def _upload_stl(access: str, sk: bytes, did: str, wid: str,
                name: str, stl_path: pathlib.Path) -> list[str]:
    """Upload one STL with translate=true; return new element ids."""
    display_name = f"{name}.stl"
    fields = {
        "encodedFilename": display_name,
        "fileName": display_name,
        "translate": "true",
        "storeInDocument": "true",
        "createComposite": "false",
        "splitAssembliesIntoMultipleDocuments": "false",
        "flattenAssemblies": "false",
        "yAxisIsUp": "false",
        "allowFaultyParts": "true",
        # STLs are unitless; the SCAD/STL pipeline is millimetres throughout.
        "unit": "MILLIMETER",
    }
    code, body = multipart_signed(
        access, sk, f"/api/v6/blobelements/d/{did}/w/{wid}",
        fields, display_name, stl_path.read_bytes(),
    )
    if code not in (200, 201):
        print(f"  [{name}] upload HTTP {code}: "
              f"{body[:300].decode(errors='replace')}")
        return []
    j = json.loads(body)
    tid = j.get("translationId") or j.get("id")
    if not tid:
        print(f"  [{name}] no translationId in response")
        return []
    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(5)
        code, body = signed("GET", access, sk, f"/api/v6/translations/{tid}")
        if code != 200:
            continue
        t = json.loads(body)
        state = t.get("requestState")
        if state == "DONE":
            return t.get("resultElementIds") or []
        if state == "FAILED":
            print(f"  [{name}] translation FAILED: {t.get('failureReason')}")
            return []
    print(f"  [{name}] translation poll timed out")
    return []


def _bbox_mm(access: str, sk: bytes, did: str, wid: str,
             eid: str) -> str | None:
    """Read a Part Studio's bounding box and format it in mm.

    `/partstudios/.../boundingboxes` reports **millimetres** already (verified
    against the local STL extents), so no unit conversion is applied here — an
    earlier ``* 1000`` made every import look 1000x oversized.
    """
    code, body = signed(
        "GET", access, sk,
        f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/boundingboxes",
    )
    if code != 200:
        return None
    j = json.loads(body)
    try:
        lo = (j["lowX"], j["lowY"], j["lowZ"])
        hi = (j["highX"], j["highY"], j["highZ"])
    except KeyError:
        return None
    dims = [h - l for l, h in zip(lo, hi)]
    return (f"{dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm "
            f"(X x Y x Z)")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--stl", action="append", default=[], metavar="NAME=PATH",
        help="upload this STL as Part Studio NAME (repeatable); replaces the "
             "default four production STLs when given",
    )
    ap.add_argument(
        "--doc-name", default=None,
        help=f"Onshape document name (default: {TARGET_DOC_NAME!r})",
    )
    ap.add_argument(
        "--jobs", type=int, default=1,
        help="concurrent uploads/translations (default 1)",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    global TARGET_DOC_NAME
    args = _parse_args(argv)
    if args.doc_name:
        TARGET_DOC_NAME = args.doc_name

    stls = STLS
    if args.stl:
        stls = []
        for spec in args.stl:
            if "=" not in spec:
                print(f"--stl expects NAME=PATH, got {spec!r}")
                return 2
            name, _, path = spec.partition("=")
            stls.append((name, pathlib.Path(path).resolve()))

    access = os.environ.get("ONSHAPE_ACCESS_KEY")
    secret = os.environ.get("ONSHAPE_SECRET_KEY")
    if not access or not secret:
        print("ONSHAPE_ACCESS_KEY/SECRET_KEY not set; aborting.")
        return 1
    sk = secret.encode("utf-8")
    print(f"BASE = {BASE}")

    did, wid, created, owner_label = _resolve_doc(access, sk)
    print(f"target document ({'created' if created else 'found'}): "
          f"{TARGET_DOC_NAME!r}")
    print(f"  owner: {owner_label}   public: {IS_PUBLIC}")
    doc_url = f"{BASE}/documents/{did}/w/{wid}"
    print(f"document URL: {doc_url}")

    to_upload = [(n, p) for n, p in stls if p.exists()]
    for n, p in stls:
        if not p.exists():
            print(f"  [{n}] missing at {p}, skipping")

    print(f"\n== uploading {len(to_upload)} STLs "
          f"(jobs={max(1, args.jobs)}) ==")

    def _one(item):
        name, stl_path = item
        print(f"[{name}] uploading {stl_path.name} "
              f"({stl_path.stat().st_size} bytes) ...", flush=True)
        eids = _upload_stl(access, sk, did, wid, name, stl_path)
        boxes = [(eid, _bbox_mm(access, sk, did, wid, eid)) for eid in eids]
        for eid, bbox in boxes:
            print(f"  [{name}] -> {BASE}/documents/{did}/w/{wid}/e/{eid}\n"
                  f"     bounding box: {bbox or '(unavailable)'}", flush=True)
        return name, boxes

    if max(1, args.jobs) > 1:
        with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
            results = list(ex.map(_one, to_upload))
    else:
        results = [_one(item) for item in to_upload]

    print("\n== Clickable Onshape URLs ==")
    print(f"Document: {doc_url}")
    for name, boxes in results:
        if not boxes:
            print(f"  {name}: (upload failed or no element id)")
        for eid, bbox in boxes:
            print(f"  {name}: {BASE}/documents/{did}/w/{wid}/e/{eid}"
                  f"   [{bbox or 'bbox unavailable'}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
