# Performance and Highlight Event Card

Create a card for a moment with an audience function, not for every blink or shot. An event may span shots; a shot may serve several related events. Use stable IDs so protected details can be traced through production.

## Six groups

| Group | Record |
|---|---|
| **Audience expectation and payoff** | What the audience knows, expects, or misreads; what changes that understanding; what reward or consequence lands. A hook and its payoff may occur at different moments. |
| **Observable performance chain** | Relevant trigger, attention, choice, preparation, contact or peak, reaction, and settling. Select only the phases this event needs. Separate visible behavior from a proposed intention. |
| **Protected details** | The few details whose removal would damage the meaning or appeal. Give each a sub-ID, an observable criterion, required order or overlap, and the effect lost if omitted. Separate optional polish. |
| **Attention handoff** | Who should be watched first, who receives attention next, the transfer cue, and the window in which the important action can be read. A single-focus event may need no handoff. |
| **Allowed changes and necessary relationships** | Distinguish replaceable scenery or styling from required identity, eyeline, distance, concealment, prop function, physical conditions, and information order. Preserve user-locked facts. |
| **Evidence or original intent** | What was actually observed, where and how; what is interpretation; what is a new creative choice; what remains unknown. |

## Compact template

```markdown
# Event PE-01 — title
Mode: reference / original
Version and scope:
Performers, form, and style:
User-locked facts:

## 1. Audience expectation and payoff
Known or misread:
Expected result:
Highlight and consequence:

## 2. Observable performance chain
| Phase | Performer | Trigger | Body facing | Head facing | Visible gaze target | Handled object | Action/order | Interpretation or intent | Evidence/location |
|---|---|---|---|---|---|---|---|---|---|

## 3. Protected details
| Detail ID | Observable requirement | Order/overlap | What is lost if omitted |
|---|---|---|---|
Optional polish:

## 4. Attention handoff
From → to; cue; readable window; competing activity:

## 5. Allowed changes and necessary relationships
May change:
Must remain true:

## 6. Evidence or original intent
Material/version and observation method:
Observed facts:
Interpretation:
Proposed creative choices:
Unknown or not yet observed:
Current delivery boundary:
```

Adapt the presentation if a table becomes cumbersome, but keep the six responsibilities. Omit irrelevant channels rather than filling them with invented actions. Unknown eye direction stays unknown even when head direction or a manipulation target is clear.

## Evidence precision

- Record the actual source and version. Use file hashes or host asset IDs when available; never invent them.
- If frames are known, use zero-based half-open ranges `[in_frame, out_frame)`. The last displayed frame is `out_frame - 1`. Preserve each source's own frame rate or timestamps; do not transfer reference frame numbers to generated footage with a different time base.
- If timing is unknown, use relative order and mark timing as unknown. Original timing is a design proposal, not an observation.
- A transcript, still, user description, or article is evidence of that material only. Do not present it as full-video observation. Still frames can support poses and visible facts without proving real-time rhythm.
- Preserve meaningful overlaps and contrasts in speed. The phase list is not a compulsory sequence of cuts or a fixed emotional arc.
