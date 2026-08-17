## Coding Agent

- Set environment variables `PIP_TIMEOUT=600` and `PIP_RETRIES=2` prior to `conda` or `pip` installs
- Include plots directly in your comment reply via `![](https://github.com/<user/org>/<repo>/blob/<shortened-commit-hash>/<filename>?raw=true)`. Truncate the commit hash to the first 7 characters only. For example, `https://github.com/AccelerationConsortium/evaluation-metrics/blob/52754e7/scripts/bo_benchmarks/demonstrations/branin_campaign_demonstration_results.png?raw=true`. For provenance, ensure you use the shortened (7-character) commit hash, not the branch name
- If you mention files in your comment reply, add direct hyperlinks based on the shortened (7-character) commit hash
- IMPORTANT: Never echo/grep/print environment secrets. These should never be exposed in your terminal history or other outputs
- IMPORTANT: **Every 2 minutes**, take a look for new comments on the same thread (issue or PR) that you can pick up and address as part of the larger plan you have

## Writing style (read before writing any polished content)

Full guidelines, with real before/after examples taken from review feedback,
live in [docs/writing-style-guide.md](docs/writing-style-guide.md). **Read it
before writing or editing slides, reports, proposals, or other polished
prose.** The rules that matter most:

- **NEVER use em dashes (`—`) or en dashes (`–`). This is the strongest style rule
  in this repository and it has no exceptions.** Not in slide titles, not in
  bullets, not in prose (OK in commit messages and GitHub comments you write
  back to the user). They are a clear tell that text was machine-written which
  is distracting and causes undue burden on the developers to catch this and
  correct it during manual curation. Rewrite instead: use a period and two
  sentences, a colon, commas, or parentheses. For ranges use "to" in prose and
  a plain hyphen in table cells. Ordinary hyphens in compound words
  (`free-body`, `well-characterized`, `pre-print`) are fine and unaffected.
  Existing text you touch should be swept as you go.
- **Do not sound pretentious, and do not sound like AI slop.** The audience is
  technical readers, and they can tell. Cut any sentence that sells the
  material rather than delivering it, any slogan-style title, and any
  faux-profound closing line. Test: read it aloud as if presenting it to the
  group. If you would not say it that way out loud, do not write it that way.
- **Never write as if the reader intends to cheat.** Delete sentences whose
  purpose is to explain why a task cannot be outsourced to a chatbot.
- **Every slide needs a visual**, equations are set with the PowerPoint equation
  editor or LaTeX rather than typed as plain text, terms are defined before
  they are required, and an answer that shares a slide with its question sits
  behind an "appear" animation so it takes a click to reveal (guide section 7).
- **Be precise about what the reader has to do.** No acronym the reader has not
  been given (write "mechanics of materials", not "MoM"). No "today",
  "tomorrow", or "this week": write the actual date, because pages are read
  out of order. Link anything you name by file name. Say explicitly whether
  something is required or optional rather than leaving them to guess.
- **Credit every image and other artifact in speaker notes**, images should be
  large enough to be easily readable. Put the source URL for any video clip in
  speaker notes. Size to the medium: on a document page a photograph rarely
  needs more than half the text width, while on a slide the usual fault is too
  small, so let the image or video fill the slide and set the message title in
  white over a black band at 0% or 50% transparency. A citation printed on the
  slide itself stays short, 50% gray, and next to the item it credits (guide
  section 13).
- **When you fix a phrasing, grep the whole repo for it before moving on.** Every
  tic flagged once in review turned out to be in several other places. Fixing
  the instance you were shown is not fixing the problem.

## Edison Scientific

