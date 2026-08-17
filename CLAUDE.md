## Coding Agent

- Set environment variables `PIP_TIMEOUT=600` and `PIP_RETRIES=2` prior to `conda` or `pip` installs
- Include plots directly in your comment reply via `![image name](https://github.com/<user/org>/<repo>/blob/<shortened-commit-hash>/<filename>?raw=true)`. Truncate the commit hash to the first 7 characters only. For example, `https://github.com/AccelerationConsortium/evaluation-metrics/blob/52754e7/scripts/bo_benchmarks/demonstrations/branin_campaign_demonstration_results.png?raw=true`. For provenance, ensure you use the shortened (7-character) commit hash, not the branch name
- If you mention files in your comment reply, add direct hyperlinks based on the shortened (7-character) commit hash
- IMPORTANT: Never echo/grep/print environment secrets. These should never be exposed in your terminal history or other outputs
- IMPORTANT: **Every 2 minutes**, take a look for new comments on the same thread (issue or PR) that you can pick up and address as part of the larger plan you have

## Writing style (read before writing any course content)

Full guidelines, with real before/after examples taken from review feedback on
this course's own material, live in
[docs/writing-style-guide.md](docs/writing-style-guide.md). **Read it before
writing or editing slides, Canvas pages, quizzes, homework, lab sheets, website
tutorials, or student template content.** The rules that matter most:

- **NEVER use em dashes (`—`) or en dashes (`–`). This is the strongest style rule
  in this repository and it has no exceptions.** Not in slide titles, not in
  bullets, not in Canvas descriptions, not in quiz stems, not in tutorial prose,
  (OK in commit messages and GitHub comments you write back to the
  user). They are a clear tell that text was machine-written which is distracting and causes undue burden on the developers to catch this and correct it during manual curation. Rewrite instead: use a
  period and two sentences, a colon, commas, or parentheses. For ranges use "to"
  in prose and a plain hyphen in table cells. Ordinary hyphens in compound words
  (`free-body`, `well-characterized`, `pre-class`) are fine and unaffected.
  Existing text you touch should be swept as you go.
- **Do not sound pretentious, and do not sound like AI slop.** The audience is
  juniors and seniors who have already passed statics and mechanics of materials,
  and they can tell. Cut any sentence that sells the material rather than
  delivering it (`Every phase hands the next one a physical artifact, that is what
  makes the project hard to fake`), any slogan-style slide title, and any
  faux-profound closing line. Test: read it aloud as if standing in front of the
  class. If you would not say it that way out loud, do not write it that way.
- **Never write as if students intend to cheat.** Delete sentences whose purpose is
  to explain why an assignment cannot be outsourced to a chatbot or to last year's
  team.
- **Every slide needs a visual**, equations are set with the PowerPoint equation
  editor (OMML via `scripts/ppt/omml.py`) or LaTeX in markdown rather than typed
  as plain text, terms are defined before they are required, and an answer that
  shares a slide with its question sits behind an "appear" animation so it takes
  a click to reveal (guide section 7).
- **Be precise about what the reader has to do.** No acronym a student has not
  been taught (write "mechanics of materials", not "MoM"). No "today",
  "tomorrow", or "this week": write the actual date, because Canvas pages are
  read out of order. Link anything you name by file name. Say explicitly
  whether something is required or optional rather than leaving them to guess.
  Nothing may assume the reader is sitting in the classroom: pre-class material
  is read alone, at a desk, before class.
- **Credit every image and other artifact in speaker notes**, images should be large enough to be easily readable. Put the source URL for any YouTube clip in speaker notes. Size to the medium: on a Canvas page a photograph rarely needs
  more than half the text width, while on a slide the usual fault is too small,
  so let the image or video fill the slide and set the message title in white
  over a black band at 0% or 50% transparency. A citation printed on the slide
  itself stays short, 50% gray, and next to the item it credits (guide section
  13). Do not add slides to, remove slides from, or
  reorder the `slide-graveyard` section; it is the instructor's manual backup
  area and its contents should be hidden.
- `python scripts/check_style.py` enforces the mechanical parts of this. Run it
  before committing. A clean run does not mean the writing is good, only that
  the regex-checkable rules pass.
