# Should the new Base replace the old model?

**The new Base is a clear overall improvement for a reviewed text/spreadsheet workflow. Do not replace it everywhere as a weights-only update.** Its complete Python pipeline is the better demo candidate, with the old model kept as a fallback. The browser needs explicit export/runtime work, and the original medical-record scenario still does not remove the unrelated visits. This assessment does not promote a production privacy guarantee or change the live default.

## What was actually run

On this laptop, using four CPU threads, run each complete published pipeline against:

- 50 original dev messages and 80 frozen, family-separated supplemental dev messages.
- 12 newly written 114–125-word diagnostics (eight distinct sources), frozen before either inference run. These include three meaningful same-source/task-switch pairs, ambiguous names, a credential, negation, vague/missing tasks and a benign control.
- Both original video messages and all six web-gallery examples.
- All 16 real CSV/XLSX parse → protect → export fixtures.

That is 150 message conditions and 16 file fixtures per model. Loading and inference ran with network access disabled. No thresholds, model parameters, transformation policy or production code were changed. Native application preview and direct engine outputs matched on all 12 fresh cases for each model. The old checkpoint's manifest hash matches the browser export's reference checkpoint. These comparisons use the same current Python policy code and each model's published versioned inference behavior; they are not a live browser parity test.

The 130 dev rows were used previously for development/selection and are synthetic, model-reviewed data. The gallery and file fixtures are training demonstrations. Fresh expectations were authored for this diagnostic, not human-audited independent benchmark labels. Gains include the new identity resolver and pipeline behavior, not just learned weights.

## Measured comparison

| Harder supplemental dev: 80 messages | Old Base | New Base |
|---|---:|---:|
| Missed annotated direct identifiers, out of 323 | 29 | 24 |
| Lost required-fact quotes, out of 405 | 19 | 8 |
| Inconsistent identity alias groups | 47 | 0 |
| Erroneously merged identity groups | 2 | 0 |
| Correctly removed complete target sections, out of 33 | 0 | 8 |
| Correctly removed target clauses, out of 58 | 0 | 20 |
| False clause removals | 0 | 5 |
| Correct task-conditioned switches, out of 42 | 0 | 9 |
| Changed approved-no-edit controls, out of 3 | 2 | 0 |
| Median CPU pipeline latency | 0.144 s | 0.644 s |

The original 50-message dev set has no identifier misses or lost required facts for either model. The new model removes 3/9 target sections and the old model removes none; there are no false clause removals on this set. Local counts reproduce the published comparison.

The new model fixes 16 of the old model's lost fact quotes but introduces five new losses; three losses persist. It fixes five identifier misses and introduces no new identifier misses on the dev sets. Therefore the aggregate improvement does not establish that it dominates the old model on every message.

The five new labeled fact losses concern care-allowance ownership, availability of an employer medical certificate, the reason a child squints at the board, and two pieces of an uptime/credit clause. Some gold claims are fragments around alias boundaries, and relevance judgments are not perfect. They remain counted as regressions; labels were not changed after seeing the outputs. Exact cases are in `summary.json` and the complete reports.

## Fresh messages and name restoration

| Fresh diagnostics: 12 conditions | Old Base | New Base |
|---|---:|---:|
| Lost checked facts, out of 30 | 0 | 0 |
| Correct complete task-dependent removals, out of 3 | 0 | 2 |
| Inconsistent full/short-name groups | 2 | 0 |
| Erroneous person merges | 0 | 0 |
| Identifier targets not fully covered | 1 | 1 |
| Benign no-edit control unchanged | Yes | Yes |
| Actual application previews supported | 12/12 | 12/12 |

The identifier boundary miss is the same for both: `DATABASE_PASSWORD=SilverLeaf_demo_4829!` becomes `DATABASE_PASSWORD=[SECRET]!`. The password body is masked but its terminal `!` remains, so exact target coverage fails. This is not a whole credential exposed, and not a new-model regression.

A useful actual success: with one set of health notes, the new model removes the psychiatric diagnosis/medicine and sleep details for a manager email, while retaining them for the clinician summary. Work restrictions and their negation/conditions remain. On the corporate incident pair, it removes confidential renewal/credit terms for the engineering task and retains them for the finance task. It fails to remove the household financial hardship block for a boiler appointment.

The name case has two different people named Sara. New aliases correctly link each full name to her surname, preserve the two identities separately, and leave the ambiguous bare Sara as its own alias. The actual local mock reply restores `Sara Hale Sara Nolan Sara`; unknown `[PERSON_999]` and `[EMAIL]` remain unchanged. No live provider response was requested. Exact working context examples are in `context-examples.md`.

## File and demo flows

All 16 CSV/XLSX round trips complete with both models. Exact expected fixture matches improve from **9/16 to 15/16**, with no new failing fixture. The remaining failure leaves a sentence containing an already masked payment-card number in a gardening message; it does not expose the card value. The corporate video CSV fixture matches for both.

Both models match only **1/6 complete approved gallery outputs exactly**. This strict metric includes missing removals and formatting, so it is not equivalent to five unusable outputs. The original medical video message receives just the three identity/contact replacements under both models. Its unrelated visits and birth date remain. The dedicated head identifies the unrelated visits, but the older span relevance head's essential decisions veto their deletion; see `../medical-base-20261108/`.

Measured direct engine medians on the supplemental set were 0.144 s old versus 0.644 s new. These are sequential single-run laptop measurements, not controlled general latency benchmarks; speed is still adequate for these demo-sized messages.

## Why the hosted browser cannot be upgraded by swapping weights

Static inspection of the current browser source finds:

1. Its ONNX graph exports only token tags, actions and span relevance. It does not export the new section head.
2. `BrowserModel` has no `predict_sections` method or new section runtime configuration, and its manifest contract has only the old two marker tokens.
3. The policy packager omits `sections`, `section_pipeline`, `identifiers` and `validators`, which are required by the new Python source. Its async transformation also needs the new section inference path.

This does not mean the existing deployed page is broken: it has its previously built bundle. It means a new complete model/policy export and matching browser adapter must be implemented and checked for Python/ONNX/browser output parity before promotion. `browser-compatibility.json` records the inspected file hashes and scope. The existing hosted page and model selection were not modified.

## Decision and next steps

Use the new complete Base pipeline as the preferred **reviewed demo candidate** for text and file handling. Its privacy and utility results are better overall, and it can demonstrate real task-conditioned decisions. Keep the old model accessible for comparison and rollback. Do not silently promote it across all surfaces today.

Before the browser deployment: implement the new graph/adapter/policy contract, verify the real hosted page against these exact outputs, and inspect the chosen video examples. Before claiming reliable general automatic removal: resolve the section-versus-span-head conflict and over-masking regressions, then rerun the frozen preservation cases. Merely lowering the deletion threshold is not justified by these results.

## Reproduce and inspect

- `run.py`: complete fixed comparison, with no network during inference.
- `fresh-inputs.json`: fixed fresh prompts and narrow expected facts/actions, saved before model runs.
- `results/{old,new}/`: full dev outputs, fresh outputs, demo previews, gallery outputs and actual protected tables.
- `summary.json`: counts, paired regressions and compatibility findings.
- `summarize.py`: generates the summary and working task-switch examples.
- `results/run.json`: code revision, model hashes, input hashes and environment.

```sh
python evidence/privacy-v1/base-replacement-20261108/run.py \
  --old /path/to/reviewed-2026-11-07/deberta-v3-base \
  --new /path/to/section-training-20261108/deberta-v3-base \
  --output /tmp/mask-base-comparison
```
