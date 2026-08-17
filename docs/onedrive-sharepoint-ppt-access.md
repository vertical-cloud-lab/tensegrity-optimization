# OneDrive/SharePoint PowerPoint: programmatic access recipe

Working notes for downloading and editing a PowerPoint file shared via a
OneDrive/SharePoint sharing link, from a headless environment such as a CI
runner. Validated against a real password-protected OneDrive for Business
sharing link. No secrets appear below.

Terms used throughout:

- **Sharing link**: `https://<tenant>-my.sharepoint.com/:p:/g/personal/<owner>/<share-token>`
  (password-protected, view+edit)
- **Link password**: injected as an environment variable / workflow secret
  (e.g. `ONEDRIVE_EDIT_LINK_PASSWORD`), never print it
- **Document UniqueId**: the file's GUID in the document library (visible in
  the `Doc.aspx` viewer URL after unlock, or via `/_api/web` once
  authenticated)
- **Site base**: `https://<tenant>-my.sharepoint.com/personal/<owner>`

## Step 1: unlock the link (password required for ALL access)

Anonymous GET of the sharing link returns the `guestaccess.aspx` password page
(a standard ASP.NET form). Submit the password as a postback; on success the
response redirects to `Doc.aspx` (the PowerPoint web viewer) and the cookie
jar gains a guest `FedAuth` cookie that authorizes the REST API. A wrong
password stays on the page with "Link password is incorrect."

```python
import os, re, html, urllib.request, urllib.parse, http.cookiejar

pw = os.environ["ONEDRIVE_EDIT_PASSWORD"]
base = "https://<tenant>-my.sharepoint.com"
share_url = base + "/:p:/g/personal/<owner>/<share-token>"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")]

page = op.open(share_url).read().decode("utf-8", "replace")
action = base + html.unescape(
    re.search(r'action="([^"]*guestaccess\.aspx[^"]*)"', page).group(1))
f = lambda n: (lambda m: html.unescape(m.group(1)) if m else "")(
    re.search(r'name="%s"[^>]*value="([^"]*)"' % n, page))
data = {
    "__EVENTTARGET": "btnSubmitPassword", "__EVENTARGUMENT": "",
    "SideBySideToken": f("SideBySideToken"),
    "__VIEWSTATE": f("__VIEWSTATE"),
    "__VIEWSTATEGENERATOR": f("__VIEWSTATEGENERATOR"),
    "__VIEWSTATEENCRYPTED": "",
    "__EVENTVALIDATION": f("__EVENTVALIDATION"),
    "txtPassword": pw,
}
resp = op.open(urllib.request.Request(
    action, urllib.parse.urlencode(data).encode(), method="POST"))
assert "Doc.aspx" in resp.url  # success → PowerPoint viewer + FedAuth cookie
```

On an edit-enabled link, the unlocked guest session identifies as
**"Guest Contributor"** (`/_api/web/currentuser`) with the `EditListItems`
permission bit set, i.e. the password gates entry, and entry grants edit.

## Step 2: download

With the same opener/cookie jar:

```python
data = op.open(base + "/personal/<owner>/_api/web/"
               "GetFileById(guid'<unique-id>')/$value").read()
```

(`GetFileByUniqueId` does not exist on this endpoint; use
`GetFileById(guid'...')`.)

### Step 2 without the link password: `--deck-dir`

Downloading a deck and authenticating with the sharing-link password are two
different jobs, and four tools here used to ask for the password only because
unlocking the link was the one route to the bytes. A deck pulled through a
signed-in browser is the same stored blob, so `--deck-dir DIR` reads
`DIR/L<N>.pptx` from disk instead:

```bash
python scripts/ppt/audit_live_decks.py  --deck-dir tmp/decks
python scripts/ppt/browser_edit_deck.py plan   --deck-dir tmp/decks --from-spec L18
python scripts/ppt/browser_edit_deck.py verify --deck-dir tmp/decks --all
python scripts/ppt/push_decks.py verify built/ --deck-dir tmp/decks L1 L18
python scripts/ppt/rebuild_deck.py --deck-dir tmp/decks --out handoff/ L18
```

Only the transport moves. Everything downstream parses the same bytes, so the
diffs, the byte-size media checks and the slide-count comparisons are unchanged.
Two limits are real and are enforced rather than left to the reader:

