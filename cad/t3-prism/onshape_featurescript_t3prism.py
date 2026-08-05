"""Onshape REST: build the T3-prism as a **live feature tree**, not an import.

Issue #95, "route C". Instead of uploading a tessellated STL (or even a clean
STEP) and getting a history-less dumb solid, this script:

  1. creates/【finds】 a document,
  2. creates a **Feature Studio** and pushes ``cad/t3-prism/t3-prism.fs`` into it
     (the FeatureScript port of ``t3-prism.scad``),
  3. compiles it server-side and reports any FeatureScript errors,
  4. cuts a **version** (custom features can only be referenced from a version,
     not a workspace),
  5. creates a **Part Studio** and adds the custom feature to its feature tree,
     with named parameters supplied as expressions,
  6. reads the regenerated feature's status + bounding box back in millimetres,
  7. optionally exports a true B-rep ``.step`` straight out of the Part Studio.

The result in Onshape is a Part Studio whose tree contains one editable
``T3 Prism (tensegrity)`` feature: double-click it, type a new number into
"Pocket Z (depth)", regenerate. Rollback and version history work. That is the
thing a STEP import can never give you.

Reads ``ONSHAPE_ACCESS_KEY`` / ``ONSHAPE_SECRET_KEY`` from env (HMAC-signed
REST, same scheme as ``onshape_upload_t3prism.py``). Document/element ids are
printed to stdout only and never committed.

Overrides::

    ONSHAPE_TARGET_DOC_NAME=<doc name>   # default: Tensegrity T3-prism (parametric)
    ONSHAPE_OWNER_NAME=<classroom name>  # default: Vertical Cloud Lab
    ONSHAPE_OWNER_ID=<companyId>         # takes precedence over name
    ONSHAPE_PUBLIC=0                     # opt out of public visibility

Run with::

    python3 cad/t3-prism/onshape_featurescript_t3prism.py
    python3 cad/t3-prism/onshape_featurescript_t3prism.py --export-step out.step
    python3 cad/t3-prism/onshape_featurescript_t3prism.py \\
        --param scaleFactor=1.5 --param 'pocketZ=7.1 mm' --param addAccelBottom=false
"""
from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import hmac
import json
import os
import pathlib
import re
import secrets
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com")
HERE = pathlib.Path(__file__).resolve().parent
FS_SOURCE = HERE / "t3-prism.fs"

# The exported `const` name in t3-prism.fs -- this is the featureType Onshape
# uses to look the custom feature up inside the referenced Feature Studio.
FEATURE_TYPE = "t3Prism"
FEATURE_NAME = "T3 Prism (tensegrity)"

TARGET_DOC_NAME = os.environ.get(
    "ONSHAPE_TARGET_DOC_NAME", "Tensegrity T3-prism (parametric)"
)
FS_ELEMENT_NAME = "T3Prism"
PS_ELEMENT_NAME = "T3-prism (parametric)"

OWNER_NAME = os.environ.get("ONSHAPE_OWNER_NAME", "Vertical Cloud Lab")
OWNER_ID = os.environ.get("ONSHAPE_OWNER_ID")
OWNER_TYPE = int(os.environ.get("ONSHAPE_OWNER_TYPE", "1"))  # 1 = COMPANY


def _truthy(val: str) -> bool:
    return val.strip().lower() not in ("", "0", "false", "no", "off")


IS_PUBLIC = _truthy(os.environ.get("ONSHAPE_PUBLIC", "1"))

# Onshape BTM type tags. The API rejects the older {"type": 134, "typeName":
# "BTMFeature"} envelope with a bare "Feature has invalid type"; the flattened
# "btType": "BTMFeature-134" form is what the current serializer accepts.
BT_FEATURE = "BTMFeature-134"
BT_QUANTITY = "BTMParameterQuantity-147"   # lengths, angles, plain reals
BT_BOOLEAN = "BTMParameterBoolean-144"
BT_ENUM = "BTMParameterEnum-145"

# Which parameters of the custom feature are booleans / enums. Everything else
# is sent as a quantity expression, which is also how Onshape stores reals.
BOOLEAN_PARAMS = {"useCaptiveCore", "addAccelTop", "addAccelBottom"}
ENUM_PARAMS = {"part": "T3Part"}


