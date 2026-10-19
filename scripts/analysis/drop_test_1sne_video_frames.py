#!/usr/bin/env python3
"""1sne21..1sne83 slo-mo clips: clip <-> drop pairing + identity montage (PR #86, 10-19).

The batch's 27 clips (Sony RX100 IV HFR, ``captureFps="959.04p"``, 2052
frames = 2.14 s each, one short clip) follow the film-drops-1/10/20 SOP
and are named ``1sne<id>-{1,10,20}.MP4``.  As in the dran3 batch they are
portrait recordings stored unrotated (rotate 90 deg clockwise to view) and
the camera clock is reset (it reads 2018-01-20).

Pairing: the creation time in each MP4's ``mvhd`` header (camera clock)
is matched to the TP4 series tables committed under
``data/drop-tests/1sne-checkin/raw/<id>/`` (local DAQ time).  The camera
runs a constant offset behind the DAQ, estimated here as the median
clip-to-nearest-event difference; each clip is then assigned to the
nearest event of any session, with its residual.  The XML sidecars carry
the same creation times and the frame counts.

Identity: the operator tapes the session label on the carriage, so a
rest frame (frame 1500, after the carriage has settled) shows which
article was on the tower, independently of file names and clocks.  The
montage is one column per session, one row per clip (-1, -10, -20).

Usage:
    python scripts/analysis/drop_test_1sne_video_frames.py --mp4 DIR
where DIR holds the 27 MP4s and the 27 ``C00xxM01.XML`` sidecars (Box ids
in ``data/drop-tests/1sne-checkin/video/box-ids.json``).
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drop_test_60in_5felts_analysis import DATA  # noqa: E402

OUT = DATA / "1sne-checkin"
REST_FRAME = 1500
CROP = (660, 1640, 200, 1000)        # y0, y1, x0, x1 on the upright 1080x1920 frame
TILE = (260, 318)
MAX_RESIDUAL_S = 2.0                 # a clip further than this from any event has no capture


def mvhd_creation(path: Path) -> datetime:
    """Creation time from the MP4 movie header (camera clock)."""
    with open(path, "rb") as f:
        f.seek(0, 2)
        end, pos = f.tell(), 0
        while pos < end - 8:
            f.seek(pos)
            size, typ = struct.unpack(">I4s", f.read(8))
            hs = 8
            if size == 1:
                size, hs = struct.unpack(">Q", f.read(8))[0], 16
            if typ == b"moov":
                sub = pos + hs
                while sub < pos + size - 8:
                    f.seek(sub)
                    s2, t2 = struct.unpack(">I4s", f.read(8))
                    if t2 == b"mvhd":
                        version = f.read(4)[0]
                        ct = (struct.unpack(">Q", f.read(8))[0] if version == 1
                              else struct.unpack(">I", f.read(4))[0])
                        return datetime(1904, 1, 1) + timedelta(seconds=ct)
                    sub += s2
            pos += size
    raise ValueError(f"no mvhd in {path}")


def sidecars(mp4_dir: Path) -> list[dict]:
    out = []
    for x in sorted(mp4_dir.glob("*.XML")):
        txt = x.read_text(encoding="utf-8", errors="replace")
        cd = re.search(r'CreationDate value="([^"]+)"', txt).group(1)
        out.append({"xml": x.name, "creation": datetime.fromisoformat(cd),
                    "frames": int(re.search(r'Duration value="(\d+)"', txt).group(1)),
                    "capture_fps": re.search(r'captureFps="([^"]+)"', txt).group(1)})
    return out


def events() -> list[dict]:
    ev = []
    for tab in sorted((OUT / "raw").glob("*/*.csv")):
        sess = tab.parent.name
        for line in tab.read_text(encoding="latin-1").splitlines()[6:]:
            c = [v.strip() for v in line.split(",")]
            if len(c) > 15 and c[1].isdigit():
                ev.append({"session": sess, "event": int(c[1]),
                           "time": datetime.strptime(c[2], "%m/%d/%Y %I:%M:%S %p")})
    return sorted(ev, key=lambda e: e["time"])


def rest_tile(path: Path, label_top: str, label_bot: str) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, min(REST_FRAME, n - 5))
    ok, fr = cap.read()
    up = cv2.rotate(fr, cv2.ROTATE_90_CLOCKWISE)
    y0, y1, x0, x1 = CROP
    img = cv2.resize(cv2.convertScaleAbs(up[y0:y1, x0:x1], alpha=1.7, beta=10), TILE)
    cv2.putText(img, label_top, (5, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
    cv2.putText(img, label_bot, (5, TILE[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42,
                (0, 255, 255), 1)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp4", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT / "figures")
    args = ap.parse_args()

    cens = {(r["session"], r["signal"]): r["class"] for r in
            json.loads((args.out / "capture_census.json").read_text())}
    side = sidecars(args.mp4)
    ev = events()
    clips = []
    for p in sorted(args.mp4.glob("*.MP4")):
        t = mvhd_creation(p)                                  # UTC, camera clock
        xml = min(side, key=lambda s: abs((s["creation"].astimezone(timezone.utc)
                                           .replace(tzinfo=None) - t).total_seconds()))
        clips.append({"clip": p.name, "camera_time": xml["creation"].replace(tzinfo=None),
                      "xml": xml["xml"], "frames": xml["frames"],
                      "capture_fps": xml["capture_fps"]})

    # constant camera -> DAQ offset: the candidate (any event minus any clip)
    # that puts the most clips within MAX_RESIDUAL_S of an event, refined by
    # the median residual of those clips
    et = np.array([e["time"].timestamp() for e in ev])
    ct = np.array([c["camera_time"].timestamp() for c in clips])
    cands = (et[:, None] - ct[None, :]).ravel()
    hits = [(np.abs(et[None, :] - (ct[:, None] + d)).min(1) <= MAX_RESIDUAL_S).sum()
            for d in cands]
    d0 = cands[int(np.argmax(hits))]
    res = np.abs(et[None, :] - (ct[:, None] + d0)).argmin(1)
    resid = et[res] - (ct + d0)
    d0 += float(np.median(resid[np.abs(resid) <= MAX_RESIDUAL_S]))
    offset = timedelta(seconds=round(float(d0)))

    rows = []
    for c in clips:
        daq = c["camera_time"] + offset
        e = min(ev, key=lambda e: abs((e["time"] - daq).total_seconds()))
        res = (daq - e["time"]).total_seconds()
        name = c["clip"].split("-")[0]
        drop_named = int(c["clip"].split("-")[1].split(".")[0])
        paired = abs(res) <= MAX_RESIDUAL_S
        sess_ev = [x for x in ev if x["session"] == name]
        note = ""
        if not paired:
            last = max(sess_ev, key=lambda x: x["time"]) if sess_ev else None
            gap = (daq - last["time"]).total_seconds() if last else None
            note = (f"no capture: {gap / 60:.1f} min after {name}'s last capture"
                    if gap is not None and gap > 0 else "no capture in the export")
        rows.append({
            "clip": c["clip"], "xml": c["xml"], "frames": c["frames"],
            "capture_fps": c["capture_fps"],
            "camera_time": c["camera_time"].isoformat(), "daq_time": daq.isoformat(),
            "paired_session": e["session"] if paired else None,
            "paired_event": e["event"] if paired else None,
            "residual_s": round(res, 1) if paired else None,
            "matches_name": paired and e["session"] == name and e["event"] == drop_named,
            "capture_class": cens.get((e["session"], e["event"])) if paired else None,
            "note": note})

    sessions = sorted({r["clip"].split("-")[0] for r in rows})
    grid = []
    for k in ("1", "10", "20"):
        tiles = []
        for s in sessions:
            r = next(r for r in rows if r["clip"] == f"{s}-{k}.MP4")
            bot = (f"-> {r['paired_session']} ev {r['paired_event']} ({r['capture_class']})"
                   if r["paired_event"] else "-> no DAQ capture")
            tiles.append(rest_tile(args.mp4 / r["clip"], r["clip"][:-4], bot))
        grid.append(np.hstack(tiles))
    cv2.imwrite(str(args.out / "16_video_identity_montage.jpg"), np.vstack(grid),
                [cv2.IMWRITE_JPEG_QUALITY, 86])

    out = {"camera_to_daq_offset": str(offset), "rest_frame": REST_FRAME,
           "n_clips": len(rows),
           "n_paired_to_named_drop": sum(r["matches_name"] for r in rows),
           "clips": rows}
    (args.out / "video_pairing.json").write_text(json.dumps(out, indent=1))
    print(f"offset {offset}; {out['n_paired_to_named_drop']}/{len(rows)} clips on their "
          f"named drop")
    for r in rows:
        print(f"  {r['clip']:15s} {r['xml']}  daq {r['daq_time'][11:19]}  "
              f"{r['paired_session'] or '-'} ev {r['paired_event'] or '-'} "
              f"res {r['residual_s']}  {r['capture_class'] or ''} {r['note']}")


if __name__ == "__main__":
    main()