- **`browser_edit_deck.py apply` refuses it.** The edits go through the live web
  editor, and a directory is a copy of the stored blob, not the file.
- **`rebuild_deck.py --deck-dir` requires `--out` or `--dry-run`.** With no REST
  session there is no `TimeLastModified` to re-read, so the freshness guard that
  is the point of that script has nothing to compare against.

**A directory is only as current as the moment it was filled.** The
verify-by-re-download discipline below is unchanged: re-pull after an edit, or
you are verifying against a stale copy and it will say everything is fine.

## Write path A, headless-browser co-authoring: the only permitted way to edit a deck

Per CLAUDE.md, this is the sole sanctioned write path. It works even while the
owner has the file open, and it merges rather than replaces. Path B below is
recorded for diagnosis and history only; do not use it.

If the environment has system Chrome, `pip install playwright` and launch with
`channel="chrome"` (no browser download needed). Load the sharing link. The
password page renders first, so fill `#txtPassword` and click
`#btnSubmitPassword`, then wait ~40 s for the Office WOPI editor
(`powerpoint.officeapps.live.com` iframe) to boot; it opens directly in
**Editing** mode. Typed changes autosave through co-authoring and merge with any
live human session; the stored blob reflects them within ~1-2 min of closing the
browser.

**Use `scripts/ppt/browser_edit_deck.py` rather than driving this by hand.** It
plans offline (read-only), applies, and verifies against the re-downloaded blob.
`scripts/ppt/web_editor.py` is the mechanics layer underneath it.

### Driving the editor: what actually works

Most of this was established by probing the live editor. Each entry is here
because the obvious alternative fails, and most of them fail *quietly*.

**Not yet probed, as of 2026-08-15**: the text-box, click-shield and
Change Slide Layout entries below, and the browser half of the stored-file
reorder check. They are implemented in `web_editor.py` from the DOM behaviour
recorded here and each raises rather than reporting a success it did not
observe, but no run has driven them against a live deck. Treat them as
unverified until one has, and say so rather than repeating them as fact: a
previous session recorded two of these as verified in the stored `.pptx` when
the code did not exist anywhere.

- **Load the edit link, not the public view link.** `onedrive-ppt-links.md`
  holds both, and `onedrive_ppt.load_links` returns whichever is last in the
  file. The anonymous view link opens read-only and every edit is silently
  discarded. `web_editor.edit_links()` parses the section headings instead.
- **The editor frame** is the one whose URL contains `officeapps.live.com`
  (named `WacFrame_PowerPoint_0`). Its `src` attribute is not reliable for
  finding it; match on `frame.url`.
- **Ready** means `#StatusBar` reads `Slide N of M`. That string is also the
  only honest confirmation that a navigation landed.
- **Navigate** by clicking the nth `[id^="grid-content-view-id"]` thumbnail.
  Each carries an `aria-label` with the slide's title plus `Has notes` and
  `Is hidden`, which is a cheap way to spot graveyard slides.
- **Address a shape by where it is drawn.** The slide is letterboxed inside
  `#WACViewPanel`, so fit it by aspect ratio and map the EMU box `python-pptx`
  reports for the same file. Click via `locator.click(position=...)`, which adds
  the iframe offset for you. A click both selects the shape and gives the canvas
  keyboard focus; confirm by checking `document.activeElement.id` contains
  `WACViewPanel_EditingElement`.
- **Replace text**: double-click the shape, `Ctrl+A`, then `keyboard.type()`.
- **Clear the click shields first.** `#WACDialogOverlay` is invisible, lets
  every `evaluate()` through, and swallows clicks for the whole of Playwright's
  25 second retry, so the symptom is a timeout on an element that is plainly
  there. **The id is in the DOM more than once**, so
  `document.querySelector('#WACDialogOverlay')` answers about a dead leftover
  and reports clear while a live sibling covers the page. Use
  `querySelectorAll` and filter on layout and `pointer-events`, never on
  anything visible: `web_editor.live_overlays()` and `dismiss_overlays()`.
