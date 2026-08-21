#!/usr/bin/env python3
"""Fetch every file of a public Box shared folder (no login).

Usage:
    python scripts/fetch_box_shared_folder.py SHARED_NAME DEST_DIR [--host byu.box.com]

SHARED_NAME is the trailing token of a share URL like
https://byu.box.com/s/<SHARED_NAME>.  The script resolves the share to its
folder id, walks the embedded page listing (20 items/page), recurses into
subfolders, downloads all files with a small thread pool, verifies sizes,
and writes a ``box-ids.json`` manifest (shared_name, folder name, file ->
id map) next to the downloaded files — the repo convention for keeping
raw data on Box while committing its provenance.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.cookiejar import CookieJar
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def make_opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    return op


def get(opener, url, tries=4):
    for k in range(tries):
        try:
            with opener.open(url, timeout=120) as r:
                return r.read()
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


def page_data(opener, url):
    html = get(opener, url).decode("utf-8", "replace")
    i = html.find("Box.postStreamData = ")
    if i < 0:
        raise RuntimeError(f"no postStreamData at {url}")
    data, _ = json.JSONDecoder().raw_decode(html[i + len("Box.postStreamData = "):])
    return data


def list_folder(opener, app_host, shared_name, folder_id):
    items, page, pages = [], 1, 1
    while page <= pages:
        d = page_data(opener, f"https://{app_host}/s/{shared_name}/folder/{folder_id}?page={page}")
        sf = d["/app-api/enduserapp/shared-folder"]
        pages = int(sf.get("pageCount") or 1)
        items.extend(sf["items"])
        name = sf.get("currentFolderName")
        page += 1
    return name, items


def walk(opener, app_host, shared_name, folder_id, rel=""):
    name, items = list_folder(opener, app_host, shared_name, folder_id)
    out = []
    for it in items:
        if it["type"] == "file":
            out.append({"rel": f"{rel}{it['name']}", "id": it["id"],
                        "size": it.get("itemSize")})
        elif it["type"] == "folder":
            out.extend(walk(opener, app_host, shared_name, it["id"],
                            rel=f"{rel}{it['name']}/")[1])
    return name, out


def fetch_one(app_host, shared_name, f, dest: Path):
    p = dest / f["rel"]
    if p.exists() and f.get("size") and p.stat().st_size == f["size"]:
        return f["rel"], "cached"
    p.parent.mkdir(parents=True, exist_ok=True)
    op = make_opener()
    url = (f"https://{app_host}/index.php?rm=box_download_shared_file"
           f"&shared_name={shared_name}&file_id=f_{f['id']}")
    data = get(op, url)
    if f.get("size") and len(data) != f["size"]:
        raise RuntimeError(f"size mismatch for {f['rel']}: {len(data)} != {f['size']}")
    p.write_bytes(data)
    return f["rel"], f"{len(data)} B"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shared_name")
    ap.add_argument("dest", type=Path)
    ap.add_argument("--host", default="byu.box.com")
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    app_host = args.host.replace(".box.com", ".app.box.com")
    opener = make_opener()
    d = page_data(opener, f"https://{args.host}/s/{args.shared_name}")
    item = d["/app-api/enduserapp/shared-item"]
    if item["itemType"] != "folder":
        sys.exit("share is not a folder")
    fname, files = walk(opener, app_host, args.shared_name, item["itemID"])
    print(f"{args.shared_name}: folder '{fname}', {len(files)} files, "
          f"{sum(f.get('size') or 0 for f in files)/1e6:.0f} MB")

    args.dest.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.jobs) as ex:
        futs = [ex.submit(fetch_one, app_host, args.shared_name, f, args.dest)
                for f in files]
        for n, fut in enumerate(as_completed(futs), 1):
            rel, note = fut.result()
            if n % 20 == 0 or n == len(futs):
                print(f"  {n}/{len(futs)}  {rel} ({note})", flush=True)

    manifest = {"shared_name": args.shared_name, "folder": fname,
                "files": {f["rel"]: f"f_{f['id']}" for f in sorted(files, key=lambda x: x["rel"])}}
    (args.dest / "box-ids.json").write_text(json.dumps(manifest, indent=1))
    print(f"manifest -> {args.dest / 'box-ids.json'}")


if __name__ == "__main__":
    main()
