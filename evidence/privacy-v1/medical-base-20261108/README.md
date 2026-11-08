# New Base checkpoint: medical demo check

Tested the unchanged `demo/personal-health-message.txt` locally using Base epoch 2, the versioned `section-head-v1` pipeline, and the real Python application preview service. Network access was disabled during loading and inference. This medical source is present in training (`c33e902d85e448c7a2be659edb432d41:video-health`): this is a demo diagnostic, not held-out validation.

Archive SHA256: `356bae562b723b84aa18880676db2fda0283b0cce8d37a6db37ab2703238459d`. The 597,907,864-byte download and all 11 bundled file checksums were verified. Source/inference code: `0b3854dfb65eaffca6714595ae6daf961d3f421e`.

## Actual behavior

All three task conditions produce identical protected source text. The name becomes `[PERSON_1]`, patient number `[ACCOUNT_ID]`, and email `[EMAIL]`. Cetirizine and the runny-nose/sneezing symptoms remain. The date of birth, anal-itching visit and wrist-injury visit also remain. There are no section removals.

| Task condition | CPU preview time | Edits | DROP edits |
|---|---:|---:|---:|
| browser_first_line | 1.76 s | 3 | 0 |
| backend_message_only | 1.93 s | 3 | 0 |
| specific_intended_task | 1.77 s | 3 | 0 |

Source length: 107 words. Model loading: 4.31 seconds. These are single-run timings on this laptop using four CPU threads, not a controlled latency benchmark.

## Why deletion was blocked

With the browser's first-line task or the more specific intended task, the dedicated section head classifies all eight clauses in the two unrelated visits as unnecessary. The existing value/span relevance head classifies the overlapping HEALTH blocks as essential. The safeguard `section_contains_retained_or_uncertain_evidence` therefore vetoes every proposed removal. For example, the unrelated September visit receives an unnecessary section score of about 0.9997 while its larger HEALTH span receives an essential score of about 0.8348. Scores are not calibrated safety probabilities.

With no separate task passed to the Python service, it uses the entire message as the task; the current `missing_or_vague_task` gate additionally prevents section deletion. The browser currently extracts the first line, so that is the primary demo condition reproduced here.

This local test does not justify filming the medical passage as an automatically removed section. The next issue to investigate is the conflict between the two relevance heads and the scope of the veto. Do not bypass the safeguard solely to make this example work; evaluate any resolution against the frozen preservation and deletion cases.

## Files and reproduction

- `protected-medical-record.txt`: exact protected source text, without manual cleanup.
- `results.json`: all three task inputs, outputs, edit diagnostics and preservation checks.
- `run.py`: reproducible local test. The source record is not rewritten for a favorable outcome.

```sh
python evidence/privacy-v1/medical-base-20261108/run.py \
  --model /path/to/artifacts/section-training-20261108/deberta-v3-base \
  --output /tmp/medical-base-results.json
```

The application preview and direct engine output matched in all three conditions. No cloud AI call, hosted-browser model update, threshold change or pipeline modification was performed.
