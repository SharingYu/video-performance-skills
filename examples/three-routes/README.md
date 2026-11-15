# Three-route walkthroughs

These materials are original fictional text exercises. They do not represent an uploaded video, a published novel, an actual trend or a generated episode. Use your existing assistant; no rendering, cloud model account or GPU is needed.

## 1. Reference reconstruction

Give the assistant the [fictional observation input](../reference/input.md), and say:

> Use video-creation in reference mode. Rebuild this interaction with two adult coworkers rather than cats. Keep the event order, attempted concealment and partner response; the setting may change. Use only the supplied text as evidence. Deliver the adaptation brief and essential shot duties, not media.

If giving only an inaccessible URL instead, the correct first result is a source-access record and what remains unavailable, not invented descriptions of the clip.

## 2. Novel to short drama

Use [the original three-chapter prose](novel-source.md). In a repository clone:

```bash
python skills/video-creation/scripts/project_tool.py init --project scratch/novel-demo --route novel --title "The Third Strike"
python skills/video-creation/scripts/project_tool.py source --project scratch/novel-demo --id BOOK1 --kind novel --file examples/three-routes/novel-source.md
python skills/video-creation/scripts/project_tool.py index --project scratch/novel-demo --source BOOK1 --chunk-chars 600
python skills/video-creation/scripts/project_tool.py read --project scratch/novel-demo --source BOOK1 --chunk C0001
python skills/video-creation/scripts/project_tool.py status --project scratch/novel-demo
```

Ask the assistant to read further chunks as needed, then:

> Use video-creation in novel mode. Develop this source into a short serialized comic-drama proposal. Distinguish observed source facts, alias candidates and new adaptation choices. Do not map one chapter to one episode by default. Preserve a real result in each episode and carry what each character knows. Develop two candidate episodes and the first episode's script; stop before media generation.

The project tool verifies source identity and returns manageable text; it does not perform this creative task. Delivered chunks are not a completion score. Use `record` only after a real analysis/script file exists, and name the next step for resuming.

## 3. Original or mechanism adaptation

> Use video-creation in original mode. In a small plant shop, one adult employee wants a perfectly ordered display while an eager partner tries to help quickly and saves their own mistakes. Compare three different visible-comedy mechanisms, choose one and write the short script plus its protected performance beats. No dialogue, no fixed runtime. This is an original brief, not a verified trend.

For a trend-inspired request, provide dated references and the mechanism you want to investigate. Have the assistant inspect accessible material before claiming what happens; identify the changed goal, choice and consequence in the new story.

## What to compare

- Does the route match the user's intent rather than just the input type?
- Do source claims stay within actually available or read material?
- Does the novel proposal preserve character knowledge and causal setup across the episode boundary?
- Does the original mechanism belong to these characters and create a visible payoff?
- Are real production capabilities distinguished from a written plan?

The examples permit different creative solutions. They are not wording oracles or a claim of commercial appeal.
