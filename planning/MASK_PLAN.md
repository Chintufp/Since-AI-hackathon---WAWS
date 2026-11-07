# Mask current plan

Updated 7 November 2026. **Current priority: readable output for approximately 100-word English messages within the under-19-hour demo deadline.** Use stable `[PERSON_1]` references inside useful text, preserve surrounding relationships, and remove genuinely unnecessary sections coherently. Cover everyday goals beyond health. Quality takes priority over speed/size; most work happens on this computer with cloud training available. The immediate demo profile in the authoritative plan overrides the longer-term ordering below.

- [Authoritative local model build plan](LOCAL_MODEL_PLAN.md)
- [Current implementation brief](CLAUDE_BUILD_BRIEF.md)
- [Consumer product background](PROMPT_PRIVACY_PIVOT.md)
- [Existing application](../mask/README.md), [legacy ML pipeline](../mask/ml/README.md), [benchmark adapter](../mask/bench/README.md)

The immediate milestone is an improved local text pipeline, a minimal review UI and separate rehearsal/robustness results. Familiar training patterns are acceptable for a rehearsed demo, but do not establish held-out generalisation. The full-release deliverable remains a trained offline model bundle, local API/CLI, text and spreadsheet adapters, independent held-out evidence, and measured size/latency/memory. Full release requires the model plan's quality, fidelity, coverage and file-integrity gates.

Try both architectures: **A, our own small feature-based classifier**, and **B, a compact pretrained English encoder with task-specific heads**. Use the same data/splits, deterministic actions, file adapters and release gates. Measure detection and treatment separately and together. Select on validation evidence for privacy, fidelity, coverage, size and speed, then confirm on held-out test data. MiniLM is a challenger, not a commitment. Preserve existing infrastructure and legacy provenance; do not rely on agent agreement or historical institutional scores as validation.

A minimal review UI is now in scope. Future provider integration should carry the fixed placeholder-use instruction in the authoritative plan; original values and alias maps stay local. Broad UI redesign, browser extensions, additional languages and institutional expansion remain deferred. Prioritise encoder improvements for the demo while retaining the custom comparison; neither existing pilot is a validated release.