- **Add a text box**: `Insert > Text Box` (`#InsertTextBox`) **creates
  nothing**. It arms a draw mode, and the box is whatever the next drag on the
  canvas encloses. Three ways that goes wrong silently, all handled in
  `web_editor.insert_text_box`:
  - A single `mouse.move` between `down` and `up` reads as a click, which
    disarms the mode and leaves the slide untouched. Move in several steps, as
    for a thumbnail drag.
  - **Do not Escape out and come back through `replace_text`.** A text box with
    no text has no hit area, so the double-click falls through to whatever is
    behind it. Type into the state the drag leaves behind, where focus is
    already `WACViewPanel_EditingElement`.
  - **PowerPoint discards an empty text box on save.** A typing failure
    therefore leaves no evidence at all rather than a visibly empty box, so the
    function confirms the typed characters are on the canvas before it returns.
- **Delete a text box**: click it, **`Escape`**, then `Delete`. The Escape is
  load-bearing. A click puts a caret inside the text rather than selecting the
  shape, so without it `Delete` removes one character and leaves the shape
  behind (observed: `TYPED LINE` became `TYPED INE`).
- **Delete a picture or a video: no Escape.** The click already selects the
  object, and the same Escape *drops* the selection, so `Delete` does nothing
  at all. Ask the ribbon which case you are in rather than hard-coding either:
  a `Picture` / `Video` / `Audio` contextual tab means the object itself is
  selected. A `Shape` tab does not, since a text box raises one while the caret
  is still inside its text. Both halves of this were learned the expensive way
  in one session, one per direction.
- **Speaker notes**: `#ShowHideNotes` toggles the pane; open/closed is
  `#EditingNotesPanel`'s height (>50 px). Do not test
  `#EditingNotesPanel_EditingElement`, which is a 0x0 accessibility proxy in both
  states, so it reads "closed" forever and the toggle closes an open pane.
  Neither it nor `#NotesContentContainer` accepts a direct click; click a point
  inside `#EditingNotesPanel`. Check focus before typing, because a miss puts
  `Ctrl+A` on the slide and overwrites slide content.
- **The save indicator** `#SaveStatusButton` has empty `innerText`; the state is
  in its `aria-label`.

Approaches that seem right and are not, recorded so they are not retried:

| Attempt | What happens |
|---|---|
| `keyboard.insert_text()` | Types nothing. `Ctrl+A` visibly selects, the replacement does not happen, so it fails looking like it worked. Office uses a composition model that ignores synthetic `input` events. |
| Esc then Tab to cycle placeholders | Focus lands in an internal `ClipboardTarget` iframe and stays there. Nothing is selected. |
| Select via the Selection Pane, then act | Handles appear on the canvas, but focus stays on the pane and Delete or typing goes nowhere. Forcing focus back with JS keeps the handles and still does nothing. |
| Click a text box, press Delete | Deletes a character, not the shape. See above. |
| Click a picture or video, press Escape, then Delete | Nothing happens. The click had already selected the object and the Escape dropped it. The mirror image of the row above, and the reason selection is decided from the ribbon rather than assumed. |
| `querySelector('#WACDialogOverlay')` to check the page is clickable | Reports clear while a live overlay covers the page. The id is in the DOM more than once and the first match is usually a dead leftover. Check all of them. |
| Click Insert > Text Box, then type | Types into the slide, not into a text box. The menu item arms a draw mode; the box only exists once a multi-step drag has enclosed it. |

The Selection Pane (Ctrl+F10, or Arrange > Selection Pane) is still worth
having: it lists every shape on the slide **by name**, and those names are the
same strings `python-pptx` reports. That is what lets a plan be built offline
and executed here. Use it to read and to confirm, never to select.

## Write path B, REST upload: BANNED. Documented so it is recognized, not used

**Do not write to a deck with the REST API.** This section stays because the
mechanism still explains failures you will see (a 423 while probing metadata,
a deck whose slides changed under you), and because several existing scripts
still contain it. It is not a fallback, not a backup, and not the thing to
reach for when the browser path is slow. See CLAUDE.md for the rule and for
what to do instead when the web editor genuinely cannot make the change.

Three reasons it is banned rather than merely discouraged:

- It is a **whole-file replace**. It cannot merge, so it discards whatever the
  human changed since your download, silently.
- It returns **HTTP 423 `SPFileLockException`** ("locked for shared use")
  whenever anyone has the file open, a co-authoring lock rather than a
  permission failure, lingering ~10 min after they close.