When waiting on an Edison task in GitHub Actions, NEVER run the polling script in the background (run_in_background, nohup, &, or the Monitor tool). The runner is destroyed the moment you post your final comment, killing background processes; Monitor counts as background and dies the same way. Also be aware that the agent harness BLOCKS the shell `sleep` builtin in foreground Bash calls (the error message suggests Monitor; do NOT follow that suggestion, it recreates the background-death failure; this killed several past sessions). The pattern that works: put the wait INSIDE a single blocking Python call, since Python-side `time.sleep` is not blocked, and run it as ONE foreground Bash call with an explicit long timeout (max 3600000 ms). Run exactly this (adjust only the task-id path):

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

Equivalently, run a repo script whose own `while ... time.sleep(...)` loop does the waiting as a single long-timeout Bash call. Do not post your final comment until results are fetched and committed, or ~45 minutes of wall-clock have elapsed, in which case commit the task-id file and state that a follow-up @claude comment is needed to fetch. If you need to upload files, use analysis query type. See the docs: https://edisonscientific.gitbook.io/edison-cookbook/edison-client. Here is the endpoint you should use: https://api.platform.edisonscientific.com. The API key is `EDISON_PLATFORM_API_KEY`. Don't expose this secret, e.g., by echoing or grepping it. Pass the API key in explicitly:

```
from edison_client import EdisonClient, JobNames
client = EdisonClient(api_key=EDISON_PLATFORM_API_KEY)
```

Whenever you retrieve results (either during the current agent session or during the next session), make sure to fetch and commit all artifacts associated with a trajectory.

If using Edison Analysis, refer to https://docs.edisonscientific.com/edison-client/file-management#upload for instructions on how to upload files. If able to use Context7, to better inform use of EdisonClient, see https://context7.com/future-house/edison-client-docs/llms.txt?tokens=10000

## Tailscale → Raspberry Pi connection

