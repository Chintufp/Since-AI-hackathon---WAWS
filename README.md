# Mask

**Useful AI conversations. Less unnecessary personal disclosure.**

**Current priority:** a readable local privacy demo for approximately 100-word English messages within the user's under-19-hour deadline. Prefer stable person labels inside useful text, and remove genuinely unnecessary sections cleanly. Quality comes before size/speed optimisation. Follow the [current demo profile and longer-term model plan](planning/LOCAL_MODEL_PLAN.md); a minimal review UI is in scope, while full release criteria remain unachieved. Work is centred on this computer, with cloud compute and AI-assisted synthetic data generation available.

The plan requires a fair comparison of our custom feature-based classifier and a pretrained-encoder model. Both use the same task data, transformations and release gates; choose the deployed model from measured validation quality, footprint and latency, with independent final confirmation.

Mask's current direction is a hackathon prototype of local prompt-protection middleware: paste context, ask a question, review faithful semantic substitutions, and send only the protected request to an external AI.

The existing application already processes CSV datasets in the browser with detection, transformation proposals, editable previews and exact export. The consumer prompt/send path is the next build, not an implemented capability claim. A development learned selector loads, but has no held-out validation/test results for the new task.

## Start here

- [Current Claude implementation brief](planning/CLAUDE_BUILD_BRIEF.md)
- [Local model architecture, training and readiness criteria](planning/LOCAL_MODEL_PLAN.md)
- [Pivot assessment, architecture and prioritised work](planning/PROMPT_PRIVACY_PIVOT.md)
- [Run the existing application](mask/README.md)
- [Existing ML pipeline](mask/ml/README.md)
- [Benchmark adapter](mask/bench/README.md)
- [Challenge materials](MATERIALS.md)

## Delivery scope

First improve the local message path and connect a minimal review demonstration. Use stable references inside useful text and clean removal of irrelevant sections across everyday goals; keep rehearsed examples separate from unfamiliar-message checks. The full local model bundle, spreadsheet coverage and independent release evaluation remain later completion requirements. Semantic substitution must not invent facts or promise anonymity, and a successful demo does not establish full release readiness.

## Preserved components

`mask/` holds the current browser application and ML/evaluation tooling. `petpilot/` is an older generic column-detector baseline. The complete supplied synthetic challenge package remains under `TRUSTED_SinceAI2026_FINAL/`, including the original mobility benchmark material. The former bus application is no longer the product.

Challenge data/documentation retain upstream CC BY 4.0 attribution; supplied toolkit code retains its MIT license. See the package notices and materials guide.

The prior transport project is recoverable from Git at `23eedc29d6f2a3cd945cac2a4307e91e6427af77`. Its local runtime files were moved to `/private/tmp/mask-retired-bfz9ordp` during the earlier reset; that temporary directory is not durable storage.