- The `python-pptx` round trip it requires has damaged decks before:
  duplicate zip part names silently ate the last slide of L21 and of L33, and
  a concurrent rebuild shipped L4 with two identical cold-open slides.

The mechanism, for recognition only:

1. `POST /_api/contextinfo` with the cookies gives `FormDigestValue`.
2. `POST .../GetFileById(guid'...')/$value` with headers `X-HTTP-Method: PUT`,
   `X-RequestDigest: <digest>`, body = new pptx bytes.

If you have built a `.pptx` locally that the web editor cannot produce (a slide
master or layout change), report where the file is and let the instructor upload
it or open it in desktop PowerPoint. Do not upload it yourself. **An embedded
local media file used to be on that list and is not any more, and neither are
adding or reordering slides**, see below.

### Precision drawing via co-authoring

Validated by building a multi-shape diagram slide entirely in the web editor
while the file's owner was editing live (REST upload stays 423-locked the
whole time). Key facts:

- **Skip the password page in the browser**: inject the `FedAuth` cookie from
  the Step-1 unlock into the Playwright context (`ctx.add_cookies`) before
  loading the sharing link, lands directly in Editing mode.
- **Exact sizes**: the contextual **Shape** ribbon tab has numeric
  Width/Height fields; triple-click the field, type e.g. `0.34"`, Enter.
  (Verify it took. A missed click followed by a canvas drag can grab a resize
  handle and stretch the shape.)
- **Exact positions**: the slide maps linearly to canvas pixels. Measure the
  slide's white bounding box on a screenshot to derive the px/inch scale and
  slide origin for your viewport/zoom. Insert the shape, size it numerically,
  then mouse-drag its center to the computed pixel target; shapes snap onto
  thin guide lines cleanly. Verify positions by thresholding a screenshot
  (dark-pixel column profile) rather than trusting the drag.
- Arrow-key nudge moves a shape only ~0.01" per press, fine-tune only.
- `Arrange > Align` (Align to Slide) gives exact horizontal/vertical
  centering; keyboard shortcuts work (`Ctrl+A`/`Ctrl+E` inside a text box);
  if driving via an HTTP bridge, URL-encode `+` in key combos as `%2B`.
- **Slide masters/layouts CANNOT be edited in PowerPoint for the web**
  (Microsoft limitation, no Slide Master view). To make a built slide into a
  reusable layout: desktop PowerPoint (View → Slide Master, paste shapes into
  a new layout), which means handing the job to the instructor. This is not a
  licence to use path B. Duplicating the finished slide is a
  workflow-equivalent substitute that stays inside the web editor.

### Adding, duplicating, deleting and reordering slides CAN be done here

This page and CLAUDE.md both used to list "adding or reordering slides, and
therefore a whole spec rebuild" among the things that had to be built locally
and handed to the instructor. Wrong, and wrong the same way the media claim
below was wrong: assumed rather than probed.

Right-clicking a thumbnail offers, all enabled: **New Slide** (`Ctrl+M`),
**Duplicate Slide** (`Ctrl+D`), **Delete Slide**, **Change Slide Layout**,
**Hide Slide**, **Add Section**, plus Cut/Copy/Paste. Reordering is a drag in
the thumbnail rail. `web_editor.py` wraps these as `add_slide_after`,
`duplicate_slide`, `delete_slide`, `move_slide` and `set_slide_layout`.

New Slide, Change Slide Layout to `Title Only`, the spec title typed
into the placeholder the layout supplies (its box is read from the master,
since a slide inheriting a placeholder reports no position of its own), the
body drawn as a text box, and the figure uploaded from `figures-shared/`. It
appends only, which keeps the arithmetic honest: nothing that follows shifts
index, so every other op in the plan still points at the slide it was planned
against. It declines, per slide and with the reason named, a spec slide whose
content is a **video** (no fill-transparency or poster-frame control for the
band), a **table** (a double-click lands in a cell, not the shape) or an
**equation** (OMML). Typed text takes the box's default font, so the builder's
per-run sizes, colours and bullet levels are not reproduced, and a slide added
here is in no section until `normalize_sections.py` runs, so PowerPoint draws
it under `slide-graveyard`. Both are printed as notes on the plan.

Note that *applying* an existing layout via Change Slide Layout is not the same
as *editing* a master or layout, which still cannot be done here.

