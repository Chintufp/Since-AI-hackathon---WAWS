# Additional Astra verification

Astra rechecked actual-band-checks.json on 6 November 2026 UTC using NumPy stable argsort after sorting the public domain keys, rather than the diagnostic's Python sort expression. All five bands matched for protected top-three and top-ten overlap, cap-only top-three overlap, all exact/capped/protected top-three tuples and counts, and regret (absolute tolerance 1e-12). Raw/capped vectors were loaded through the existing production inference and capping path; this does not independently validate that shared path.

The evaluator SHA-256 matched the report. The existing release passed pipeline.artifact.verify and matched the report's original manifest digest. The private ledger's bytes were hashed before and after and were unchanged. The final silent video's bytes matched evidence/e6/silent-rehearsal-final.json. No new noise draw or publication occurred.

This is an alternate-calculation check by the same builder, **not peer acceptance**. Opus review remains pending. The five-band report is post-hoc, synthetic-only, all origins and one existing artifact; it does not extend the 100-draw morning claim. Main and its evidence summary remain unchanged.

## Independent check reported through the coordinator

On 7 November 2026 UTC, the coordinating thread reported an independent read-only review using a separate NumPy ranking calculation, with source and release hash verification and no arithmetic mismatch. This paragraph records that communicated finding; the review's executable script and full output were not supplied here. It is additional corroboration, not Opus approval.

Interpretation boundaries from that review:

- Overlap measures set membership, not ordering within the shortlist.
- Night has 0/3 overlap and 95.85% regret; afternoon has 2/3 overlap.
- Midday's 3/3 is one favorable noisy draw: capping alone retained 2/3. Do not generalise that recovery or attribute all rank changes to one stage.
- The diagnostic contains unnoised synthetic reference counts. Its manifest synthetic-data check is not proof that arbitrary inputs are safe real-data substitutes. Never run or publish this reference diagnostic on real private data under this workflow.
- Keep the morning-led demo, 25.1% OD error disclosure and frozen main. The separate one-artifact diagnostic does not extend repeated-draw validation to other bands.
