# Production Handoff and Review

Carry an approved event through shots, prompts, selected media, and review. These are human- and agent-readable instructions, not a new backend API or an implemented automation layer.

## Minimal craft decisions

- **Story:** A goal leads to a choice; existing conditions explain the consequence. Return to the idea if a highlight depends on an arbitrary change of rules.
- **Performance:** Give attention a target and behavior a trigger. Keep the effects of an event into the next phase when relevant. Stillness can show assessment or restraint; do not add random activity to make a performer look alive.
- **Shot design:** Choose a view in which the critical behavior and necessary response can be read. Preserve eyelines, physical relationships, concealment, and information order. A motivated static view is sufficient when it serves the event.
- **Editing:** Find the point where preparation, contact, understanding, or intention changes. Remove redundant waiting while keeping the time needed to anticipate and read a consequence. Do not stretch shots to satisfy a fixed total duration.

## Trace protected details

Map event and detail IDs to existing shot responsibilities. If the host uses fields such as `protected_beats`, `required_events`, or `beat_ids`, reuse their meanings; otherwise a simple table is enough. Do not rename historical fields or assume a new note will be executed by a backend.

For example, a fictional detail `PE-01-A` may require a hand to stop after a cue while the character tries to keep their posture unchanged. Link it to the responsible shot and prompt behavior. Once a real candidate exists, link its actual version and adopted range, then cite the evidence that the pause and posture contrast are visible. Until then, media review remains pending; do not fill invented candidate IDs or hashes.

Every protected detail needs a readable carrier. Do not freeze the payoff into the opening frame or presume that a correct ending proves the middle. If the path is the point, plan intermediate performance or suitable motion references and verify the result. Do not automatically turn every phase into an editorial cut.

## Use available production tools honestly

State each reference's role: identity, performance, space, prop, style, or sound. Check what the chosen tool actually accepts and reads, including effective time window, resolution, and duration rules. Small expressions can disappear in low-resolution proxies. A video reference may preserve motion while changing identity; neither success implies the other.

Translate the card into the selected backend's supported language. Do not copy another platform's prompt fields, frame grid, fixed beat count, or human muscle codes. A card does not add precise pose, gaze, timing, or audio controls that the model lacks.

Separate source length, requested generation length, and selected edit length. Use actual source and output timestamps or frame rates. Keep picture and corresponding sound aligned. Distinguish event speed, camera speed, playback speed, and cut frequency. Normal-speed selection is the default; any deliberate retiming needs a reason and a check of both picture and sound.

For neighboring shots, inspect the actual adopted exit and entry states. Changing a candidate or edit point invalidates affected downstream assumptions. A backend's cached end state is not necessarily the state at the editor's chosen out-point.

## Five separate review gates

Use `pass`, `fail`, `pending`, or `not_applicable`, with evidence and a reason for any N/A. Required details cannot be exempted through N/A.

| Gate | Check | Example blocker |
|---|---|---|
| **Technical** | The actual version, file, timing, selected range, tracks, and export match the delivery claim | Wrong candidate, incomplete media, or undisclosed placeholder footage |
| **Action** | Relevant phases, trigger/reaction order, contact, balance, and recovery occur | A crucial correction is absent, contact is false, or a response anticipates its cue without intent |
| **Continuity** | Identity, props, knowledge, physical state, and necessary spatial relationships carry coherently | Unmotivated gaze/prop changes or an unexplained reset after a consequence |
| **Highlight** | Protected expression, response, information order, and payoff are actually perceptible | Plot action completes but the defining reaction is missing, hidden, too small, or revealed early |
| **Rhythm** | Real-time anticipation, peak, response, and release work without padding | A needed pause is removed, or repetitive slow activity fills unused duration |

Record the observer, method, actual version/range, evidence, and limits. Decoding establishes media integrity; stills and dense samples can support pose and sequence findings. They do not by themselves establish real-time rhythm or subjective audio quality. If the host cannot perform the needed observation, mark that part pending and complete the work it can perform. User feedback can add scoped evidence, but is not a mandatory per-shot approval gate.

For written exercises, judge the proposed contract or design; keep media gates pending until media exists and is observed. A complete card is not an automatic pass. If a required detail was not generated, do not remove it from the contract after the fact.

## Repair the earliest failure

Return a weak expectation or arbitrary choice to story design; an unreadable performance to staging; a missing generated phase to the input or shot approach; an available but omitted reaction to editing. Preserve work that already serves its purpose. Continue within the current scope and resource authorization; retrying or changing tools does not create new authorization.
