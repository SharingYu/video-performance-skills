# Written evaluation cases

These ten cases are **new, fictional text fixtures**. They do not describe real people, films, recordings, model outputs or audience observations. The puppet presentation and bicycle-workshop ideas were written for this public set; no private production material is required.

Use them to inspect whether an agent protects meaningful behaviour, distinguishes evidence from interpretation, and hands unresolved questions back to the correct production stage. They are not a video-quality or creativity benchmark.

## Files

- [`cases.json`](cases.json): public requests, supplied fictional evidence and candidate proposals.
- [`oracle.json`](oracle.json): reviewer-only expectations, kept separate from the agent's input during a blind run.

Both files use `schema_version: 1`. `cases.json` contains `cases[]` with stable `id`, `mode`, `synthetic_text`, `request`, `evidence[]` and `candidate` fields. `oracle.json` contains `expected[]` keyed by the same IDs. These IDs identify fixtures, not real production candidates or media assets.

## Run a blind trial

1. Start a fresh agent context and load the repository's performance-direction skill. Give it one or more cases from `cases.json`. Do not provide `oracle.json`, an intended answer, previous judgements or author preferences.
2. Ask for a written-duty judgement, supporting evidence, unknowns, and the smallest useful next step. The agent may use a different phrasing or shot solution; it should stay inside the supplied task.
3. Save the actual response before inspecting the oracle. Record the skill version or commit, host/model if known, case IDs, supplied files and any tools used.
4. A reviewer then compares the reasoning with `oracle.json`. Record agreement, disagreement and limitations with concrete response passages. Revisions made after a hint belong in a separate record and are not another blind result.

An example instruction to the agent:

> Use the performance-direction skill to review case PD-03 in cases.json. Treat its evidence as supplied fictional text, not as footage you watched. Explain what is supported, what needs revision or remains unknown, and the next useful step. Do not generate media or invent media identifiers, timing or observations.

## What can be checked automatically

A file checker can verify JSON shape, required fields, unique IDs and the one-to-one correspondence between cases and oracle entries. Those checks establish that the fixture set is usable; they do not establish that an agent understood a performance.

Do not award behavioural success because a response repeats an expected word, uses a heading, contains `supported`, or reproduces the oracle. Read whether the response identifies the right causal relationship and keeps its evidence boundaries intact.

## Record reviewer and human evidence honestly

A useful result record includes:

| Field | Record |
|---|---|
| Trial context | Skill revision, host/model, case IDs and files supplied; whether the oracle was withheld |
| Actual output | The unchanged agent response, not only a summary or score |
| Reviewer | Human reviewer or separate agent, and what information they received |
| Finding | The relevant duty, the evidence cited, and the reason for agreement or disagreement |
| Observation scope | Supplied synthetic text only, unless an additional real-media study was actually performed |
| Follow-up | Proposed correction, any hinted revision, and unresolved questions |

If human viewers later watch an original rendered example, record the specific file/version, viewing context, question and actual feedback separately. Do not replace missing human or playback evidence with an agent's confidence, numeric self-rating, waveform statistics or a claim that a joke must land. No human confirmation is required for every ordinary production shot; these are evidence records for reported evaluations.

## Interpreting results

`supported`, `revise` and `pending` concern the written contract in a case. A plan can be supported while identity, anatomy, actual motion, normal-speed rhythm, audio and audience response remain untested. A missing observation is different from an observation that explicitly reports a missing action.

Multiple valid responses are possible. For example, an unsupported gaze claim can be corrected by revising the record while leaving the actual gaze pending. Likewise, a deliberately restrained face can work through attention and consequences without extra blinking.

Publish a small set of observed findings and failure examples rather than advertising a ten-case result as a model accuracy rate, a guaranteed improvement in creativity, or proof of commercial appeal.
