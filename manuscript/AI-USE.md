# Use of AI tools in this study

This file is the inventory that the manuscript's Acknowledgment and its
"Use of AI Tools" subsection (Materials and Methods) point to. AI tools were
used throughout the project, under the authors' direction and with human
review and edits at every step, for text and figure generation, methodology,
code, analysis and testing. The manuscript has been reviewed in full by the
human authors, who take responsibility for it.

Compiled 2026-10-27 from the git history of every branch of this repository
(a blobless mirror of all 95 branches, 1,428 commits) and from the issue and
pull-request comments. How to refresh it is at the end.

## Tools, models, access and dates

| Tool | Models / version | Access | Dates | Evidence |
|---|---|---|---|---|
| Claude Code (Anthropic) | Claude Opus 4.8 (2026-06-30, one commit), Claude Fable 5 (2026-07-01 to 2026-09-25), Claude Opus 5 (2026-08-04 to 2026-09-25), Claude Opus 5.5 (2026-09-25 to 2026-10-27), Claude Fable 5.1 (2026-10-13 to 2026-10-25) | GitHub Actions, through [`anthropics/claude-code-action@v1`](https://github.com/anthropics/claude-code-action) (workflow `.github/workflows/claude.yml`, added 2026-06-29), started by an `@claude` comment from a lab member. Claude Code 2.1.312 on the 2026-10-27 runner | 2026-06-29 to 2026-10-27 | 947 commits authored by `claude[bot]`; model from each commit's `Co-Authored-By: Claude <model>` trailer (403 Fable 5, 187 Fable 5.1, 180 Opus 5.5, 46 Opus 5, 1 Opus 4.8) |
| Claude Code (Anthropic) | Claude Opus 5.5, including its 1M-context variant | Command-line interface, in local sessions run by S. G. Baird and pushed from his account | 2026-09-26 to 2026-10-27 | 7 commits authored by S. G. Baird with a `Co-Authored-By: Claude Opus 5.5` trailer, mostly workflow and repository-instruction changes |
| GitHub Copilot coding agent | Claude Opus 4.6 (2026-03-10 to 2026-05-21), Claude Opus 4.7 (2026-04-20 to 2026-05-26), Claude Opus 4.8 (2026-05-28 to 2026-07-20), and once each Claude Haiku 4.5, Claude Sonnet 4.6, Claude Fable 5 and MAI Code 1 Flash | GitHub, started by an `@copilot` mention or issue assignment | 2026-03-09 to 2026-07-20 | 334 commits authored by `copilot-swe-agent[bot]`. Its commits carry no model trailer, so the models come from the `@copilot+<model>` selectors in lab members' comments (194 such selectors) |
| GitHub Copilot CLI | model not recorded | Command-line interface, local sessions run by S. G. Baird | 2026-06-09 | 4 commits with a `Co-authored-by: Copilot` trailer, including the first manuscript scaffolding (`262e0a6`, `447f64b`) |
| GitHub Copilot Autofix | model not recorded | GitHub code scanning | 2026-03-12 to 2026-05-20 | 4 commits with a `Co-authored-by: Copilot Autofix powered by AI` trailer |
| Edison Scientific platform | data-analysis agent (`job-futurehouse-data-analysis-crow-high`), literature agent (`job-futurehouse-paperqa3-high`, "LITERATURE_HIGH") and precedent search | API (`edison-client`), called from Claude Code and Copilot sessions | 2026-05-08 to 2026-09-21 | Task records and outputs in [`edison-trajectories/`](../edison-trajectories/): five rounds of mock JMD peer review, five Socratic review rounds, the pre-registered adversarial review of the objective choices (task `3e398131`), figure feedback, citation classification and DOI verification |
| faster-whisper (speech-to-text) | `medium.en` | Run on the Actions runner by Claude Code | 2026-09-08 and 2026-09-29 | Transcripts of the co-authors' recorded reviews, in [`reviews/`](../reviews/) |

The first and second Claude rows differ only in access route. Model names are
exactly as the trailers and selectors give them.

## Automated sessions on the manuscript pull request (#76)

Claude Code Action runs whose results were posted to
[PR #76](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/76),
in order. Each run's prompt is the triggering comment on that PR.

| Date (UTC) | Started by | Run |
|---|---|---|
| 2026-08-22 | sgbaird | [32587705182](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/32587705182) |
| 2026-08-22 | sgbaird | [32599001244](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/32599001244) |
| 2026-08-23 | sgbaird | [32611272327](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/32611272327) |
| 2026-09-08 | sgbaird | [34250589809](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/34250589809) |
| 2026-09-15 | sgbaird | [34947671717](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/34947671717) |
| 2026-09-15 | sgbaird | [35029205290](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/35029205290) |
| 2026-09-22 | sgbaird | [35788421607](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/35788421607) |
| 2026-09-22 | sgbaird | [35790053739](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/35790053739) |
| 2026-09-22 | sgbaird | [35792102012](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/35792102012) |
| 2026-09-22 | sgbaird | [35792261355](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/35792261355) |
| 2026-09-22 | sgbaird | [35793157060](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/35793157060) |
| 2026-09-29 | me-madsen | [36601051026](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/36601051026) |
| 2026-10-10 | sgbaird | [38081229925](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/38081229925) |
| 2026-10-11 | sgbaird | [38113753615](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/38113753615) |
| 2026-10-23 | achris0520 | [39985743091](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/39985743091) |
| 2026-10-23 | achris0520 | [40010411709](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40010411709) |
| 2026-10-24 | sgbaird | [40066982733](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40066982733) |
| 2026-10-24 | sgbaird | [40126421965](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40126421965) |
| 2026-10-25 | sgbaird | [40148662172](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40148662172) |
| 2026-10-27 | sgbaird | [40597981027](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40597981027) |
| 2026-10-27 | sgbaird | [40597984199](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40597984199) |
| 2026-10-27 | sgbaird | [40597986643](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40597986643) |
| 2026-10-27 | sgbaird | [40597990730](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40597990730) |
| 2026-10-27 | sgbaird | [40597994432](https://github.com/vertical-cloud-lab/tensegrity-optimization/actions/runs/40597994432) |

The five runs of 2026-10-27 are the parallel requests A to E that split the
post-review edits. Before 2026-08-22 the Copilot coding agent worked the
manuscript branch. It opened PR #76 on 2026-06-12 by merging the 43 commits of
the earlier manuscript branch (PR #20), which it had also written, and it
replied on PR #76 on 2026-06-12, 2026-06-13 and 2026-06-14.

## Refreshing this inventory

```bash
git clone --filter=blob:none --no-checkout \
  https://github.com/vertical-cloud-lab/tensegrity-optimization /tmp/mirror
# models and dates from the commit trailers
git -C /tmp/mirror log --all --format='%(trailers:key=Co-authored-by,valueonly,separator=%x0A)' \
  | sort | uniq -c | sort -rn
git -C /tmp/mirror log --all --format='%aI %h %an' --fixed-strings --grep='Claude Opus 5.5' | sort
# commit authors (claude[bot], copilot-swe-agent[bot], people)
git -C /tmp/mirror log --all --format='%an' | sort | uniq -c | sort -rn
# Copilot coding-agent model selectors and the PR #76 run links
gh api --paginate "repos/vertical-cloud-lab/tensegrity-optimization/issues/comments?per_page=100" \
  --jq '.[] | [.created_at, .user.login, .html_url, .body] | @tsv' > comments.tsv
grep -o -E '@copilot\+[a-z0-9.-]+' comments.tsv | sort | uniq -c
grep -P '/pull/76#' comments.tsv | grep -o -E 'actions/runs/[0-9]+' | sort -u
```
