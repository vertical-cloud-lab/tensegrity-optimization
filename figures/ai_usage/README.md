# AI usage and cost analysis (issue #103)

Generated 2026-08-24 for [issue #103](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/103).

## Files

- `ai_usage_by_week.png`: weekly AI usage by project week (week 1 begins Mar 9, 2026, the repo creation date). Top panel is Claude cost in API-equivalent dollars, stacked by model. Middle panel is GitHub Copilot coding agent session counts. The band beneath maps weeks to calendar months.
- `ai_running_cost.png`: cumulative cost since repo creation. The Claude line is measured per-run cost; the Copilot AI-credits line is a duration-based estimate.
- `claude_runs.csv`: one row per executed Claude workflow run with the actual `total_cost_usd` reported by Claude Code in the Actions log, plus model, trigger actor, duration, and turn count.
- `copilot_sessions.csv`: one row per Copilot coding agent session and code review run, with wall-clock duration.

## Method

Claude costs are not estimates. Every executed run of the `Claude Code` and `Claude Code Review` workflows prints an execution result JSON that includes `total_cost_usd`, computed at run time from the then-current per-model API prices. Logs for all 292 non-skipped runs were downloaded via `gh api .../actions/runs/<id>/logs` and parsed; 268 runs contained a cost figure and the remaining 24 died during setup or exited without invoking Claude (cost $0, aside from a handful of cancelled partials).

Copilot token usage is not exposed by GitHub, so the AI-credits estimate prices each session's wall-clock duration at $0.10 to $0.20 per agent-minute. That range brackets the burn rates measured for this repo's own Claude agent runs, converted to Claude Sonnet-class AI-credit token rates ($3 in / $15 out per million tokens; GitHub's credit rates for Claude models match Anthropic API prices). Code review runs are priced at the denser rate measured for this repo's Claude code review runs.