- **When you fix a phrasing, grep the whole repo for it before moving on.** Every
  tic flagged once in review turned out to be in several other places:
  "Predict before/first" was called out on one slide and is in 20 places across
  6 deck specs and 7 website tutorials. Fixing the instance you were shown is
  not fixing the problem.

## Edison Scientific

When waiting on an Edison task in GitHub Actions, NEVER run the polling script in the background (run_in_background, nohup, &, or the Monitor tool) — the runner is destroyed the moment you post your final comment, killing background processes; Monitor counts as background and dies the same way. Also be aware that the agent harness BLOCKS the shell `sleep` builtin in foreground Bash calls (the error message suggests Monitor — do NOT follow that suggestion, it recreates the background-death failure; this killed several past sessions). The pattern that works: put the wait INSIDE a single blocking Python call — Python-side `time.sleep` is not blocked — and run it as ONE foreground Bash call with an explicit long timeout (max 3600000 ms). Run exactly this (adjust only the task-id path):

```bash
# ONE foreground Bash tool call with timeout: 3600000
python - <<'EOF'
import json, os, time
from edison_client import EdisonClient

client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
task_id = json.load(open("outputs/<...>/_task_id.json"))["task_id"]
while True:
    task = client.get_task(task_id=task_id, verbose=True)
    status = str(task.status)
    print("status:", status, flush=True)
    if status in {"success", "fail", "failed", "cancelled", "error"}:
        break
    time.sleep(240)
EOF
```

Equivalently, run a repo script whose own `while ... time.sleep(...)` loop does the waiting (e.g. `python scripts/explore_case_studies.py stage8-wait`) as a single long-timeout Bash call. Do not post your final comment until results are fetched and committed, or ~45 minutes of wall-clock have elapsed — in which case commit the task-id file and state that a follow-up @claude comment is needed to fetch. If you need to upload files, use analysis query type. See the docs: https://edisonscientific.gitbook.io/edison-cookbook/edison-client. Here is the endpoint you should use: https://api.platform.edisonscientific.com. The API key is `EDISON_PLATFORM_API_KEY`. Don't expose this secret, e.g., by echoing or grepping it. Pass the API key in explicitly:

```
from edison_client import EdisonClient, JobNames
client = EdisonClient(api_key=EDISON_PLATFORM_API_KEY)
```

Whenever you retrieve results (either during the current agent session or during the next session), make sure to fetch and commit all artifacts associated with a trajectory.

If using Edison Analysis, refer to https://docs.edisonscientific.com/edison-client/file-management#upload for instructions on how to upload files. If able to use Context7, to better inform use of EdisonClient, see https://context7.com/future-house/edison-client-docs/llms.txt?tokens=10000

## Tailscale → Raspberry Pi connection

