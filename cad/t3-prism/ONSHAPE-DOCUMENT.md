# Onshape document — T3-prism parametric feature tree

The live Onshape document produced by
[`onshape_featurescript_t3prism.py`](onshape_featurescript_t3prism.py) from
[`t3-prism.fs`](t3-prism.fs) (issue #95, route C).

**Open the feature tree here:**
<https://cad.onshape.com/documents/31e08e4df8d1d1a5073123e5/w/ac16a0ddb76685f7abad2605/e/1c2d672517c4435ac9d5b4c5>

| | |
|---|---|
| Document | `Tensegrity T3-prism (parametric)` |
| Owner | Vertical Cloud Lab (company-owned) |
| Visibility | public — link works without an Onshape login |
| Document id (`did`) | `31e08e4df8d1d1a5073123e5` |
| Default workspace (`wid`) | `ac16a0ddb76685f7abad2605` |
| Part Studio (`eid`) — **the feature tree** | `1c2d672517c4435ac9d5b4c5` — tab `T3-prism (parametric)` |
| Feature Studio (`eid`) — the FeatureScript source | `dcc22ff9844eb4ab6992422f` — tab `T3Prism` |

Direct links:

- Document root — <https://cad.onshape.com/documents/31e08e4df8d1d1a5073123e5>
- Feature Studio (`T3Prism`) —
  <https://cad.onshape.com/documents/31e08e4df8d1d1a5073123e5/w/ac16a0ddb76685f7abad2605/e/dcc22ff9844eb4ab6992422f>

## What's in the Part Studio

One editable custom feature, `T3 Prism (tensegrity)` (`featureType: t3Prism`),
which builds four parts:

| part | material |
|---|---|
| `t3-prism-struts (PLA)` ×3 | PLA |
| `t3-prism-cables (TPU)` | TPU |

Double-click the feature, change a parameter, Regenerate. Rollback and history
work as they do for any native feature.

The `Part Studio 1`, `Assembly 1` and `BOM : Assembly 1` tabs are the empty
defaults Onshape creates with a new document — ignore them.

## Regenerating

Re-running the driver deletes the previous Part Studio and Feature Studio and
recreates them, so **the element ids above change on every run** and this file
needs updating with the ids the script prints. The document id and workspace id
are stable — the script looks the document up by name and only creates it if
absent.

```bash
export ONSHAPE_ACCESS_KEY=... ONSHAPE_SECRET_KEY=...
python cad/t3-prism/onshape_featurescript_t3prism.py
```

Custom features can only be referenced from a *version*, never a workspace, so
each run also cuts a version named `t3-prism fs <epoch>`. Those accumulate;
they are harmless.

## Source of truth

The FeatureScript in `t3-prism.fs` is the source of truth for this document.
Hand-edits made in Onshape are overwritten by the next run of the driver — see
[`README-parametric.md`](README-parametric.md).
