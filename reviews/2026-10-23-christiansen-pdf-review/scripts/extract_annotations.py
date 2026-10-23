import sys, json
import pymupdf
pdf = sys.argv[1]
doc = pymupdf.open(pdf)
print("pages:", doc.page_count, "metadata:", {k: v for k, v in doc.metadata.items() if v})
out = []
for pno in range(doc.page_count):
    page = doc[pno]
    for a in page.annots() or []:
        info = a.info
        rec = {
            "page": pno + 1,
            "type": a.type[1],
            "xref": a.xref,
            "rect": [round(v, 1) for v in a.rect],
            "author": info.get("title"),
            "subject": info.get("subject"),
            "content": info.get("content"),
            "created": info.get("creationDate"),
            "modified": info.get("modDate"),
            "irt": a.irt_xref,
            "popup": a.popup_xref,
        }
        # highlighted text via quadpoints
        verts = a.vertices
        if verts and a.type[1] in ("Highlight", "Underline", "StrikeOut", "Squiggly"):
            words = []
            quads = [verts[i:i+4] for i in range(0, len(verts), 4)]
            texts = []
            for q in quads:
                r = pymupdf.Quad(q).rect
                # shrink slightly to avoid picking neighbours
                r2 = pymupdf.Rect(r.x0 + 0.5, r.y0 + r.height * 0.2, r.x1 - 0.5, r.y1 - r.height * 0.2)
                texts.append(page.get_textbox(r2).strip())
            rec["highlighted"] = " | ".join(texts)
        out.append(rec)
json.dump(out, open(sys.argv[2], "w"), indent=1)
from collections import Counter
print(Counter(r["type"] for r in out))
print(Counter(r["author"] for r in out))
for r in out:
    if r["type"] == "Popup":
        continue
    print("---", r["page"], r["type"], r["xref"], "irt=", r["irt"], r["created"])
    if r.get("highlighted"):
        print("  HL:", r["highlighted"][:400])
    if r["content"]:
        print("  C :", r["content"][:1500])
