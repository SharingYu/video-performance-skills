# From idea to candidate review

This package covers performance direction inside a larger creative workflow. It provides a small shared contract between writing, shot design, generation and editing; it does not replace those tools.

## Start with an audience-facing event

For original work, establish what the character wants, the habitual way they pursue it, what obstructs it, and what their choice changes. Compare different comic or dramatic mechanisms before investing in elaborate shots. A surprise needs a readable expectation; a character's response makes it belong to that character.

For reference work, inspect the actual scene or observation record. Find the moment that changes what a viewer understands. Record what was seen and distinguish the directing interpretation. Scenery can change; a prop's function, a line of sight, or an information gap may be essential.

For a local file, the optional [video-observation skill](../skills/video-observation/SKILL.md) covers each shot, revisits uncertain time windows and supplies context-linked crops. Inspect the returned images before writing observation notes. Broad attention, body language, partner response and order are sufficient when that is the user's goal; a facial-measurement system is not required.

## Make the performance event card

Use the [six-part template](../skills/performance-direction/references/event-card.md). Assign stable IDs only to details that matter: a glance discovering the witness, an interrupted reach, an over-careful cover-up, or a partner's delayed response. A quiet character can be fully active through attention and a precise choice.

Protect the meaningful sequence, not a universal number of beats or seconds. An endpoint frame cannot establish whether a reaction happened in between.

## Turn the card into shot duties

For each shot, record the visible event it must carry, the starting state, the change and the intended cutting opportunity. Choose a camera distance where the relevant look or paw action can be read. Decide who holds attention and who yields it. Avoid revealing the answer in the first frame if discovery is the payoff.

Separate these relationships:

- Head/body orientation: what direction the body points.
- Eye attention: what the evidence actually shows the character looking at.
- Manipulation target: what the character touches or moves.

One does not prove the others. Generate keyframes as single moments, then use a motion prompt or reference for the intervening performance. Use actual candidate outpoints when continuing a physical state across a cut.

## Generate and select

Pass the card and shot duties to the user's existing backend. A simple independent shot may suit image-to-video; performance paths may benefit from a video reference or motion control if that backend supports it. These are choices to verify, not guaranteed capabilities of this skill.

Record generation length separately from editorial use. Select the interval that contains the useful action and its needed reaction; do not stretch a scene to meet an arbitrary runtime. Keep the current candidate identity, protected-beat IDs and actual selected interval together.

## Review five different things

| Gate | Question |
| --- | --- |
| Technical | Is the accessible candidate complete and readable? |
| Action | Did the necessary performance process actually happen? |
| Continuity | Does the adopted outgoing state connect to the next incoming state? |
| Highlight | Is the intended reveal, reaction or contrast visible and understandable? |
| Rhythm | Are anticipation, payoff and recovery supported by the moving sequence? |

For a written design, use supported / revise / pending with evidence. For actual media, use the skill's pass / fail / pending / not_applicable gates, with a reason for any N/A. Technical success cannot waive a missing highlight. Still frames or a description cannot settle playback rhythm. If the action is obscured, fix visibility; if a necessary response is absent, repair or replace the performance rather than relabeling the shot's purpose.

Editing may remove repeated waiting while preserving necessary anticipation and response. Sound can carry attention and contact, but cannot prove an unseen facial action occurred. Preserve audio synchronization when trimming or changing speed.

## Integrate without rebuilding your production stack

Keep normal screenwriting, asset, image, model-prompt and editing tools. Feed them the compact performance contract and return their actual evidence for review. Adapt backend fields locally; do not invent an API because an event card has a useful field.

See [production handoff](../skills/performance-direction/references/production-handoff.md) and the [roadmap](ROADMAP.md) for future adapters.
