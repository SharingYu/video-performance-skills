# Roadmap

Priorities are guided by reproducible creator problems. The sequence below is directional, not a release-date promise.

## v0.1 — usable skill and examples

- Self-contained reference and original workflows.
- Shared performance event card and production handoff.
- English core, Chinese onboarding, fictional text examples and counterexamples.
- Standard Skills installation and a thin optional Claude Code plugin wrapper.

## Next — demonstrate useful differences

- Original or contributor-owned video demonstrations showing a missing performance detail and its repair.
- Recorded assistant runs against the text cases, including failures and ambiguous evidence.
- Additional genres and acting styles: restrained drama, stylized animation, product storytelling and human ensembles.
- Better creator onboarding based on actual installation and task feedback.

## v0.2 — local observation tools

CPU media inspection, per-shot overview, timestamp-preserving windows, context-linked crops and observer-attested notes are now provided by `video-observation`. It uses the host's existing image perception and makes no model API calls. Broad body language and interactions are the default target.

Candidate interval comparison and task submission remain future adapters. Each needs a deterministic interface, documented limits and a local test before being exposed to an agent.

Use existing production backends where practical. A ComfyUI/H3 adapter could submit and recover authorized tasks with receipts; the skill itself should stay backend independent. Do not duplicate an entire workbench to add an event card.

## MCP when there are operations to expose

A future MCP server can expose useful media operations and production adapters. It should have real input/output behavior and a working local example. Wrapping instruction text in tool names is not the current priority.

## Evidence and adoption

Track reproducible uses, external examples, helpful failure reports, contributors and installation friction. Stars can indicate interest; they do not establish creative quality. We do not promise directory placement, algorithmic reach or viral results.
