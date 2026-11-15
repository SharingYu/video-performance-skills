# Shared Project Handoff and Recovery

Use a compact common record to carry the selected route across creative and production stages. Do not build a second production workbench or require every project to fill every field. The responsibilities below are human/agent-readable; they are not an invented backend API.

## Preserve the project and its evidence

| Record | Minimum useful responsibility |
|---|---|
| Brief | Route, intended result, audience/format, locked facts, allowed changes, scope and production constraints |
| Sources and coverage | Source IDs, URL or local identity, version/hash when available, locators and what was actually read/viewed |
| Canon and continuation | Character IDs/alias uncertainty, relationships, knowledge, rules, prop/physical states and unresolved setups relevant to the next unit |
| Creative artifacts | Current story/episode, script and shot versions, source/adaptation links, selected alternatives and unresolved questions |
| Execution and review | Actual backend inputs, task receipt, candidate/version, selected interval, evidence and scoped findings when these exist |

Keep original inputs private where appropriate. Do not copy a novel, reference film, family photo, credential or production receipt into a public example merely because the generic workflow is open source. Use original shareable substitutes for public demonstrations.

The [brief template](../assets/project-brief.md) is an adaptable starting artifact. The optional [project helper](../scripts/project_tool.py) records sources, read coverage and artifact state. Run its `--help` for the actual interface. Its index, successful command or completion flag does not prove semantic reading, accepted canon, a good script or generated media.

## Use the project helper when durable records are useful

Commands below are relative to this skill's directory. Substitute real input/output files. `scratch/` is a local work example, not material to publish:

```bash
python scripts/project_tool.py init --project scratch/my-project --route novel --title "Working title"
python scripts/project_tool.py source --project scratch/my-project --id S001 --kind novel --file novel.txt
python scripts/project_tool.py index --project scratch/my-project --source S001
python scripts/project_tool.py read --project scratch/my-project --source S001 --chunk C0001
python scripts/project_tool.py record --project scratch/my-project --artifact-id A001 --stage analysis --file source-notes.md --source-ids S001 --next-step "Inspect the next pending source chunk"
python scripts/project_tool.py status --project scratch/my-project
```

The `record` example requires an analysis file the assistant has actually written at `scratch/my-project/source-notes.md`, outside `inputs/`. Its `--file` is relative to the project; `source --file` is a local source path relative to the command's working directory or an absolute path. Use the returned source/chunk IDs, rather than assuming every input has the same structure. Select `--route reference` or `--route original` for the other routes. For a link, `source --kind video --url URL` records a pending source; it does not download or inspect the video. A real local file can later be attached to that source ID. Different source content uses a new ID, with the brief and affected canon/artifacts revised explicitly.

Text `index` creates mechanical UTF-8 chunks and candidate chapter navigation, not episodes or semantic facts. `read` verifies the source and returns one chunk with locators; its record is `tool_delivery_only`. The assistant still needs to inspect and analyze the content. `record` stores an artifact hash and source dependencies; it is not a creative or media approval. `status` reports mechanical `ready` / `stale` / `missing` records and chunks not yet returned, not a judgment that a novel has been understood or a film is complete.

Analysis/development artifacts may cite a URL-only source as explicitly `url_metadata_only` evidence. This lets an access brief retain its provenance while the video is unavailable. Script and later stages require real local source files for source dependencies. Attaching media later does not retroactively turn an earlier URL-only record into an observed-video analysis.

## Recover without inventing progress

On resume, inspect the actual project record, current source versions, completed artifacts and pending scope. Bring only relevant accepted context and the next reading/writing unit into the model's context. Save useful work as stages or units complete; do not depend on conversation memory alone.

If a source, script, selected candidate or edit point changes, identify affected descendants and recheck them. A changed source can make chapter locators and derived claims stale. A newly selected video out-point can invalidate the next shot's assumed entry state. Preserve history and show consequential changes instead of silently rewriting accepted facts.

Existing specialized tools may offer receipts or recovery. Check queue/history/output before resubmitting interrupted generation. Use current task scope and resource limits; an installed workflow or a historical budget is not a new rendering allowance.

## A common creative-to-production chain

1. **Story / episode:** who pursues what, the meaningful choices, changed state and audience payoff. Novel work retains source locations and labeled adaptation changes.
2. **Script:** visible action, purposeful dialogue or deliberate narration, scene entry/exit states and partner consequences.
3. **Assets:** stable identity versus outfit/state variants; scene geography, recurring props and the references needed for actual shots.
4. **Performance and shots:** event and protected-detail IDs, attention order, start state, key action/response, readable view and intended cutting opportunity.
5. **Backend work:** use the actual supported image/video/audio inputs. Identity, performance, style and space references have different roles. Do not claim an input was connected merely because a prompt mentions it.
6. **Selection and edit:** source length, requested generation length and adopted range stay separate. Bind actual candidate identity and use range to each shot; preserve corresponding sound when trimming or retiming.
7. **Review:** judge what the actual version and evidence establish; unresolved questions stay pending and missing duties return to the earliest useful repair stage.

An existing script, approved idea or finished asset can enter at its appropriate stage. Do not force an already complete unit back through every earlier template. Keyframes represent single moments; a meaningful intervening action still needs direction and evidence.

For narration-led comic video, establish narrator voice, panel timing, readable composition and necessary motion. For multi-character dialogue animation, additionally establish role/voice identity, dialogue performance, timing, lip sync when required and interaction coverage. Neither form proves the other's readiness.

## Five media review gates

| Gate | Question |
|---|---|
| Technical | Does the actual file/version/range/tracks match the delivery claim? |
| Action | Are the needed trigger, action change, contact and response actually present? |
| Continuity | Do identity, knowledge, space, props and outgoing/incoming states connect? |
| Highlight | Is the intended reveal, contrast, payoff or protected performance readable? |
| Rhythm | Does actual playback support anticipation, response and release without padding? |

For actual media use pass/fail/pending/not_applicable, with evidence and a reason for N/A. Required duties cannot disappear through N/A or a changed label. Written designs use supported/revise/pending within their own scope. Stills and descriptions can support poses and order without establishing real-time rhythm or audible quality.

Keep any source-placeholder preview distinct from generated footage. A mixed preview or partial task result is not a completed remake. Technical success cannot waive a missing action or payoff; a correct ending cannot establish an unseen middle.

## Report capability at the level actually established

Distinguish **method available**, **tool executable**, **text trial**, and **media trial**, recording the relevant task/version and limitations. These are evidence dimensions, not an automatic ranking: a working parser does not establish good serial writing, and one successful clip does not establish an entire season or every backend.

When execution is unavailable, deliver the concrete current artifacts and name the missing operation. When it is available and authorized, continue the requested production work. Do not substitute a capability checklist or routine per-shot confirmation for progress.
