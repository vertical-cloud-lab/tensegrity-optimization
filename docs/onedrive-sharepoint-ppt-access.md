# OneDrive/SharePoint PowerPoint: programmatic access recipe

How to download and edit a PowerPoint file that is shared through a OneDrive or
SharePoint sharing link, from a headless environment such as a CI runner.
Validated against a real password-protected OneDrive for Business link.

This page is self-contained. Every technique below is given as a runnable
snippet rather than as a pointer to a script, so nothing here depends on a file
that lives somewhere else. No secrets appear.

**The short version.** The link password buys a guest `FedAuth` cookie. That
cookie authorizes the SharePoint REST API for reading, and it also lets a
headless browser skip the password page and land directly in the Office web
editor. So: read over REST, write through the browser, and prove every write by
re-downloading the stored file and parsing it.

Almost everything on this page was established by probing a live editor, and
most of it is here because the obvious alternative fails. The failures are
usually silent, which is the reason for the length: a step that quietly does
nothing costs far more than one that raises.

## Contents

- [What you need](#what-you-need)
- [Step 1: unlock the link](#step-1-unlock-the-link)
- [Step 2: find the file's id](#step-2-find-the-files-id)
- [Step 3: download the stored file](#step-3-download-the-stored-file)
- [Step 4: read the file offline, and plan against it](#step-4-read-the-file-offline-and-plan-against-it)
- [The write rule: browser yes, REST no](#the-write-rule-browser-yes-rest-no)
- [Booting the web editor](#booting-the-web-editor)
- [Driving the editor](#driving-the-editor)
- [Slide operations](#slide-operations)
- [Inserting local media](#inserting-local-media)
- [Precision drawing](#precision-drawing)
- [What genuinely cannot be done here](#what-genuinely-cannot-be-done-here)
- [Approaches that look right and are not](#approaches-that-look-right-and-are-not)
- [Verifying persistence](#verifying-persistence)

## What you need

```bash
pip install playwright python-pptx        # no `playwright install` needed
```

Launch with `channel="chrome"` to drive the system Chrome, which skips the
browser download entirely. On a GitHub Actions `ubuntu-latest` runner Chrome is
already present.

Terms used throughout:

| Term | Meaning |
|---|---|
| Sharing link | `https://<tenant>-my.sharepoint.com/:p:/g/personal/<owner>/<share-token>` |
| Link password | Injected as an environment variable or workflow secret (`ONEDRIVE_EDIT_PASSWORD` below). Never print it |
| Site base | `https://<tenant>-my.sharepoint.com` |
| Site path | `/personal/<owner>`, the path segment the REST API hangs off |
| UniqueId | The file's GUID in the document library, read from the viewer URL after unlock |
| EMU | English Metric Unit, PowerPoint's internal length. 914,400 to the inch |

A file can be shared through more than one link, and only one of them can be
written through. Keep them apart, and label them, because they are
indistinguishable by inspection:

- The **edit link**, which is the one to use everywhere below.
- The **view link**, which opens the editor read-only and **silently discards
  every change**. Nothing raises. If a run reports success and the stored file
  is unchanged, check this first.

## Step 1: unlock the link

An anonymous GET of the sharing link returns the `guestaccess.aspx` password
page, which is a standard ASP.NET form. Submit the password as a postback. On
success the response redirects to `Doc.aspx` (the PowerPoint web viewer) and the
cookie jar gains a guest `FedAuth` cookie that authorizes the REST API. A wrong
password stays on the page with "Link password is incorrect."

```python
import os, re, html, urllib.request, urllib.parse, http.cookiejar

BASE = "https://<tenant>-my.sharepoint.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def unlock(share_url, password=None):
    """Submit the link password. Returns (opener, cookie jar, Doc.aspx URL)."""
    pw = password or os.environ["ONEDRIVE_EDIT_PASSWORD"]
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", UA)]

    page = op.open(share_url).read().decode("utf-8", "replace")
    m = re.search(r'action="([^"]*guestaccess\.aspx[^"]*)"', page)
    if not m:
        raise RuntimeError("no guestaccess form; page layout changed?")
    action = html.unescape(m.group(1))
    if action.startswith("/"):
        action = BASE + action

    def field(name):                      # the ASP.NET viewstate fields
        f = re.search(r'name="%s"[^>]*value="([^"]*)"' % name, page)
        return html.unescape(f.group(1)) if f else ""

    data = {
        "__EVENTTARGET": "btnSubmitPassword", "__EVENTARGUMENT": "",
        "SideBySideToken": field("SideBySideToken"),
        "__VIEWSTATE": field("__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": field("__VIEWSTATEGENERATOR"),
        "__VIEWSTATEENCRYPTED": "",
        "__EVENTVALIDATION": field("__EVENTVALIDATION"),
        "txtPassword": pw,
    }
    resp = op.open(urllib.request.Request(
        action, urllib.parse.urlencode(data).encode(), method="POST"))
    if "Doc.aspx" not in resp.url:
        raise RuntimeError("unlock failed: no Doc.aspx redirect")
    return op, cj, resp.url
```

On an edit-enabled link the unlocked guest session identifies as **"Guest
Contributor"** (`GET /_api/web/currentuser`) with the `EditListItems` permission
bit set. The password gates entry, and entry grants edit.

Pull the cookie itself out when the browser needs it, which it does in
[Booting the web editor](#booting-the-web-editor):

```python
def fedauth(share_url):
    """The guest FedAuth cookie value, for handing to a browser context."""
    _op, cj, _doc_url = unlock(share_url)
    return next(c.value for c in cj if c.name == "FedAuth")
```

## Step 2: find the file's id

The `Doc.aspx` URL carries both halves of the REST address:

```python
def doc_info(doc_url):
    """(site_path, unique_id) from a Doc.aspx URL."""
    u = urllib.parse.urlparse(doc_url)
    unique_id = urllib.parse.parse_qs(u.query)["sourcedoc"][0].strip("{}")
    site_path = u.path.split("/_layouts/")[0]        # /personal/<owner>
    return site_path, unique_id
```

## Step 3: download the stored file

With the same opener and cookie jar:

```python
import json

def download(op, site_path, unique_id):
    return op.open(BASE + site_path +
                   "/_api/web/GetFileById(guid'%s')/$value" % unique_id).read()


def file_meta(op, site_path, unique_id):
    """Metadata, including TimeLastModified. Useful as a freshness guard."""
    url = BASE + site_path + "/_api/web/GetFileById(guid'%s')" % unique_id
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    return json.loads(op.open(req).read())
```

`GetFileByUniqueId` does not exist on this endpoint. Use
`GetFileById(guid'...')`.

### Reading the file without the link password

Getting the bytes and authenticating with the sharing-link password are two
different jobs, and tools tend to conflate them because unlocking the link is
the one route to the bytes that they happened to write first. A copy pulled
through a signed-in browser is the same stored blob, so a tool that only needs
to *read* a file should accept a path on disk as an alternative to a REST
session. Everything downstream parses the same bytes, so diffs, byte-size media
checks and slide-count comparisons are unchanged.

Two limits are real, and are worth enforcing in code rather than leaving to the
reader:

- **Applying an edit cannot take this route.** Edits go through the live web
  editor, and a file on disk is a copy of the stored blob, not the file.
- **A freshness guard cannot take this route.** With no REST session there is no
  `TimeLastModified` to re-read, so a check that compares against it has nothing
  to compare with.

**A directory is only as current as the moment it was filled.** The
verify-by-re-download discipline below is unchanged: pull again after an edit,
or you are verifying against a stale copy and it will report that everything is
fine.

## Step 4: read the file offline, and plan against it

This is the step that makes everything after it possible, so it is worth doing
first even though the editor is where the writing happens. `python-pptx` reports
the name, the geometry and the text of every shape. The geometry is what turns
into a click target, so a plan built here is executable in the browser without
any exploratory clicking on a live file.

```python
import io
from pptx import Presentation

prs = Presentation(io.BytesIO(download(op, site_path, unique_id)))
slide_size = (prs.slide_width, prs.slide_height)      # EMU, e.g. 12192000 x 6858000

for i, slide in enumerate(prs.slides, start=1):
    for shape in slide.shapes:
        emu = [shape.left, shape.top, shape.width, shape.height]
        print(i, shape.shape_type, shape.name, emu,
              shape.text_frame.text if shape.has_text_frame else "")
    print(i, "notes:", slide.notes_slide.notes_text_frame.text
          if slide.has_notes_slide else "")
```

Shape names here are the same strings the editor's Selection Pane shows, which
is what lets an offline plan be checked against the live file before it runs. A
name mismatch means the plan was built against a different version.

**Split the work into plan, apply and verify, and make plan read-only.** Plan
downloads the stored file, diffs it against what you intend, and prints the
operations. Apply drives the editor. Verify re-downloads and re-diffs. The split
is what lets a run be inspected before it touches a file somebody else is
working in, and it costs nothing, because the plan stage is the parsing you had
to do anyway.

Shapes a repeated build has stacked exactly on top of each other are worth
detecting in the plan stage. They are invisible on a screenshot and cannot be
told apart by clicking, so the only honest way to remove one is to delete the
front shape and then confirm from the Selection Pane that the survivor is the
one you meant to keep.

## The write rule: browser yes, REST no

**Edit through the headless browser. Do not write to the file with the REST
API.** The browser path merges with whoever else has the file open. The REST
path replaces the file underneath them.

Three reasons this is a rule rather than a preference:

- REST upload is a **whole-file replace**. It cannot merge, so it discards
  whatever the owner changed since your download, and it gives no sign that it
  did.
- It returns **HTTP 423 `SPFileLockException`** ("locked for shared use")
  whenever anyone has the file open. That is a co-authoring lock rather than a
  permission failure, and it lingers about 10 minutes after they close. A
  process that leans on REST therefore stalls or races.
- It forces a `python-pptx` round trip on a file the library did not write.
  Round-tripping a deck built by PowerPoint has silently produced duplicate zip
  part names, which cost the last slide of two decks in one project, and it
  reformats more than you asked it to.

The mechanism, recorded so a 423 in a log is recognizable rather than so it can
be used:

```python
# NOT a fallback. Here to explain failures you will see while reading metadata.
digest = json.loads(op.open(urllib.request.Request(
    BASE + site_path + "/_api/contextinfo", data=b"",
    headers={"Accept": "application/json"})).read())["FormDigestValue"]
req = urllib.request.Request(
    BASE + site_path + "/_api/web/GetFileById(guid'%s')/$value" % unique_id,
    data=new_pptx_bytes, method="POST",
    headers={"X-HTTP-Method": "PUT", "X-RequestDigest": digest})
op.open(req)                                    # 423 while anyone has it open
```

If you have built a `.pptx` locally that the web editor genuinely cannot produce
(see [What genuinely cannot be done
here](#what-genuinely-cannot-be-done-here)), say where the file is and let the
file's owner open it in desktop PowerPoint. That list is much shorter than it
looks, and three entries that used to be on it turned out to be assumptions
nobody had probed.

## Booting the web editor

Inject the `FedAuth` cookie from step 1 so the password page never renders, load
the **edit** link, and wait for the editor to reach editing mode. Boot takes
about 40 seconds, so budget for it.

```python
from playwright.sync_api import sync_playwright

pw = sync_playwright().start()
browser = pw.chromium.launch(channel="chrome", headless=True,
                             args=["--no-sandbox", "--disable-dev-shm-usage"])
ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
ctx.add_cookies([{"name": "FedAuth", "value": fedauth(edit_url),
                  "domain": "<tenant>-my.sharepoint.com", "path": "/"}])
page = ctx.new_page()
page.goto(edit_url, wait_until="domcontentloaded", timeout=150_000)

# The editor lives in a cross-origin iframe. Match on frame.url, not on the
# iframe's src attribute, which is not reliable here.
ed = None
for _ in range(75):                      # boot is ~40 s; allow well past it
    ed = next((f for f in page.frames if "officeapps.live.com" in f.url), None)
    if ed:
        try:
            status = ed.evaluate("() => (document.querySelector('#StatusBar')"
                                 "||{}).innerText || ''")
            if re.search(r"Slide\s+\d+\s+of\s+\d+", status):
                break                    # editing mode, and it knows the count
        except Exception:
            pass                         # frame is still navigating
    page.wait_for_timeout(2_000)
else:
    raise RuntimeError("no editing-mode status bar; is this the view link?")
```

Two facts that the rest of this page assumes:

- **`ed` is a frame and `page` is a page.** Reads and locators go through `ed`.
  Keyboard and raw mouse go through `page`. Mixing them up produces silence, not
  an error.
- **Ready means `#StatusBar` reads `Slide N of M`.** That string is also the
  only honest confirmation that a navigation landed, so keep it around:

```python
def status(ed):
    return ed.evaluate("() => (document.querySelector('#StatusBar')||{})"
                       ".innerText || ''")

def slide_count(ed):
    return int(re.search(r"Slide\s+\d+\s+of\s+(\d+)", status(ed)).group(1))

def current_slide(ed):
    return int(re.search(r"Slide\s+(\d+)\s+of", status(ed)).group(1))
```

Typed changes autosave through co-authoring and merge with any live human
session, including one that is open right now. The stored file reflects them
within one to two minutes. **Wait for the save before closing the browser**,
because autosave is asynchronous and closing early loses the tail of the last
edit:

```python
def is_saved(ed):
    """The indicator's innerText is empty. The state is in its aria-label."""
    label = ed.evaluate("""() => {const b =
        document.querySelector('#SaveStatusButton');
        return b ? (b.getAttribute('aria-label') || '') : '';}""")
    return "saved" in label.lower()
```

## Driving the editor

### Clicking a ribbon or menu item

Every menu interaction goes through one helper, because two things break the
obvious one-liner and both were found by probing:

```python
def click_control(ed, name, timeout=25_000):
    """Click the first *visible* control whose accessible name matches."""
    for sel in (f'[role="tab"][aria-label*="{name}" i]',
                f'button[aria-label*="{name}" i]',
                f'[role="menuitem"][aria-label*="{name}" i]',
                f'button:has-text("{name}")',
                f'[role="menuitem"]:has-text("{name}")',
                f'span:text-is("{name}")'):
        try:
            loc = ed.locator(sel)
            for i in range(min(loc.count(), 12)):
                if loc.nth(i).is_visible():
                    loc.nth(i).click(timeout=timeout)
                    return True
        except Exception:
            continue
    return False
```

- **Ribbon buttons carry `aria-label`, but flyout items do not**, and they are
  `[role=menuitem]` rather than `button`. Matching has to fall through to
  visible text, or a whole branch of the Insert menu silently never opens.
- **The previous flyout's items stay in the DOM, hidden, and sort ahead of the
  open menu's.** Taking `.first` and testing visibility throws the selector away
  on a stale hit, so iterate the matches and click the visible one.

### Clear the click shields first

`#WACDialogOverlay` is a modal click shield, and it breaks every obvious way of
checking for it:

- **It is invisible.** Fully transparent, nothing on a screenshot. A visual
  check finds nothing while it is covering the page.
- **It does not block `evaluate()`.** Every JS read keeps working through it, so
  state looks healthy while it is up. Only clicks are swallowed, so the symptom
  is a click that retries for Playwright's full 25 second timeout and then fails
  on an element that is plainly there.
- **The id is in the DOM more than once.** So
  `document.querySelector('#WACDialogOverlay')` answers about whichever copy
  sorts first, which is usually a dead leftover, and reports clear while a live
  sibling covers the page. Use `querySelectorAll`, and filter on layout and
  `pointer-events` rather than on anything visible.

```python
OVERLAY_JS = """
(sel) => [...document.querySelectorAll(sel)].map(el => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return {id: el.id || null, w: Math.round(r.width), h: Math.round(r.height),
            display: s.display, visibility: s.visibility,
            pointerEvents: s.pointerEvents};
  }).filter(o => o.w > 0 && o.h > 0 && o.display !== 'none'
                 && o.visibility !== 'hidden' && o.pointerEvents !== 'none')
"""
SHIELDS = '#WACDialogOverlay, [id^="WACDialogOverlay"], .WACDialogOverlay'

def dismiss_overlays(page, ed, timeout_ms=30_000):
    """Escape until nothing is shielding the page. True if it is clear."""
    waited = 0
    while ed.evaluate(OVERLAY_JS, SHIELDS):
        if waited >= timeout_ms:
            return False
        page.keyboard.press("Escape")      # only when there IS one to dismiss:
        page.wait_for_timeout(900)         # Escape also drops a selection
        waited += 900
    return True
```

Send Escape only when a shield is actually up. Escape with a shape selected
drops the selection, and the placement and deletion steps below both depend on a
selection surviving.

### Navigating

Clicking the thumbnail is the only navigation that proved reliable:

```python
def goto_slide(page, ed, index):
    if current_slide(ed) == index:
        return
    dismiss_overlays(page, ed)
    thumbs = ed.locator('[id^="grid-content-view-id"]')
    if not 1 <= index <= thumbs.count():          # else .nth() times out
        raise IndexError(f"slide {index} of {thumbs.count()}")
    thumbs.nth(index - 1).click(timeout=25_000)
    for _ in range(25):
        page.wait_for_timeout(400)
        if current_slide(ed) == index:
            return
    raise RuntimeError(f"navigation to slide {index} did not land")
```

Each thumbnail carries an `aria-label` with the slide's title plus `Has notes`
and `Is hidden`, which is a cheap way to spot hidden slides. It is not a
reliable way to identify a slide: see [Slide operations](#slide-operations).

### Addressing a shape by where it is drawn

The slide is letterboxed inside `#WACViewPanel`, so fit it by aspect ratio and
map the EMU box `python-pptx` reported for the same file. A click both selects
the shape and gives the canvas keyboard focus, which is the combination
everything else needs.

```python
def panel_pos(ed, emu, slide_w, slide_h):
    """Shape EMU box to a click point relative to #WACViewPanel."""
    vw, vh = ed.evaluate("""() => {const r =
        document.querySelector('#WACViewPanel').getBoundingClientRect();
        return [r.width, r.height];}""")
    aspect = slide_w / slide_h
    if vw / vh > aspect:
        sh_px, sw_px = vh, vh * aspect
    else:
        sw_px, sh_px = vw, vw / aspect
    left, top, width, height = emu
    return ((vw - sw_px) / 2 + (left + width / 2) / slide_w * sw_px,
            (vh - sh_px) / 2 + (top + height / 2) / slide_h * sh_px)
```

`locator.click(position=...)` adds the iframe offset for you, so panel-relative
coordinates are enough for a click. The raw mouse API does not, and a drag has
to use the raw mouse API, so a drag needs `#WACViewPanel`'s own page box added
on top.

Confirm a click landed by checking that focus reached the canvas:

```python
active = ed.evaluate("() => (document.activeElement||{}).id || ''")
assert "WACViewPanel_EditingElement" in active
```

To click empty canvas and select nothing, aim for the letterbox bar beside the
slide, or just inside the slide's top edge when the panel is the same shape as
the slide. Not the top-left corner: the thumbnail pane's resize handle sits over
it and swallows the click, which produces the same 25 second timeout an
invisible shield does.

```python
def focus_empty_canvas(page, ed, slide_w, slide_h):
    """Give the slide keyboard focus and select nothing."""
    dismiss_overlays(page, ed)
    vw, vh = ed.evaluate("""() => {const r =
        document.querySelector('#WACViewPanel').getBoundingClientRect();
        return [r.width, r.height];}""")
    aspect = slide_w / slide_h
    if vw / vh > aspect + 0.02:                     # bars left and right
        x, y = (vw - vh * aspect) / 4, vh / 2
    elif vh > vw / aspect + 8:                      # bars top and bottom
        x, y = vw / 2, (vh - vw / aspect) / 4
    else:                                           # no bars: the top strip
        x, y = vw / 2, 12
    ed.locator("#WACViewPanel").click(position={"x": x, "y": y}, timeout=25_000)
    page.keyboard.press("Escape")
    page.wait_for_timeout(400)
```

### Replacing text

```python
def replace_text(page, ed, emu, text, slide_w, slide_h):
    dismiss_overlays(page, ed)
    x, y = panel_pos(ed, emu, slide_w, slide_h)
    ed.locator("#WACViewPanel").dblclick(position={"x": x, "y": y}, timeout=25_000)
    page.wait_for_timeout(1_500)
    if "WACViewPanel_EditingElement" not in ed.evaluate(
            "() => (document.activeElement||{}).id || ''"):
        raise RuntimeError("double-click did not focus the canvas; the shape "
                           "may not be where the plan thinks it is")
    page.keyboard.press("Control+a")
    for i, line in enumerate(text.split("\n")):
        if i:
            page.keyboard.press("Enter")
        if line:
            page.keyboard.type(line, delay=8)      # type(), never insert_text()
    page.keyboard.press("Escape")                  # shape selected, not editing
    page.keyboard.press("Escape")                  # nothing selected
```

Confirm typing landed by reading the canvas back, with whitespace removed on
both sides so that line wrapping does not fail a comparison about text that is
plainly there:

```python
canvas = ed.evaluate("() => (document.querySelector('#WACViewPanel')||{})"
                     ".innerText || ''")
assert "".join(expected.split()) in "".join(canvas.split())
```

Typing goes through real key events, so PowerPoint's autocorrect is in the loop
and could in principle rewrite what lands. Measured on one long notes edit it
did not, and the stored text matched the typed text character for character.
Nothing in the browser defends against it, so the check that matters is against
the re-downloaded file.

### Adding a text box

`Insert > Text Box` **creates nothing**. It arms a draw mode, and the box is
whatever the next drag on the canvas encloses. Three ways that goes wrong
silently:

- **A single `mouse.move` between `down` and `up` reads as a click**, which
  disarms the mode and leaves the slide untouched. Move in several steps.
- **Do not Escape out and come back to type.** A text box with no text has no
  hit area, so a double-click on it falls through to whatever is behind it. Type
  into the state the drag leaves behind, where focus is already on the canvas.
- **PowerPoint discards an empty text box on save.** A typing failure therefore
  leaves no evidence at all rather than a visibly empty box, so confirm the
  typed characters are on the canvas before returning.

```python
box = ed.locator("#WACViewPanel").bounding_box()
x0, y0 = box["x"] + px_left, box["y"] + px_top      # page coordinates
click_control(ed, "Insert"); click_control(ed, "Text Box")
page.mouse.move(x0, y0); page.mouse.down()
for k in range(1, 6):                               # several moves, not one
    page.mouse.move(x0 + dx * k / 5, y0 + dy * k / 5)
page.mouse.up()
page.keyboard.type("first line", delay=8)
```

A drag narrower than about 45 px on screen may not register as a drag at all.
The editor autofits a text box to its text on save, so the drawn size is a
starting point rather than the result.

### Deleting a shape: whether Escape is needed depends on what you clicked

This is the single most expensive asymmetry on this page, and it was learned
once in each direction:

- **A text box**: the click lands a caret *inside the text*, so Escape is what
  promotes it to a selection of the shape. Without the Escape, `Delete` removes
  one character and leaves the shape in place. Observed: `TYPED LINE` became
  `TYPED INE`.
- **A picture or a video**: the click already selects the object, and that same
  Escape *drops* the selection, so `Delete` does nothing at all.

Ask the ribbon which case you are in rather than hard-coding either. A
contextual `Picture`, `Video` or `Audio` tab means the object itself is
selected. A `Shape` tab does not, because a text box raises one while the caret
is still inside its text.

```python
MEDIA_TABS = {"Picture", "Video", "Audio"}

def media_tab(ed):
    """Read innerText too: contextual tabs carry no aria-label, unlike every
    permanent tab. An aria-label-only test never sees them, which once cost a
    five minute timeout on an insert that had already succeeded."""
    labels = ed.evaluate("""() => [...document.querySelectorAll('[role="tab"]')]
        .filter(t => t.getBoundingClientRect().width > 0)
        .map(t => ((t.getAttribute('aria-label') || '') + ' ' +
                   (t.innerText || '')).trim())""")
    for label in labels:
        head = label.split()[0] if label.split() else ""
        if head in MEDIA_TABS:
            return head
    return None


def select_at(page, ed, emu, slide_w, slide_h):
    """Select whatever is drawn frontmost at `emu`. Returns its media tab."""
    dismiss_overlays(page, ed)
    x, y = panel_pos(ed, emu, slide_w, slide_h)
    ed.locator("#WACViewPanel").click(position={"x": x, "y": y}, timeout=25_000)
    page.wait_for_timeout(1_200)
    tab = media_tab(ed)
    if tab is None:                       # a text box: Escape promotes the caret
        page.keyboard.press("Escape")     # to a selection of the shape
        page.wait_for_timeout(500)
    return tab
```

After a delete, confirm from the Selection Pane that the shape you named is the
one that went, rather than trusting the click.

### The Selection Pane: read only

`Ctrl+F10`, or `Arrange > Selection Pane`, lists every shape on the slide **by
name**, and those names are the same strings `python-pptx` reports. That is what
lets an offline plan be checked against the live file.

```python
names = ed.evaluate("""() => {
    const p = document.querySelector('#SelectionPaneContainerDiv');
    if (!p) return [];
    const out = [];
    for (const el of p.querySelectorAll('div[aria-label]')) {
      const t = (el.getAttribute('aria-label')||'').trim();
      if (t && !out.includes(t) &&
          !['Show All','Hide All','Selection Pane'].includes(t)) out.push(t);
    }
    return out;}""")
```

**Never select from it.** Clicking a row draws selection handles on the canvas,
but focus stays on the pane, and a subsequent Delete or keystroke goes nowhere.
Forcing focus back with JS keeps the handles and still does nothing. Use it to
read and to confirm, never to act.

### Speaker notes

```python
def notes_open(ed):
    """Open or closed is the *panel's* height. Do not test
    #EditingNotesPanel_EditingElement, a 0x0 accessibility proxy in both states,
    so it reads "closed" forever and the toggle closes an open pane."""
    return ed.evaluate("""() => {const p =
        document.getElementById('EditingNotesPanel');
        return p ? p.getBoundingClientRect().height > 50 : false;}""")


def set_notes(page, ed, text):
    if not notes_open(ed):
        ed.click("#ShowHideNotes", timeout=25_000)
        page.wait_for_timeout(2_000)
    panel = ed.locator("#EditingNotesPanel")
    b = panel.bounding_box()
    # Neither #NotesContentContainer nor the editing proxy accepts a direct
    # click. Click a point inside the opened panel instead.
    panel.click(position={"x": min(120, b["width"] / 2), "y": b["height"] / 2})
    page.wait_for_timeout(900)
    active = ed.evaluate("""() => {const a = document.activeElement || {};
        return (a.id || '') + '|' + (a.getAttribute ?
               (a.getAttribute('aria-label') || '') : '');}""")
    if "otes" not in active:
        raise RuntimeError(f"focus is {active!r}, refusing to type: Ctrl+A "
                           "here would select the slide and overwrite it")
    page.keyboard.press("Control+a")
    for i, line in enumerate(text.split("\n")):
        if i:
            page.keyboard.press("Enter")
        if line:
            page.keyboard.type(line, delay=6)
```

The focus guard is not defensive padding. A missed click puts `Ctrl+A` on the
slide, and the typing then overwrites slide content.

## Slide operations

Right-clicking a thumbnail offers **New Slide** (`Ctrl+M`), **Duplicate Slide**
(`Ctrl+D`), **Delete Slide**, **Change Slide Layout**, **Hide Slide** and **Add
Section**, all enabled, plus Cut, Copy and Paste. Reordering is a drag in the
thumbnail rail.

Worth stating plainly, because this and embedding a local media file are both
widely assumed to be impossible in PowerPoint for the web. Neither is. Both
assumptions survived a long time because nobody opened the menu and looked, so
treat any limitation on this page that is not backed by a probe the same way.

Applying an existing layout through Change Slide Layout is not the same as
*editing* a master or layout, which genuinely cannot be done here.

```python
def slide_menu(page, ed, index, item):
    """Select thumbnail `index` (1-based), right-click it, pick `item`."""
    dismiss_overlays(page, ed)
    goto_slide(page, ed, index)           # selecting first is NOT redundant
    page.wait_for_timeout(600)
    ed.locator('[id^="grid-content-view-id"]').nth(index - 1).click(
        button="right", timeout=25_000)
    page.wait_for_timeout(1_500)
    hit = click_control(ed, item)
    page.wait_for_timeout(3_500)
    if not hit:
        page.keyboard.press("Escape")     # leave no menu open for the next step
    return hit
```

Five things established the hard way, three of them by losing a slide:

- **New Slide inserts after the *selected* slide, not the one you
  right-clicked.** Right-clicking slide 6 while slide 1 was current put the new
  slide after slide 1. Select first.
- **The thumbnail rail cannot reliably identify a slide.** Labels populate
  lazily, so a slide's `Has notes` marker arrives after its thumbnail renders,
  and until it does an untitled media slide's label is character for character
  what a blank slide's label is. Code deleting "blank" slides deleted a real
  video slide on exactly that collision. Take indices from the downloaded file,
  and refuse to act when the file and the rail disagree on the slide count.
- **Never confirm a slide operation by the slide count.** The probe that
  established all of this deleted a content slide and reported success, because
  it checked only that the count had returned to 13. It had. Compare the whole
  ordered label list, and pass the expected label into the delete so it refuses
  an off-by-one instead of eating a slide.
- **A drag needs several mouse moves between down and up.** One move registers
  as a click, the rail never enters drag mode, and the reorder silently does
  nothing while looking like it worked.
- **The rail is not evidence that a reorder happened.** A check that compares
  labels the editor is still filling in against an expectation built from labels
  it filled in a moment earlier can agree with itself while the stored file
  disagrees with both.

Wait for the labels to settle before snapshotting them, and require three
consecutive identical reads rather than two. A slide's marker can arrive between
any two polls, and the cost of believing an unsettled list is a deleted slide,
not a retry.

Normalize as you read. The rail writes selection state into the same
`aria-label` as the title, so the label of a slide nobody touched changes when
the slide beside it is picked. Without stripping those tokens, every comparison
across an edit reports differences that no edit caused.

```python
def norm_label(label):
    """A thumbnail label with its transient selection-state tokens removed."""
    out = label.replace("\u00a0", " ")     # the rail uses non-breaking spaces
    for token in ("Selected", "Current slide", "selected"):
        out = out.replace(f", {token},", ",").replace(f", {token}", "")
    return " ".join(out.split()).strip().rstrip(",")


def thumbnail_labels(ed):
    return [norm_label(s) for s in ed.evaluate("""() =>
        [...document.querySelectorAll('[id^="grid-content-view-id"]')]
        .map(e => e.getAttribute('aria-label') || '')""")]


def settled_labels(page, ed, timeout_ms=20_000):
    prev, same, waited = None, 0, 0
    while waited < timeout_ms:
        cur = thumbnail_labels(ed)
        same = same + 1 if cur == prev else 0     # same == 2 is three identical
        prev = cur                                # reads, not two
        if same >= 2 and waited >= 6_000:
            return cur
        page.wait_for_timeout(1_200)
        waited += 1_200
    return prev or []
```

**Match a layout name exactly.** The Change Slide Layout gallery is generated
from the file's own master, so its entries are the strings `python-pptx` reports
as `slide_layout.name`. A master can easily offer several layouts whose names
all contain the same words, for instance `Title Only` alongside `1_Title Only`
through `4_Title Only`, one of which may have no title placeholder at all. A
substring match would take whichever sorts first and would not complain, so a
slide can land on a layout that drops the title you are about to type. Match
exactly, scope the search to the open menu container so a ribbon button cannot
be mistaken for a gallery entry, and raise with the full offered list when the
name is not there.

Change Slide Layout cannot confirm itself. A slide's layout appears in no
thumbnail label and on no ribbon, so the proof is `slide_layout.name` in the
re-downloaded file.

### Composing a slide that carries content

New Slide, then Change Slide Layout, then the title typed into the placeholder
the layout supplies, then the body drawn as a text box, then any figure
uploaded. Read the placeholder's box from the **master**, because a slide
inheriting a placeholder reports no position of its own.

Append rather than insert wherever you can. It keeps the arithmetic honest:
nothing that follows shifts index, so every other operation in a plan still
points at the slide it was planned against.

Three kinds of slide are better declined than half-built here, each for a
concrete reason: a **video** slide (no fill-transparency or poster-frame
control), a **table** (a double-click lands in a cell, not the shape) and an
**equation** (OMML). Typed text also takes the box's default font, so per-run
sizes, colours and bullet levels from a builder are not reproduced. Print these
as notes on the plan rather than discovering them in the output.

## Inserting local media

Insert > **Pictures** / **Video** / **Audio** > **This Device** each expose a
plain `<input type="file">`, which Playwright drives with `set_input_files`, so
there is no OS file dialog to negotiate.

| Insert | input id | `accept` |
|---|---|---|
| Pictures | `fileInputId` | `.jpg .jpeg .jfif .png .gif .bmp .wmf .emf .tif .tiff .svg` |
| Video | `uploadFileInputId` | `.mp4 .mov .m4v .webm` |
| Audio | `uploadFileInputId` | `.mp3 .wav .m4a .aac` |

```python
def insert_media(page, ed, kind, path, slide_w, slide_h, timeout_ms=300_000):
    """kind is 'Pictures', 'Video' or 'Audio'. Leaves the object selected."""
    # Deselect first: with a shape still selected from an earlier operation,
    # Insert can act on that shape rather than on the slide.
    focus_empty_canvas(page, ed, slide_w, slide_h)
    for step in ("Insert", kind, "This Device"):
        if not click_control(ed, step):
            raise RuntimeError(f"could not open Insert > {kind} > This Device")
        page.wait_for_timeout(1_500)
    inputs = ed.locator('input[type=file]')
    # The input is created per menu choice and the previous kind's input stays
    # in the DOM, so take the last one, after the menu click.
    inputs.nth(inputs.count() - 1).set_input_files(path)

    waited = 0
    tab = {"Pictures": "Picture"}.get(kind, kind)
    while waited < timeout_ms:            # a 5 MB clip is minutes, not seconds
        page.wait_for_timeout(2_000)
        waited += 2_000
        if media_tab(ed) == tab:          # readiness IS the contextual tab
            return
    raise RuntimeError(f"{path} never appeared; the {tab} tab did not show")
```

Two menu-probing gotchas, both of which make a menu look absent when it is not:
flyout items have no `aria-label` and are `[role=menuitem]` rather than
`button`, and the previous flyout's items stay in the DOM hidden and sort ahead
of the open menu's. Both are handled inside `click_control` above. If you write
a probe that reads the `accept` attribute, read it *after* the menu choice and
probe one media kind at a time, or you will read the previous kind's input.

**The upload is byte-exact, measured rather than assumed.** Swapping a video
clip: 5,413,648 bytes handed to `set_input_files`, and `/ppt/media/media1.mp4`
in the re-downloaded file is 5,413,648 bytes with the same SHA-256. The editor
does not re-encode, so a file placed this way is the file you cut, and the
result can be checked by size afterwards.

Three things that mislead while waiting for an upload:

- **Readiness is the contextual `Video` or `Picture` tab appearing**, which only
  happens once the object is on the slide and selected. Poll with a generous
  timeout.
- **Those contextual tabs carry no `aria-label`**, only text, unlike every
  permanent tab. See `media_tab` above.
- **The numeric Size fields have no label and no stable id.** They were
  `input785` and `input793` one boot and will be something else the next, and
  none of `aria-label`, `title` or `name` is present.

### Placement: exact where Align can express it, reported where it cannot

There are **no numeric Position fields** in PowerPoint for the web. The
desktop's Format Shape pane is absent, so position is only as exact as
`Arrange > Align > Align to Slide` allows. That covers the two cases that
usually matter: an object sized to the whole slide is at (0, 0) once centred,
and a centred figure is centred. Report anything else as unpositioned rather
than dragging blind on a live file.

Find the Size fields **by the shape of their value**, an inch measurement like
`10.67"`. The only other visible inputs in the editor are the search box and the
zoom percentage, and neither carries a trailing inch mark. They come in DOM
order width then height, and the aspect ratio is locked, so type the width
alone. Typing both fights the lock.

```python
def arrange(page, ed, *path):
    """Home > Arrange > ..., one flyout level at a time."""
    if not click_control(ed, "Arrange"):
        return False
    page.wait_for_timeout(1_000)
    for step in path:
        if not click_control(ed, step):
            page.keyboard.press("Escape")
            return False
        page.wait_for_timeout(1_000)
    return True


def size_fields(ed):
    """{'width': {id, inches}, 'height': {...}}, empty if nothing is selected."""
    found = ed.evaluate("""() => {
        const out = [];
        for (const el of document.querySelectorAll('input')) {
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height || !el.id) continue;
          const m = /^\\s*([0-9]+(?:\\.[0-9]+)?)\\s*"\\s*$/.exec(el.value || '');
          if (m) out.push({id: el.id, inches: parseFloat(m[1])});
        }
        return out;}""")
    return {"width": found[0], "height": found[1]} if len(found) >= 2 else {}


def place_selected(page, ed, emu, slide_w, slide_h):
    left, top, width, height = emu
    did = {"sized": False, "positioned": False}
    fields = size_fields(ed)
    if fields:
        ed.locator("#" + fields["width"]["id"]).click(click_count=3)
        page.keyboard.type('%.2f"' % (width / 914_400), delay=25)
        page.keyboard.press("Enter")
        page.wait_for_timeout(2_000)
        now = size_fields(ed)
        did["sized"] = bool(now) and abs(
            now["width"]["inches"] - width / 914_400) < 0.02
    centred = (abs((left + width / 2) - slide_w / 2) < 914_400 // 20 and
               abs((top + height / 2) - slide_h / 2) < 914_400 // 20)
    if centred:
        did["positioned"] = (arrange(page, ed, "Align", "Align Center") and
                             arrange(page, ed, "Align", "Align Middle"))
    return did
```

Measured result of a full-bleed placement: `[6458, 0, 12178619, 6855416]`
against a `[0, 0, 12192000, 6858000]` slide, so within 0.015 inches on every
edge.

`Arrange > Send to Back` is how a full-bleed clip ends up under a title band,
and it is a separate step: an inserted object always lands on top.

**No poster-frame control exists here.** A clip inserted through the browser
shows its own first frame. If a specific poster frame matters, that slide has to
be built somewhere else.

### Swapping a clip: order the operations so the slide is never empty

Upload, then delete, then place. The order is the whole design:

- **Upload first**, so the slide always has a video on it. If anything fails
  afterwards, the file is a re-run away rather than broken.
- **Delete second**, while the two are still *distinguishable*. A fresh insert
  lands at the editor's own size, smaller than the full-bleed clip it replaces,
  so a click near the old clip's top edge reaches only the old one. At the
  centre it would reach the new one.
- **Place last**, because placing the new clip full-bleed makes it the same box
  as the stale one, and then the delete has nothing to aim at.

## Precision drawing

Validated by building a multi-shape diagram slide entirely in the web editor
while the file's owner was editing live, with the REST upload path 423-locked
the whole time.

- **Exact sizes**: the contextual **Shape** ribbon tab has numeric Width and
  Height fields. Triple-click the field, type `0.34"`, press Enter. Verify it
  took: a missed click followed by a canvas drag can grab a resize handle and
  stretch the shape instead.
- **Exact positions**: the slide maps linearly to canvas pixels. Measure the
  slide's white bounding box on a screenshot to derive the pixels-per-inch scale
  and the slide origin for your viewport and zoom. Insert the shape, size it
  numerically, then drag its centre to the computed pixel target. Shapes snap
  onto thin guide lines cleanly. Verify positions by thresholding a screenshot
  (a dark-pixel column profile) rather than trusting the drag.
- Arrow-key nudge moves a shape about 0.01 inches per press. Fine-tuning only.
- `Arrange > Align` (Align to Slide) gives exact horizontal and vertical
  centering. Keyboard shortcuts work (`Ctrl+A` and `Ctrl+E` inside a text box).
  If you are driving the browser through an HTTP bridge, URL-encode `+` in key
  combos as `%2B`.

## What genuinely cannot be done here

The list is shorter than it looks, and it has lost three entries to actual
probes (media insertion, slide add and reorder, applying a layout). What is left:

- **Slide masters and layouts cannot be edited.** PowerPoint for the web has no
  Slide Master view. This is a Microsoft limitation rather than a permissions
  problem. Duplicating a finished slide is the workflow-equivalent substitute
  inside the editor; anything more belongs in desktop PowerPoint.
- **No poster frame for a video**, as above.
- **No numeric position fields**, so placement is limited to what Align to Slide
  can express.
- **Version history is not available to a guest link.** `GET
  /_api/.../Versions` returns **403** for the sharing-link account, so the
  obvious undo does not exist. Repairing a damaged slide goes back through the
  editor like any other content change. Make edits reversible where you can, and
  label test edits clearly.

Before believing that something else is impossible, write a read-only probe that
opens the relevant menus and reports what it finds. A probe that only reads is
safe to run against a live file. Have it print that it did not modify anything,
so a reader does not have to take that on trust.

## Approaches that look right and are not

| Attempt | What happens |
|---|---|
| `keyboard.insert_text()` | Types nothing. `Ctrl+A` visibly selects, the replacement does not happen, so it fails looking like it worked. Office uses a composition model that ignores synthetic `input` events. Use `keyboard.type()`. |
| Escape then Tab to cycle placeholders | Focus lands in an internal `ClipboardTarget` iframe and stays there. Nothing is selected. |
| Select via the Selection Pane, then act | Handles appear on the canvas, but focus stays on the pane and Delete or typing goes nowhere. Forcing focus back with JS keeps the handles and still does nothing. |
| Click a text box, press Delete | Deletes a character, not the shape. Escape first. |
| Click a picture or video, press Escape, then Delete | Nothing happens. The click had already selected the object and the Escape dropped it. The mirror image of the row above, and the reason selection is decided from the ribbon rather than assumed. |
| `querySelector('#WACDialogOverlay')` to check the page is clickable | Reports clear while a live overlay covers the page. The id is in the DOM more than once and the first match is usually a dead leftover. Check all of them. |
| Click Insert > Text Box, then type | Types into the slide, not into a text box. The menu item arms a draw mode; the box only exists once a multi-step drag has enclosed it. |
| Find the editor iframe by its `src` | Unreliable. Match on `frame.url` containing `officeapps.live.com`. |
| Trust the "Saved" indicator's text | Its `innerText` is empty. The state is in its `aria-label`. |
| Confirm a slide operation by the slide count | A delete that removed the wrong slide leaves the count correct and the file wrong. |
| Load the view link and edit | Opens read-only and swallows every change without raising. |

## Verifying persistence

**Re-download the stored file and parse it.** Do not trust the editor's "Saved"
indicator, an apparently successful upload, or the thumbnail rail. One run
believed an upload had landed when it had not.

Wait one to two minutes after the edit before pulling, because SharePoint does
not publish the co-authoring save the instant the editor says it is done. Then
compare identities rather than counts:

```python
import hashlib, re

def slide_identity(slide):
    """Position-independent identity for one slide, from the file itself."""
    names, texts, media = [], [], []
    for shape in slide.shapes:
        names.append(shape.name)
        if shape.has_text_frame:
            flat = re.sub(r"\s+", " ", shape.text_frame.text).strip()
            if flat:
                texts.append(flat)
    for rel in slide.part.rels.values():
        if not rel.is_external and \
                str(rel.target_part.partname).startswith("/ppt/media/"):
            media.append(len(rel.target_part.blob))
    notes = (slide.notes_slide.notes_text_frame.text
             if slide.has_notes_slide else "")
    blob = repr((names, texts, sorted(media), slide.slide_layout.name,
                 re.sub(r"\s+", " ", notes).strip()))
    digest = hashlib.sha1(blob.encode("utf-8")).hexdigest()[:10]
    return f"{digest} {texts[0][:44] if texts else '(no text)'}"
```

Everything that makes a slide that slide goes into the hash: every shape name,
every text run in document order, the notes, the layout name and the byte size
of any embedded media. Position does not, which is the point. After a reorder
the same slides must still be present in a different order, and a fingerprint
that included the index could not say that. Keep the readable half alongside the
digest, because an error that reads `a1b2c3d4e5` tells nobody which slide went
missing. Where two slides hash the same, report that the comparison could not
tell them apart rather than banking the pass.

A copy on disk does not change this rule. A directory of downloaded files is a
re-download only if it was filled *after* the edit, so pull it again before
verifying rather than reusing the copy the plan was made against.
