# Reading a Video Through Useful Views

Use the smallest set of views that answers the user's question. The target is readable acting and interaction, not exhaustive measurement. This workflow requires an existing assistant that can inspect images; exporting files alone does not provide that perception.

## Local tool entry points

Run from this skill's directory with a Python environment containing the bundled requirements. Replace example filenames, times, frame IDs, and view IDs with actual values from the current source and manifest. Use a separate output directory for each observation job; do not overwrite an existing manifest.

```bash
python scripts/video_observe.py inspect --video clip.mp4
python scripts/video_observe.py overview --video clip.mp4 --output observation/overview
python scripts/video_observe.py window --video clip.mp4 --start 12 --end 15 --fps 4 --output observation/window
```

- `inspect` returns source metadata without making a content judgment.
- `overview` proposes shot boundaries and selects each shot's beginning, middle, and final frame, removing duplicate selections in very short shots. It is a navigation pass, not a complete observation of the motion.
- `window` selects ordered real frames within `[start, end)`. Times are relative to the first presented video frame. Four frames per second is a starting view, not a guaranteed level of detail. `--fps 0` requests all native frames when needed; asking for a high rate does not create extra frames.

Each image-producing job writes `manifest.json`, original frame images, and readable sheets. The manifest binds frame IDs, actual presentation timestamps, source identity, and view IDs. Use the actual selections recorded there, not an assumed count from the requested sampling rate. Preserve the distinction between an original frame and a sheet used to navigate it.

To inspect a useful region:

```bash
python scripts/video_observe.py crop --manifest observation/window/manifest.json --frame-id f000000123 --box 200,100,800,900 --output observation/crop
```

`--box` is left, top, right, bottom on a normalized 0–1000 grid of the source image. Use an existing frame ID. The crop retains its source-frame and full-frame context relationship. A crop can make existing pixels easier to inspect; it cannot recover a detail the source does not show.

## Pass 1: make a shot and action map

Open the actual overview sheets using the host's image tool. Note the broad actor and prop relationships, the initial task, what changes, and the result. Include quiet shots; a restrained character may respond by following an object, halting a reach, or letting another character move first.

Some hosts drop image blocks when a response contains too many large images. Start with one or two sheets per response when needed, inspect truncation notices, and reopen any discarded image. Record only images actually delivered for inspection, not every attempted tool call.

The map should let a reader follow the scene without treating an interpretation as an observation. A compact record is enough:

| Evidence | Visible action and approximate attention | Partner response or result | Interpretation / question |
|---|---|---|---|
| Actual source and frame/view IDs | What the pictures support | What changes next | A qualified reading or an unresolved point |

Body and head orientation can support a broad direction, but do not invent a specific eye target. For example, “turns toward the partner; eyes unreadable” is useful evidence. “Watches the partner's hand” needs a readable relationship. Handling an object does not prove the eyes are on it.

## Pass 2: answer a specific missing link

Choose a question rather than requesting more frames indiscriminately:

- What prompted the character to turn or stop?
- Does the reach change target before or after the partner notices?
- What is the other character doing at the same moment?
- Does the body approach, pull back, or begin to follow and then settle?
- Is the final object position caused by an action, or shown only after a cut?

Request a short window with enough context before and after the change. Inspect ordered full-frame views first; use a closer image for a relevant face, hand/paw, posture, or prop if it helps. Keep the partner and target available in the matching full-frame view. A scene-wide motion score cannot establish that a quiet interaction is unimportant.

If the default view already answers the broad acting question, move on. Increase sampling only for a consequential uncertainty. If the source is occluded, too small, or missing the relevant interval, record that limit instead of inventing an action or repeatedly asking for the same view.

## Record what was actually inspected

After the host has opened the images, record only those actual view IDs:

```bash
python scripts/video_observe.py note --manifest observation/window/manifest.json --view-ids VIEW_ID --observer assistant --method static_sequence --kind observation --text "The extended arm stops before contact, then changes direction toward the tabletop." --event-id EVENT_ID
```

Take `VIEW_ID` from the manifest; a comma-separated list records several inspected views. `EVENT_ID` is an optional link to the user's event or shot records, not an invented media identifier. Use `--kind interpretation` for a reading such as “appears to cover an interrupted attempt,” and `--kind question` for an unresolved issue.

The note is an observer's declaration, not automatic proof that the model saw or correctly interpreted a picture. Do not use it to claim real-time playback, listening, full-source coverage, or a passed production review. Keep raw views and actual source references available for another observer to check.

`not_asserted_in_this_note_view_ids` lists views not named in that single note. It is not a cumulative coverage verdict. If combining journal entries, retain their observer, method, source and manifest identities and still label the result observer-attested.

## Verify and hand off

For an important disputed moment, let another observer inspect the material without a preferred answer. Compare the actual visible relationships and return to the source when useful. Do not use a second assistant's agreement as independent physical evidence.

Deliver a concise account of who looks or moves toward what, the action sequence, partner response, result, and remaining uncertainty. Keep the observable sequence separate from proposed intention and comedic interpretation. A source interval with unreadable eyes may still support a clear body-language finding.

Pass these findings to the selected performance or production workflow. Stable source/frame references let a protected beat point back to its evidence. A correct ending does not prove an unseen intermediate reaction occurred. Static sequence review leaves real-time timing and audio pending until an appropriate backend actually observes them.