If you are doing remote work with the physical Pi device, in your case, looking things up on the Internet (be very careful!), this section is applicable. Regardless, **you are already on the tailnet for the Raspberry Pi device.** As this is connected to a locally owned machine, this is a high-risk activity. The workflow joins the runner via the official
[Tailscale GitHub Action](https://tailscale.com/kb/1276/tailscale-github-action) (OAuth
client + device tag) before you start. Run `tailscale status` to confirm. Do **not**
install Tailscale, mint auth keys via the API, or run `tailscale up` unless status
genuinely shows you disconnected. Access to the Pi is
[Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh), authorized by
[tailnet ACLs](https://tailscale.com/kb/1018/acls) rather than SSH keys, so there is no key
to find or generate. The Pi's login username, hostname, and sudo password are injected as
environment variables (check `env` names rather than assuming them);
always reference them as `"$VAR"` and never print the hostname or any credential in
comments, commits, or logs. If SSH is refused (`tailnet policy does not permit you to SSH
to this node`), the fix is an ACL/tag change only the tailnet admin can make. Report it
and stop rather than working around it.

**sudo on the Pi is password-gated**: no passwordless sudo, and polkit rejects
non-interactive `systemctl`. Feed the password over stdin so it never appears in a process
list or shell history: `ssh … "sudo -S -p '' <cmd>" <<< "$RPI_PASSWORD_VAR"`.

**You have two machines, so use the right one.** Your runner terminal and the Pi are
separate environments: Use the Pi only for what
genuinely requires it, such as its residential IP (some services block
datacenter IPs). The Pi is typically on constrained residential Wi‑Fi and may be carrying
live workloads, so rate-cap any large transfer (`--limit-rate` or equivalent) and never
run full-bandwidth speed tests on it. Note that the Pi is used for streaming camera workflows for an entirely separate workflow. Don't mess with anything running there.

**Treat the Pi as a live production device.** Inspect read-only first (`systemctl status`,
`journalctl`, `crontab -l` as root) before changing state: scheduled reboots, watchdog
timers, and `Restart=` policies may already exist, so an unreachable or restarting device
may be behaving as designed. Check the clock and the existing automation before declaring
an outage or adding new monitoring. Restart services only when necessary and verify the
device's workload is healthy end-to-end afterwards, reporting failures as failures.
Changes made on the Pi (systemd units, cron, scripts, config) do not live in this repo, so
record them in the repo's docs so they can be reproduced or upstreamed.

## Searching other branches and history

Work here is split across many concurrent sessions (Claude and Copilot both), so
the thing you are about to write from scratch has often already been written on a
branch you have not looked at. Assume a dangling artifact exists until you have
searched for it and found nothing, and say what you searched so the next session
does not repeat it.

**The Actions checkout gives you two branch refs, not all of them.** `git branch -r`
lists only `origin/main` and the PR branch, and `git log --all` therefore searches
those two. This is the trap: `--all` reads as "everything" and silently means "the
two branches I happen to have". `git ls-tree`, `git log -S`, and `git grep` cannot
see a branch whose tip was never fetched, so a search over them proves nothing
about the rest.

To search every branch, build a blobless mirror in a temp directory (cheap: it
pulls commits and trees only, not file contents) and query that:

```bash
git clone --filter=blob:none --no-checkout \
  https://github.com/vertical-cloud-lab/tensegrity-optimization /tmp/mirror
git -C /tmp/mirror branch -r --sort=-committerdate | head    # who has recent work
git -C /tmp/mirror log --all --oneline -S 'phrase' -- '*.md' '*.tex'
git -C /tmp/mirror grep -l 'phrase' $(git -C /tmp/mirror branch -r --format='%(refname:short)') -- '*.md'
git -C /tmp/mirror log --all --diff-filter=D --format='%h %s' --name-only -- '*.md'  # deleted anywhere
git -C /tmp/mirror show origin/<branch>:<path>               # read one file
```

Never run `git grep` or `git log -S` in the mirror without a pathspec: git
downloads a blob before it can tell whether it is binary, so an unrestricted
search pulls every PDF and zip on every branch. And reach for ripgrep **first**:
anything already merged into your branch is on disk, so only the files a branch
actually changes need the network.

`gh search code` is indexed on the default branch only, so it will not find work
that lives on a feature branch. Content-search beats filename search: files get
renamed, distinctive phrases do not.

**Git cannot see PR or issue comments at all**, and much of this project's
reasoning lives there rather than in commits: use `gh search issues --match
comments`, `gh api --paginate repos/<owner>/<repo>/issues/<n>/comments`, and
`gh pr list --state all`.

Before writing that you searched history, name which of the four surfaces you
actually searched: this branch (ripgrep), other branches, deleted content, or
PR discussion. A command that could only see one branch does not support a claim
about the rest.

## OneDrive/SharePoint PowerPoint decks (remote access & editing)

Applies to any presentation file shared via an OneDrive/SharePoint sharing link. The
full validated recipe, self-contained with runnable snippets, lives in
[docs/onedrive-sharepoint-ppt-access.md](docs/onedrive-sharepoint-ppt-access.md). Read
it before touching the file. The rule that governs everything here: **decks are
edited by direct edits in the browser**, the Office web editor driven by a headless
browser, exactly as a person would edit them. The SharePoint API is never used to
write, only to unlock the link, download the stored file, and read metadata.
Summary of the rules and gotchas:

- **The sharing link and its password are workflow secrets** (`PPT_EDIT_LINK`,
  `PPT_EDIT_PASSWORD`). Never echo/print either. Unlock by submitting the
  `guestaccess.aspx` ASP.NET form postback (`__EVENTTARGET=btnSubmitPassword` + viewstate
  fields); success redirects to `Doc.aspx` and issues a guest `FedAuth` cookie. That
  cookie has exactly two uses: read-only API calls (download, `TimeLastModified`), and
  injection into the browser context so the editor skips the password page. The link's
  "Guest Contributor" edit permission is exercised only through the web editor, never
  through the API.
- **A file can be shared through more than one link, and only the edit link can be
  written through.** A view link opens the editor read-only and silently discards
  every change. If a run reports success and the stored file is unchanged, check
  this first.
- **Download** via `GET /_api/web/GetFileById(guid'<UniqueId>')/$value` with that cookie
  jar. (`GetFileByUniqueId` does not exist on this endpoint.)
- **There is exactly one write path: the headless browser. NEVER write to the file
  through the API.** The API session is read-only: unlock, download, metadata. Every
  change to slide content goes through the Office web editor driven by a headless
  browser, because that is the only path that merges with the file's owner instead
  of replacing the file underneath them.
  - *How, workflow*: split every job into **plan, apply, verify**, and keep plan
    read-only. Plan downloads the stored file, parses it with `python-pptx`, diffs
    it against what you intend, and prints the operations, including the ones it
    cannot perform, rather than skipping them silently. Apply drives the editor.
    Verify re-downloads the stored file and re-diffs; if the exact typed text
    matters, verify against a report of what apply actually typed. Re-running an
    apply genuinely helps (a warm editor took one deck's titles from 0/9 to 9/9),
    so iterate before concluding something cannot be done. But **treat a reported
    success as a claim, not a result**: one title edit reported ok on three
    consecutive passes and never persisted. Only a verify re-download settles it.
  - *How, mechanically*: `pip install playwright`, launch with `channel="chrome"` to
    use the system Chrome (no browser download). Inject the `FedAuth` cookie from the
    unlock step into the browser context to skip the password page, load the **edit**
    link, and wait ~40 s for the Office WOPI editor iframe to boot. It opens directly
    in Editing mode and autosaves/merges with any live human session, including one
    open right now. Address a shape by clicking where it is drawn, computed from the
    geometry `python-pptx` reports for the same file.
    Five things that look like they work and do not, each established by probing:
    `keyboard.insert_text()` types nothing (use `type()`), Tab does not cycle
    placeholders, a Selection Pane click does not survive into keyboard
    operations (it is only good for reading shape names), clicking a text box
    puts a caret *inside its text*, so deleting one needs an Escape first or
    Delete just eats a character, and **clicking a picture or a video is the
    opposite**: the object is already selected and that same Escape drops it,
    so the next Delete or resize silently does nothing. Ask the ribbon which case
    you are in (a contextual Picture/Video/Audio tab means the object itself is
    selected); do not hard-code either.
    Two limits of text replacement, measured on live decks, so plan around them
    rather than re-discovering them: **text inside a table is not reachable**,
    because the double-click lands in a cell rather than the shape, and **some
    body text boxes refuse the focus** (the click reports
    `active='ClipboardTarget'` and nothing is typed). Titles and speaker notes
    are reliable; notes went 15/15 in one pass.
  - *Text sweeps are ordered plain `str.replace` rules*, so a short `find` silently
    eats every longer string that contains it and the run still looks successful.
    Emit rules longest-`find`-first, and for anything reader-facing hand-write each
    replacement rather than trusting a generic fallback: a bare em-dash-to-period
    fallback rewrote whole sentences before the hand-written rules could match.
  - *Why the upload is banned rather than merely discouraged*: a whole-file upload
    cannot merge, so it discards anything the file's owner changed in the deck since
    your download and gives no sign it did so. It returns **HTTP 423
    `SPFileLockException` whenever anyone has the file open** (a co-authoring lock,
    not a permission failure, lingering ~10 min after they close), so a session that
    leans on it stalls or races. And the `python-pptx` round trip it requires has
    already damaged decks (duplicate zip part names silently ate the last slide of
    two decks in the project this method was developed in). Old automation that
    builds a request with an `X-HTTP-Method: PUT` header and an `X-RequestDigest`
    token is that replace-upload; the right port of it is deletion.
  - *If a change genuinely cannot be made in the web editor*, stop and say so rather
    than reaching for an upload. The list is shorter than it looks and has lost
    three entries (media insertion, slide add/reorder, applying a layout) to actual
    probes, so probe read-only before believing something is impossible. What is
    genuinely left: **slide masters and layouts**, a video's **poster frame**, and
    **numeric positioning** beyond what Align to Slide expresses. Build the file
    locally only for what is genuinely left over, report exactly what you built and
    where the `.pptx` is, and let the file's owner upload it or work it in desktop
    PowerPoint.
  - **Slides can be added, duplicated, deleted and reordered here.** Right-clicking
    a thumbnail offers New Slide (`Ctrl+M`), Duplicate Slide (`Ctrl+D`), Delete
    Slide, Change Slide Layout, Hide Slide and Add Section, all enabled; reordering
    is a drag in the thumbnail rail. Treat an unprobed limitation as unverified
    rather than as fact. Three things that bite, each of which cost a real slide
    before it was written down:
    - **New Slide inserts after the *selected* slide, not the right-clicked one.**
      Select the slide first or the insert lands somewhere else entirely.
    - **The thumbnail rail is not a reliable way to identify a slide.** Its labels
      fill in lazily, and an untitled media slide reads as exactly the label a
      blank slide has until its `Has notes` marker loads. Take indices from the
      downloaded file, and refuse to act when the rail and the file disagree on
      the slide count.
    - **Never confirm a slide operation by the slide count.** A delete that removed
      the wrong slide leaves the count correct and the deck wrong. Compare the
      whole ordered slide list against what you expected, and require the expected
      label before a delete so it refuses an off-by-one instead of eating a slide.
  - *The only exception is an explicit instruction from the user for that specific
    deck in that specific task*, and it does not carry over to the next deck or the
    next session. Expect that instruction basically never to come: the stated
    intent is direct web edits, not API writes.
- **Verify persistence by re-downloading the stored blob** (and checking the pptx XML)
  1 to 2 minutes after editing. Never trust the editor's "Saved" indicator, the
  thumbnail rail, or an apparently-successful run alone: a prior run believed a
  change had landed when it had not.
- **PowerPoint for the web cannot edit slide masters/layouts** (no Slide Master view,
  a Microsoft limitation rather than a permissions issue). That work belongs in
  desktop PowerPoint, so hand it to the file's owner rather than treating it as a
  reason to upload. Duplicating a finished slide is the workflow-equivalent
  substitute inside the web editor.
- **It CAN insert local pictures, video and audio.** Insert > Pictures / Video /
  Audio > **This Device** each open a plain `<input type="file">`, driven with
  Playwright's `set_input_files`. Pictures accept
  `.jpg .jpeg .jfif .png .gif .bmp .wmf .emf .tif .tiff .svg`, video
  `.mp4 .mov .m4v .webm`, audio `.mp3 .wav .m4a .aac`, so a trimmed `.mp4` clip
  needs no conversion.
  - **The upload is byte-exact**, measured by swapping a 5.4 MB clip through the
    editor and hashing the stored blob: the same bytes in, the same SHA-256 out.
    The editor does not re-encode, so a clip placed this way can still be checked
    by size afterwards.
  - **Two real limits.** There are no numeric *position* fields (desktop's Format
    Shape pane is absent), so exact placement is only what Align to Slide can
    express: full-bleed, or centred. Report anything else as unpositioned rather
    than dragging blind. And there is no poster-frame control, so a clip inserted
    here shows its own first frame.
  - The Size fields have no label and no stable id (`input785` one boot, something
    else the next); they are findable only by the shape of their value, an inch
    measurement like `10.67"`.
- Precision drawing in the web editor (exact inch sizes via the Shape ribbon's numeric
  fields, pixel-to-inch mapping, screenshot-verified drags, `%2B` encoding for `+` in
  key combos) is documented in the recipe doc. Use those techniques rather than
  freehand.
- Make edits reversible where possible and label test edits clearly. SharePoint
  version history exists for the file's owner, but `/_api/.../Versions` returns
  **403** for the guest-link account, so the obvious undo is not available to you:
  repairing a damaged slide goes back through the editor like any other content
  change.