If you are doing remote work with the physical Pi device, in your case, looking things up on the Internet (be very careful!), this section is applicable. Regardless, **you are already on the tailnet for the Raspberry Pi device.** As this is connected to a locally owned machine, this is a high-risk activity. The workflow joins the runner via the official
[Tailscale GitHub Action](https://tailscale.com/kb/1276/tailscale-github-action) (OAuth
client + device tag) before you start. Run `tailscale status` to confirm — do **not**
install Tailscale, mint auth keys via the API, or run `tailscale up` unless status
genuinely shows you disconnected. Access to the Pi is
[Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh), authorized by
[tailnet ACLs](https://tailscale.com/kb/1018/acls) rather than SSH keys — there is no key
to find or generate. The Pi's login username, hostname, and sudo password are injected as
environment variables (check `env` names rather than assuming them);
always reference them as `"$VAR"` and never print the hostname or any credential in
comments, commits, or logs. If SSH is refused (`tailnet policy does not permit you to SSH
to this node`), the fix is an ACL/tag change only the tailnet admin can make — report it
and stop rather than working around it.

**sudo on the Pi is password-gated** — no passwordless sudo, and polkit rejects
non-interactive `systemctl`. Feed the password over stdin so it never appears in a process
list or shell history: `ssh … "sudo -S -p '' <cmd>" <<< "$RPI_PASSWORD_VAR"`.

**You have two machines — use the right one.** Your runner terminal and the Pi are
separate environments: Use the Pi only for what
genuinely requires it — its residential IP (some services block
datacenter IPs). The Pi is typically on constrained residential Wi‑Fi and may be carrying
live workloads, so rate-cap any large transfer (`--limit-rate` or equivalent) and never
run full-bandwidth speed tests on it. Note that the Pi is used for streaming camera workflows for an entirely separate workflow. Don't mess with anything running there.

**Treat the Pi as a live production device.** Inspect read-only first (`systemctl status`,
`journalctl`, `crontab -l` as root) before changing state: scheduled reboots, watchdog
timers, and `Restart=` policies may already exist, so an unreachable or restarting device
may be behaving as designed — check the clock and the existing automation before declaring
an outage or adding new monitoring. Restart services only when necessary and verify the
device's workload is healthy end-to-end afterwards, reporting failures as failures.
Changes made on the Pi (systemd units, cron, scripts, config) do not live in this repo —
record them in the repo's docs so they can be reproduced or upstreamed.

### Searching other branches and history

Work on this course is split across many concurrent sessions, so the thing you are
about to write from scratch has often already been written on a branch you have not
looked at. Assume a dangling artifact exists until you have searched for it and found
nothing, and say what you searched so the next session does not repeat it.

**The Actions checkout gives you two branch refs, not 93.** `git branch -r` lists only
`origin/main` and the PR branch, and `git log --all` therefore searches those two. This
is the trap: `--all` reads as "everything" and silently means "the two branches I happen
to have". `git ls-tree`, `git log -S`, and `git grep` cannot see a branch whose tip was
never fetched, so a search over them proves nothing about the other 91.

**Do not fetch branch tips one at a time.** That was the old advice here and it is
backwards: measured on a runner, the commit and tree graph for **all 93 branches is
1.2 MB and 0.96 s**, because effectively all of this repository's weight is blobs
(decks, figures, PDFs). Grab the whole graph and query it:

```bash
python scripts/find_in_branches.py branches             # who has unmerged work
python scripts/find_in_branches.py files '<regex>'      # path search, all 93 branches
python scripts/find_in_branches.py deleted '<regex>'    # deleted anywhere in history
python scripts/find_in_branches.py grep '<phrase>'      # content search
python scripts/find_in_branches.py show <branch> <path> # read one file
```

It builds a blobless mirror in a temp directory, so it works in the shallow checkout
and never touches the working tree. Full recipes, the measured cost of every
operation, and the recommended `claude.yml` change are in
[docs/searching-other-branches.md](docs/searching-other-branches.md).

Two traps that cost real time. Never run `git grep` on another branch without a
pathspec: git downloads a blob before it can tell whether it is binary, so an
unrestricted search pulls every `.pptx` and `.png` in the tree (about 7 minutes
versus 0.03 s limited to `*.md`). And reach for ripgrep **first**: anything already
merged into your branch is on disk, so only the files a branch actually changes need
the network.

`gh search code` is indexed on the default branch only, so it will not find work that
lives on a feature branch. Content-search beats filename search: files get renamed,
distinctive phrases do not.

**Git cannot see PR or issue comments at all**, and much of this course's reasoning
lives there rather than in commits: use `gh search issues --match comments`, `gh api
--paginate repos/$GH_REPO/issues/<n>/comments`, and `gh pr list --state all`.

Before writing that you searched history, name which of the four surfaces you actually
searched: this branch (ripgrep), other branches, deleted content, or PR discussion. A
command that could only see one branch does not support a claim about 93.

## OneDrive/SharePoint PowerPoint decks (remote access & editing)

Applies to any presentation file shared via an OneDrive/SharePoint sharing link. The
full validated recipe with working code lives in
[docs/onedrive-sharepoint-ppt-access.md](docs/onedrive-sharepoint-ppt-access.md). Read
it before touching the file. Summary of the rules and gotchas:

- **Password-protected links**: the link password is injected as a workflow secret
  (e.g. `PPT_EDIT_PASSWORD`). Never echo/print it. Unlock by submitting the
  `guestaccess.aspx` ASP.NET form postback (`__EVENTTARGET=btnSubmitPassword` + viewstate
  fields); success redirects to `Doc.aspx` and issues a guest `FedAuth` cookie that
  authorizes the SharePoint REST API as "Guest Contributor" (view + download + edit).
- **Download** via `GET /_api/web/GetFileById(guid'<UniqueId>')/$value` with that cookie
  jar. (`GetFileByUniqueId` does not exist on this endpoint.)
- **There is exactly one write path: the headless browser. NEVER edit a deck through
  the REST API.** The REST session is read-only. Use it to unlock the link, download
  the file, and read `TimeLastModified`. Every change to slide content goes through
  the Office web editor driven by a headless browser, because that is the only path
  that merges with the file's owner instead of replacing the file underneath them.
  - *How, for content edits*: **do not hand-drive the editor, use
    `scripts/ppt/browser_edit_deck.py`.** It runs in three stages and the split is
    the point: `plan` is read-only (download the stored deck, diff it, print the
    operations), `apply` drives the editor, `verify` re-downloads and re-diffs.
    Sources of truth are combinable: `--rules FILE` for text substitutions across
    every deck (the sweep case: a phrase banned in review, fixed everywhere),
    `--from-spec` to reconcile titles and speaker notes against
    `scripts/ppt/specs/L<N>.json`, and `--clips` to reconcile embedded video
    against `scripts/ppt/clips.yaml`, which uploads a re-cut clip and removes
    the cut it replaces. It also removes shapes that a repeated `build()` has
    stacked on top of each other. Always run `plan` first and read it; always
    run `verify` after, and `verify --against` the `apply --json` report if the
    exact typed text matters.
  - *How, mechanically* (`scripts/ppt/web_editor.py`, if you need to do something
    the tool above does not cover): `pip install playwright`, launch with
    `channel="chrome"` to use the system Chrome (no browser download). Inject the
    `FedAuth` cookie from the unlock step into the browser context to skip the
    password page, load the **edit** link (not the public view-only one, which
    opens read-only and swallows every change), and wait ~40 s for the Office WOPI
    editor iframe to boot. It opens directly in Editing mode and autosaves/merges
    with any live human session, including one open right now. Address a shape by
    clicking where it is drawn, computed from the geometry `python-pptx` reports.
    Five things that look like they work and do not, each established by probing:
    `keyboard.insert_text()` types nothing (use `type()`), Tab does not cycle
    placeholders, a Selection Pane click does not survive into keyboard
    operations (it is only good for reading shape names), clicking a text box
    puts a caret *inside its text*, so deleting one needs an Escape first or
    Delete just eats a character, and **clicking a picture or a video is the
    opposite**: the object is already selected and that same Escape drops it,
    so the next Delete or resize silently does nothing. `select_at` asks the
    ribbon which case it is in; do not hard-code either.
  - *Why the REST upload is banned rather than merely discouraged*: `POST .../$value`
    with `X-HTTP-Method: PUT` + `X-RequestDigest` from `/_api/contextinfo` is a
    **whole-file replace**. It cannot merge, so it discards anything the instructor
    changed in the deck since your download and gives no sign it did so. It returns
    **HTTP 423 `SPFileLockException` whenever anyone has the file open** (a
    co-authoring lock, not a permission failure, lingering ~10 min after they close),
    so a session that leans on it stalls or races. And the python-pptx round trip it
    requires has already damaged decks in this repository: duplicate zip part names
    silently ate the last slide of L21 and of L33, and a concurrent rebuild shipped
    L4 with two identical cold-open slides.
  - *If a change genuinely cannot be made in the web editor*, stop and say so rather
    than reaching for REST. The list is shorter than it looks, so check it against
    `scripts/ppt/probe_ribbon.py` and `scripts/ppt/probe_slide_ops.py` before
    believing something is impossible. What is genuinely left is **slide masters
    and layouts** (no Slide Master view in PowerPoint for the web). **Adding,
    duplicating, deleting and reordering slides are not on that list any more,
    and neither is embedding a local clip**, see the notes below. Build the file
    locally only for what is genuinely left over, report exactly what you built
    and where the `.pptx` is, and let the instructor upload it or work it in
    desktop PowerPoint. `browser_edit_deck.py plan` prints these as `UNSUPPORTED`
    rather than skipping them silently, so a spec change needing one is visible
    instead of looking applied.
  - **Slides can be added, duplicated, deleted and reordered here.** Right-clicking
    a thumbnail offers New Slide (`Ctrl+M`), Duplicate Slide (`Ctrl+D`), Delete
    Slide, Change Slide Layout, Hide Slide and Add Section, all enabled; reordering
    is a drag in the thumbnail rail. `web_editor.py` exposes `add_slide_after`,
    `duplicate_slide`, `delete_slide` and `move_slide`. This is the third
    "impossible" claim in this file to fall to an actual probe, so treat an
    unprobed limitation here as unverified rather than as fact.
    Three things that bite, each of which cost a real slide before it was written
    down:
    - **New Slide inserts after the *selected* slide, not the right-clicked one.**
      Select the slide first or the insert lands somewhere else entirely.
    - **The thumbnail rail is not a reliable way to identify a slide.** Its labels
      fill in lazily, and an untitled media slide reads as exactly the label a
      blank slide has until its `Has notes` marker loads. Take indices from the
      downloaded file, and refuse to act when the rail and the file disagree on
      the slide count.
    - **Never confirm a slide operation by the slide count.** A delete that removed
      the wrong slide leaves the count correct and the deck wrong. Compare the
      whole ordered label list against what you expected, and pass `expect=` to
      `delete_slide` so it refuses an off-by-one instead of eating a slide.
  - *The only exception is an explicit instruction from the user for that specific
    deck in that specific task*, and it does not carry over to the next deck or the
    next session. `upload()` in `scripts/ppt/onedrive_ppt.py` and its callers
    (`push_decks.py`, `rebuild_deck.py`, `insert_clip_slide.py`,
    `normalize_sections.py`) are that banned path. Do not point them at a live deck
    on your own initiative, however convenient it looks or however many previous
    sessions did.
- **Verify persistence by re-downloading the stored blob** (and checking the pptx XML)
  1 to 2 minutes after editing. Never trust the editor's "Saved" indicator or an
  apparently-successful upload alone: a prior run believed an upload had landed when
  it hadn't.
- **PowerPoint for the web cannot edit slide masters/layouts** (no Slide Master view,
  a Microsoft limitation rather than a permissions issue). That work belongs in
  desktop PowerPoint, so hand it to the instructor rather than treating it as a
  reason to REST-upload. Duplicating a finished slide is the workflow-equivalent
  substitute inside the web editor.
- **It CAN insert local pictures, video and audio, and that is now wired up.**
  Insert → Pictures / Video / Audio → **This Device** each open a plain
  `<input type="file">`, driven with Playwright's `set_input_files`. Pictures
  accept `.jpg .jpeg .jfif .png .gif .bmp .wmf .emf .tif .tiff .svg`, video
  `.mp4 .mov .m4v .webm`, audio `.mp3 .wav .m4a .aac`. `.mp4` is what
  `scripts/ppt/fetch_clips.py` produces, so a trimmed clip needs no conversion.
  Re-check with `python scripts/ppt/probe_ribbon.py L1` (read-only, does not
  modify the deck) rather than assuming this has gone stale. An earlier version
  of this file asserted the opposite; it had never been probed.
  - **The upload is byte-exact.** Measured 2026-08-15 by swapping L2's torsion
    clip through the editor and hashing the stored blob: 5,413,648 bytes in,
    the same SHA-256 out. The editor does not re-encode, so a clip placed this
    way is the file `clips.yaml` describes.
  - **Two real limits.** There are no numeric *position* fields (desktop's
    Format Shape pane is absent), so exact placement is only what Align to
    Slide can express: full-bleed, or centred. `place_selected` reports
    `positioned: False` for anything else instead of dragging blind. And there
    is no poster-frame control, so a clip inserted here shows its own first
    frame rather than the `poster_at` still `build_deck_from_spec` sets.
  - The Size fields have no label and no stable id (`input785` one boot,
    something else the next); they are findable only by the shape of their
    value, an inch measurement like `10.67"`.
- Precision drawing in the web editor (exact inch sizes via the Shape ribbon's numeric
  fields, pixel↔inch mapping, screenshot-verified drags, `%2B` encoding for `+` in key
  combos) is documented in the recipe doc. Use those techniques rather than freehand.
- Make edits reversible where possible (SharePoint version history exists) and label test
  edits clearly.