**Match the layout name exactly.** The gallery is generated from the deck's own
master, so its names are the strings `python-pptx` reports as
`slide_layout.name`. This course's master offers `Title Only` alongside
`1_Title Only`, `2_Title Only`, `3_Title Only` and `4_Title Only`, and
`3_Title Only` has no title placeholder at all. `click_control`'s usual
`aria-label*=` substring match would take whichever of the five sorts first and
would not complain, so a slide could land on the layout that drops the title
about to be typed. `web_editor.set_slide_layout` matches exactly, scopes the
search to the open menu container so a ribbon button cannot be mistaken for a
gallery entry, and raises with the full offered list when the name is not
there. It cannot confirm itself: a slide's layout appears in no thumbnail
label and on no ribbon, so the proof is `slide_layout.name` in the
re-downloaded blob, which `browser_edit_deck.check_fidelity` checks.

Five things established the hard way, three of them by losing a slide:

- **New Slide inserts after the *selected* slide, not the one you right-clicked.**
  Right-clicking slide 6 while slide 1 was current put the new slide after slide
  1. `_slide_menu` selects first for this reason.
- **The thumbnail rail cannot reliably identify a slide.** Labels populate
  lazily, so a slide's `Has notes` marker arrives after its thumbnail renders,
  and until it does an untitled media slide's label is *character-for-character*
  what a blank slide's label is. Code deleting "blank" slides deleted L40's
  video slide on exactly that collision. Take indices from the downloaded file;
  refuse to act when the file and the rail disagree on the slide count.
- **Never confirm a slide operation by the slide count.** The probe that
  established all of this deleted a real content slide out of L40 and reported
  success, because it checked only that the count had returned to 13. It had.
  Compare the whole ordered label list, and pass `expect=` to `delete_slide`.
- **A drag needs several mouse moves between down and up.** One move registers
  as a click, the rail never enters drag mode, and the reorder silently does
  nothing while looking like it worked.
- **The rail is not evidence that a reorder happened.** The check inside
  `move_slide` compares labels the editor is still filling in against an
  expectation built from labels it filled in a moment earlier, so it can agree
  with itself while the file on the server disagrees with both. What settles it
  is the stored blob: `probe_slide_ops.py` waits for the save, re-downloads,
  parses with `python-pptx`, and compares the whole ordered slide list, after
  each of add, reorder and delete. Slide identity there is a hash of every
  shape name, every text run, the notes, the layout name and the byte size of
  embedded media, so it is position-independent and two slides are the same
  slide only if their contents are. Where two slides hash the same the run says
  the comparison could not tell them apart rather than banking the pass.
  `--skip-stored-check` turns it off and makes the result weaker.

Repairing a deck this damages is `scripts/ppt/repair_l40.py`'s subject matter:
SharePoint version history is the obvious undo, but `/_api/.../Versions` returns
**403** for the guest-link account, so the repair goes back through the editor
like any other content change.

### Inserting local media (pictures, video, audio) CAN be done here

This doc and CLAUDE.md both used to say the web editor could not embed a local
trimmed media file. That was wrong, and it was wrong because it had been
assumed rather than probed, unlike every other limitation on this page. It was
also expensive: it pushed clip work onto the banned REST-upload path, which is
the path that ate the last slide of L21 and of L33.

**It is implemented, not merely possible.** `browser_edit_deck.py --clips`
diffs the video embedded in a deck against `scripts/ppt/clips.yaml` and swaps a
re-cut clip in place. Use that rather than driving the menus by hand.

`python scripts/ppt/probe_ribbon.py L1 --shots /tmp/ribbon` re-establishes the
facts below. It only opens menus and reads them, so it is safe to run against a
live deck; it reports `deck_modified: false` to say so.

Insert → **Pictures** / **Video** / **Audio** → **This Device** each expose a
plain `<input type="file">`, which Playwright drives with `set_input_files`
(no OS file dialog to negotiate):

| Insert | input id | `accept` |
|---|---|---|
| Pictures | `fileInputId` | `.jpg .jpeg .jfif .png .gif .bmp .wmf .emf .tif .tiff .svg` |
| Video | `uploadFileInputId` | `.mp4 .mov .m4v .webm` |
| Audio | `uploadFileInputId` | `.mp3 .wav .m4a .aac` |