# --------------------------------------------------------------------------
# HMAC-signed transport (identical scheme to onshape_upload_t3prism.py)
# --------------------------------------------------------------------------
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


class Client:
    def __init__(self, access: str, secret: str):
        self.access = access
        self.sk = secret.encode("utf-8")

    def call(self, method: str, path: str, query: str = "",
             payload: dict | None = None, raw: bool = False):
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = _sign(method, self.sk, self.access, path, query,
                        "application/json")
        if raw:
            headers["Accept"] = "*/*"
        url = BASE + path + (("?" + query) if query else "")
        req = urllib.request.Request(url, method=method, data=body,
                                     headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def json_call(self, method: str, path: str, query: str = "",
                  payload: dict | None = None, expect=(200, 201)):
        code, body = self.call(method, path, query, payload)
        if code not in expect:
            raise SystemExit(
                f"{method} {path} -> HTTP {code}: "
                f"{body[:400].decode(errors='replace')}"
            )
        return json.loads(body) if body else {}


# --------------------------------------------------------------------------
# Document / element plumbing
# --------------------------------------------------------------------------
def _resolve_owner(c: Client) -> tuple[str | None, int]:
    if OWNER_ID:
        return OWNER_ID, OWNER_TYPE
    if not OWNER_NAME:
        return None, 0
    code, body = c.call("GET", "/api/v6/companies")
    if code == 200:
        for item in json.loads(body).get("items", []):
            if item.get("name") == OWNER_NAME:
                return item["id"], 1
    code, body = c.call("GET", "/api/v6/teams")
    if code == 200:
        for item in json.loads(body).get("items", []):
            if item.get("name") == OWNER_NAME:
                return item["id"], 2
    print(f"  [owner] no company/team named {OWNER_NAME!r}; "
          "falling back to user-owned")
    return None, 0


def resolve_doc(c: Client) -> tuple[str, str, bool]:
    """Return (did, wid, created) for TARGET_DOC_NAME, creating it if absent."""
    owner_id, owner_type = _resolve_owner(c)

    def _scan(filter_id: int, extra: str = "") -> str | None:
        offset = 0
        while True:
            q = (f"filter={filter_id}&limit=20&offset={offset}"
                 f"&sortColumn=modifiedAt&sortOrder=desc{extra}")
            code, body = c.call("GET", "/api/v6/documents", q)
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
        info = c.json_call("GET", f"/api/v6/documents/{did}")
        return did, info["defaultWorkspace"]["id"], False

    payload: dict = {
        "name": TARGET_DOC_NAME,
        "description": (
            "T3-prism tensegrity as a NATIVE Onshape feature tree, generated by "
            "cad/t3-prism/onshape_featurescript_t3prism.py from "
            "cad/t3-prism/t3-prism.fs (issue #95). Edit the T3 Prism feature's "
            "parameters and regenerate -- do not hand-edit the geometry, the "
            "SCAD/FS source is the source of truth."
        ),
        "isPublic": IS_PUBLIC,
    }
    if owner_id:
        payload["ownerId"] = owner_id
        payload["ownerType"] = owner_type
    j = c.json_call("POST", "/api/v6/documents", payload=payload)
    return j["id"], j["defaultWorkspace"]["id"], True


def find_element(c: Client, did: str, wid: str, name: str,
                 element_type: str) -> str | None:
    els = c.json_call("GET", f"/api/v6/documents/d/{did}/w/{wid}/elements")
    for el in els:
        if el.get("name") == name and el.get("elementType") == element_type:
            return el["id"]
    return None


# --------------------------------------------------------------------------
# Feature Studio: push t3-prism.fs
# --------------------------------------------------------------------------
def sync_feature_studio(c: Client, did: str, wid: str) -> tuple[str, str]:
    """Create/update the Feature Studio holding t3-prism.fs.

    Returns (element id, FeatureScript std version actually used).
    """
    eid = find_element(c, did, wid, FS_ELEMENT_NAME, "FEATURESTUDIO")
    if eid is None:
        j = c.json_call("POST", f"/api/v6/featurestudios/d/{did}/w/{wid}",
                        payload={"name": FS_ELEMENT_NAME})
        eid = j["id"]
        print(f"  [fs] created Feature Studio {FS_ELEMENT_NAME!r}")
    else:
        print(f"  [fs] reusing Feature Studio {FS_ELEMENT_NAME!r}")

    # Onshape stamps every new Feature Studio with the server's current
    # FeatureScript version. Adopt it rather than pinning whatever number was
    # current when t3-prism.fs was committed -- otherwise the std import 404s
    # on older/newer servers.
    current = c.json_call(
        "GET", f"/api/v6/featurestudios/d/{did}/w/{wid}/e/{eid}")
    stub = current.get("contents", "") or ""
    m = re.search(r"FeatureScript\s+(\d+)\s*;", stub)
    std_version = m.group(1) if m else None

    source = FS_SOURCE.read_text(encoding="utf-8")
    if std_version:
        source = re.sub(r"FeatureScript\s+\d+\s*;",
                        f"FeatureScript {std_version};", source, count=1)
        source = re.sub(r'version\s*:\s*"\d+\.\d+"',
                        f'version : "{std_version}.0"', source)

    c.json_call("POST", f"/api/v6/featurestudios/d/{did}/w/{wid}/e/{eid}",
                payload={"contents": source})
    print(f"  [fs] pushed {FS_SOURCE.name} "
          f"({len(source)} chars, std version {std_version or 'as-committed'})")
    return eid, std_version or ""


def check_feature_spec(c: Client, did: str, wid: str, eid: str) -> bool:
    """Compile the Feature Studio server-side and surface any errors."""
    code, body = c.call(
        "GET", f"/api/v6/featurestudios/d/{did}/w/{wid}/e/{eid}/featurespecs")
    text = body.decode(errors="replace")
    if code != 200:
        print(f"  [fs] featurespecs HTTP {code}: {text[:800]}")
        return False
    j = json.loads(body)
    specs = j.get("featureSpecs") or []
    if not specs:
        print(f"  [fs] NO feature specs returned -- the studio did not compile:"
              f"\n{text[:1500]}")
        return False
    for spec in specs:
        print(f"  [fs] compiled feature: {spec.get('featureTypeName')} "
              f"({spec.get('featureType')})")
    return True


# --------------------------------------------------------------------------
# Part Studio: insert the custom feature
# --------------------------------------------------------------------------
def create_version(c: Client, did: str, wid: str, name: str) -> str:
    j = c.json_call("POST", f"/api/v6/documents/d/{did}/versions",
                    payload={"documentId": did, "workspaceId": wid,
                             "name": name})
    return j["id"]


def element_microversion(c: Client, did: str, vid: str, eid: str) -> str:
    els = c.json_call("GET", f"/api/v6/documents/d/{did}/v/{vid}/elements")
    for el in els:
        if el.get("id") == eid:
            mv = el.get("microversionId")
            if not mv:
                raise SystemExit("element has no microversionId")
            return mv
    raise SystemExit(f"element {eid} not present in version {vid}")


def _param_payload(key: str, value: str) -> dict:
    """Turn NAME=VALUE into the right BTMParameter* payload."""
    if key in BOOLEAN_PARAMS:
        return {"btType": BT_BOOLEAN, "parameterId": key,
                "value": _truthy(value)}
    if key in ENUM_PARAMS:
        return {"btType": BT_ENUM, "parameterId": key, "value": value.upper(),
                "enumName": ENUM_PARAMS[key], "namespace": ""}
    return {"btType": BT_QUANTITY, "parameterId": key, "expression": value}


def drop_existing_features(c: Client, did: str, wid: str, ps_eid: str) -> int:
    """Remove any previous T3-prism feature so re-runs stay idempotent.

    Without this, each run stacks another copy of the prism into the same tree
    (and a stale copy pointing at an older version keeps its old geometry).
    """
    j = c.json_call("GET",
                    f"/api/v6/partstudios/d/{did}/w/{wid}/e/{ps_eid}/features")
    dropped = 0
    for feat in j.get("features", []):
        msg = feat.get("message", feat)
        if msg.get("featureType") == FEATURE_TYPE:
            fid = msg.get("featureId")
            c.call("DELETE",
                   f"/api/v6/partstudios/d/{did}/w/{wid}/e/{ps_eid}"
                   f"/features/featureid/{fid}")
            dropped += 1
    return dropped


def add_custom_feature(c: Client, did: str, wid: str, ps_eid: str,
                       namespace: str, params: dict) -> dict:
    feature = {
        "feature": {
            "btType": BT_FEATURE,
            "featureType": FEATURE_TYPE,
            "featureId": "",
            "name": FEATURE_NAME,
            "namespace": namespace,
            "suppressed": False,
            "parameters": [_param_payload(k, v) for k, v in params.items()],
        }
    }
    code, body = c.call(
        "POST", f"/api/v6/partstudios/d/{did}/w/{wid}/e/{ps_eid}/features",
        payload=feature)
    text = body.decode(errors="replace")
    if code not in (200, 201):
        raise SystemExit(f"add feature HTTP {code}: {text[:1200]}")
    return json.loads(body)


def feature_status(result: dict) -> tuple[str, list[str]]:
    state = (result.get("featureState") or {}).get("message") or \
        result.get("featureState") or {}
    status = state.get("featureStatus", "UNKNOWN")
    msgs = []
    for entry in state.get("featureMessages") or []:
        m = entry.get("message") or entry
        msgs.append(f"{m.get('messageType', '?')}: {m.get('message', '')}")
    return status, msgs


def bbox_mm(c: Client, did: str, wid: str, eid: str) -> str | None:
    """Read the Part Studio bounding box and format it in millimetres.

    NOTE the unit difference from ``onshape_upload_t3prism.py``: for a
    *natively modelled* Part Studio this endpoint reports SI **metres**, so the
    numbers need a x1000. That script's comment ("reports millimetres already")
    is right for its own case -- an imported mesh element -- and wrong here.
    Verified against the exported STEP: 0.0812 m == 81.19 mm, which matches
    the SCAD STL's 81.19 mm to two decimals.
    """
    code, body = c.call(
        "GET", f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/boundingboxes")
    if code != 200:
        return None
    j = json.loads(body)
    try:
        dims = [(j["highX"] - j["lowX"]) * 1000.0,
                (j["highY"] - j["lowY"]) * 1000.0,
                (j["highZ"] - j["lowZ"]) * 1000.0]
    except KeyError:
        return None
    return f"{dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm (X x Y x Z)"


# --------------------------------------------------------------------------
# STEP export straight out of the live Part Studio
# --------------------------------------------------------------------------
def export_step(c: Client, did: str, wid: str, eid: str,
                out: pathlib.Path) -> bool:
    j = c.json_call(
        "POST", f"/api/v6/partstudios/d/{did}/w/{wid}/e/{eid}/translations",
        payload={
            "formatName": "STEP",
            "storeInDocument": False,
            "flattenAssemblies": False,
            "versionString": "",
        })
    tid = j.get("id") or j.get("translationId")
    if not tid:
        print(f"  [step] no translation id in response: {j}")
        return False
    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(5)
        code, body = c.call("GET", f"/api/v6/translations/{tid}")
        if code != 200:
            continue
        t = json.loads(body)
        state = t.get("requestState")
        if state == "FAILED":
            print(f"  [step] translation FAILED: {t.get('failureReason')}")
            return False
        if state == "DONE":
            fids = t.get("resultExternalDataIds") or []
            if not fids:
                print("  [step] translation DONE but no external data id")
                return False
            code, blob = c.call(
                "GET", f"/api/v6/documents/d/{did}/externaldata/{fids[0]}",
                raw=True)
            if code != 200:
                print(f"  [step] download HTTP {code}")
                return False
            out.write_bytes(blob)
            print(f"  [step] wrote {out} ({len(blob)} bytes)")
            return True
    print("  [step] translation poll timed out")
    return False


# --------------------------------------------------------------------------
def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc-name", default=None,
                    help=f"Onshape document name (default: {TARGET_DOC_NAME!r})")
    ap.add_argument("--param", action="append", default=[], metavar="NAME=VALUE",
                    help="custom-feature parameter, repeatable. Lengths/angles "
                         "take an expression ('7.1 mm'); booleans take "
                         "true/false; 'part' takes BOTH/STRUTS/CABLES.")
    ap.add_argument("--export-step", default=None, metavar="PATH",
                    help="also export the regenerated Part Studio to STEP")
    ap.add_argument("--version-name", default=None,
                    help="name for the version cut before inserting the feature")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate t3-prism.fs and the parameter payloads "
                         "locally, without touching Onshape")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    global TARGET_DOC_NAME
    args = _parse_args(argv)
    if args.doc_name:
        TARGET_DOC_NAME = args.doc_name

    if not FS_SOURCE.exists():
        print(f"missing FeatureScript source at {FS_SOURCE}")
        return 1

    params: dict[str, str] = {}
    for spec in args.param:
        if "=" not in spec:
            print(f"--param expects NAME=VALUE, got {spec!r}")
            return 2
        k, _, v = spec.partition("=")
        params[k.strip()] = v.strip()

    if args.dry_run:
        src = FS_SOURCE.read_text(encoding="utf-8")
        print(f"{FS_SOURCE.name}: {len(src)} chars, "
              f"{len(src.splitlines())} lines")
        exported = re.findall(r"export const (\w+)\s*=\s*defineFeature", src)
        print(f"exported features: {exported}")
        if FEATURE_TYPE not in exported:
            print(f"ERROR: featureType {FEATURE_TYPE!r} not exported by the "
                  f"studio")
            return 1
        declared = set(re.findall(r"definition\.(\w+)", src))
        unknown = sorted(set(params) - declared)
        if unknown:
            print(f"ERROR: unknown parameter(s) {unknown}; "
                  f"known: {sorted(declared)}")
            return 1
        for k, v in params.items():
            print(f"  param {k} -> {json.dumps(_param_payload(k, v))}")
        print("dry-run OK")
        return 0

    access = os.environ.get("ONSHAPE_ACCESS_KEY")
    secret = os.environ.get("ONSHAPE_SECRET_KEY")
    if not access or not secret:
        print("ONSHAPE_ACCESS_KEY/SECRET_KEY not set; aborting.")
        return 1
    c = Client(access, secret)
    print(f"BASE = {BASE}")

    did, wid, created = resolve_doc(c)
    print(f"target document ({'created' if created else 'found'}): "
          f"{TARGET_DOC_NAME!r}")
    doc_url = f"{BASE}/documents/{did}/w/{wid}"
    print(f"document URL: {doc_url}")

    print("\n== 1. Feature Studio ==")
    fs_eid, std_version = sync_feature_studio(c, did, wid)
    print(f"  [fs] {doc_url}/e/{fs_eid}")

    print("\n== 2. compile check ==")
    if not check_feature_spec(c, did, wid, fs_eid):
        return 1

    print("\n== 3. version ==")
    vname = args.version_name or f"t3-prism fs {int(time.time())}"
    vid = create_version(c, did, wid, vname)
    mvid = element_microversion(c, did, vid, fs_eid)
    namespace = f"d{did}::v{vid}::e{fs_eid}::m{mvid}"
    print(f"  [version] {vname!r}")

    print("\n== 4. Part Studio + feature ==")
    ps_eid = find_element(c, did, wid, PS_ELEMENT_NAME, "PARTSTUDIO")
    if ps_eid is None:
        ps_eid = c.json_call("POST", f"/api/v6/partstudios/d/{did}/w/{wid}",
                             payload={"name": PS_ELEMENT_NAME})["id"]
        print(f"  [ps] created Part Studio {PS_ELEMENT_NAME!r}")
    else:
        print(f"  [ps] reusing Part Studio {PS_ELEMENT_NAME!r}")
        dropped = drop_existing_features(c, did, wid, ps_eid)
        if dropped:
            print(f"  [ps] removed {dropped} stale T3-prism feature(s)")

    result = add_custom_feature(c, did, wid, ps_eid, namespace, params)
    status, msgs = feature_status(result)
    print(f"  [ps] feature status: {status}")
    for m in msgs:
        print(f"       {m}")
    if params:
        print(f"  [ps] parameters supplied: "
              f"{', '.join(f'{k}={v}' for k, v in params.items())}")
    print(f"  [ps] {doc_url}/e/{ps_eid}")

    bbox = bbox_mm(c, did, wid, ps_eid)
    print(f"  [ps] bounding box: {bbox or '(unavailable)'}")

    ok = status == "OK"
    if args.export_step:
        print("\n== 5. STEP export from the live feature tree ==")
        ok = export_step(c, did, wid, ps_eid,
                         pathlib.Path(args.export_step)) and ok

    print("\n== Clickable Onshape URLs ==")
    print(f"Document:      {doc_url}")
    print(f"Feature Studio:{doc_url}/e/{fs_eid}")
    print(f"Part Studio:   {doc_url}/e/{ps_eid}   [{bbox or 'bbox unavailable'}]")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
