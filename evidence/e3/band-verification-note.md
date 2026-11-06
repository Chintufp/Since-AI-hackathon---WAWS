# Additional Astra verification

Astra rechecked actual-band-checks.json on 6 November 2026 UTC using NumPy stable argsort after sorting the public domain keys, rather than the diagnostic's Python sort expression. All five bands matched for protected top-three and top-ten overlap, cap-only top-three overlap, all exact/capped/protected top-three tuples and counts, and regret (absolute tolerance 1e-12). Raw/capped vectors were loaded through the existing production inference and capping path; this does not independently validate that shared path.

The evaluator SHA-256 matched the report. The existing release passed pipeline.artifact.verify and matched the report's original manifest digest. The private ledger's bytes were hashed before and after and were unchanged. The final silent video's bytes matched evidence/e6/silent-rehearsal-final.json. No new noise draw or publication occurred.

This is an alternate-calculation check by the same builder, **not peer acceptance**. Opus review remains pending. The five-band report is post-hoc, synthetic-only, all origins and one existing artifact; it does not extend the 100-draw morning claim. Main and its evidence summary remain unchanged.