`.mp4` is what `scripts/ppt/fetch_clips.py` writes after its AV1 to H.264
fallback, so a trimmed clip is directly insertable with no conversion step.

Verified 2026-08-15 against L1. Menus also offer Stock Images / Stock Videos /
Online Video / Search on Web / OneDrive / Brand Images, and the ribbon carries
Cameo, Icons, SmartArt, Chart, Shapes, Table, Symbol and Footer.

Two gotchas from writing the probe, both of which make a menu look absent when
it is not:

- **The ribbon's flyout items have no `aria-label`** and are `[role=menuitem]`,
  not `button`. Name matching has to fall through to visible text or the Video
  branch silently never opens (it did not, for three runs).
- **The previous flyout's items stay in the DOM, hidden, and sort ahead of the
  open menu's.** Taking `.first` and testing visibility throws away the whole
  selector on a stale hit; iterate the matches and click the visible one. The
  same staleness applies to the upload input, so read `accept` after the menu
  choice and probe one media kind at a time (`--kinds Video`), or you will read
  the kind before it.

#### The upload is byte-exact, measured rather than assumed

Swapping L2's torsion clip on 2026-08-15: 5,413,648 bytes handed to
`set_input_files`, and `/ppt/media/media1.mp4` in the re-downloaded blob is
5,413,648 bytes with the same SHA-256. **The editor does not re-encode.** So a
clip placed this way is exactly the file `fetch_clips.py` cut, and the deck can
still be checked against `clips.yaml` by size afterwards.

#### Waiting for the upload, and three things that mislead

- **Readiness is the contextual `Video` / `Picture` tab appearing**, which only
  happens once the object is on the slide and selected. Poll for it with a
  generous timeout: a 5 MB clip is minutes, not seconds.
- **Those contextual tabs carry no `aria-label`**, only text, unlike every
  permanent tab. An `aria-label`-only test never sees them, which produced a
  5-minute timeout on an insert that had already worked, with the clip sitting
  in the stored deck the whole time.
- **The numeric Size fields have no label and no stable id.** They were
  `input785` and `input793` one boot and will be something else the next, and
  neither carries `aria-label`, `title` or `name`. Find them by the shape of
  their value, an inch measurement like `10.67"`; the only other visible inputs
  are the search box and the zoom percentage, and neither has the inch mark.
  They come in DOM order width then height, and the aspect ratio is locked, so
  type the width alone.

#### Placement: exact where Align can express it, reported where it cannot

There are **no numeric Position fields** in PowerPoint for the web (desktop's
Format Shape pane is absent), so position is only as exact as
`Arrange > Align > Align to Slide` allows. That covers the two cases that
matter: an object sized to the whole slide is at (0, 0) once centred, which is
the full-bleed clip, and a centred figure is centred. `place_selected` reports
`positioned: false` for anything else rather than dragging blind on a live
deck. The measured result on L2 was `[6458, 0, 12178619, 6855416]` against a
`[0, 0, 12192000, 6858000]` slide, i.e. within 0.015" on every edge.

`Arrange > Send to Back` is how a full-bleed clip ends up under its message
band, and it is a separate step: an inserted object always lands on top.

**No poster-frame control exists here.** A clip inserted through the browser
shows its own first frame, where `build_deck_from_spec` would have set the
`poster_at` still. If a specific poster matters for a slide, that is a rebuild.

#### Swapping a clip: order the operations so the slide is never empty

`--clips` plans upload, then delete, then place, and the order is the whole
design:

- Upload first, so the slide always has a video on it. If anything fails
  afterwards, the deck is a re-run away rather than broken.
- Delete second, while the two are still **distinguishable**: a fresh insert
  lands at the editor's own size, smaller than the full-bleed clip it replaces,
  so a click near the old clip's top edge reaches only the old one. At the
  centre it would reach the new one.
- Place last, because placing the new clip full-bleed makes it the same box as
  the stale one, and then the delete has nothing to aim at.

## Verifying persistence

Always confirm an edit landed by re-downloading the stored blob (Step 2)
~1-2 minutes after editing and inspecting the pptx XML. Do not trust the web
editor's "Saved" indicator or an apparently-successful upload alone.

`--deck-dir` does not change this rule. A directory of decks is a re-download
only if it was filled after the edit, so pull it again before verifying rather
than reusing the copy the plan was made against.
