# v0.5.5 Open Questions

## Unresolved Items

### 1. API Access Limitation
Only Anthropic API accessible from current environment (OpenAI, DeepSeek, Gemini blocked by proxy). Multi-model critique loops used only Sonnet + Haiku. Future iterations should use diverse models for adversarial review.

### 2. gen_a4_012 (banana/FAOSTAT) — Residual Ambiguity
Rewrite tightened with FAOSTAT source qualifier, but critic rated 4/5 not 5/5. The "fruit crop" definition still allows edge-case debate (tomatoes, watermelons). Consider replacing entirely if models consistently flag ambiguity during sweep.

### 3. Family B Item Count
v0.5.4 reduced Family B from 87→84 items. Sprint plan originally referenced 87-item IDs — 3 items (`abs_087` and 2 others) were removed. If additional items are needed to reach a target count, generate new items following the API-assisted workflow.

### 4. Notebook End-to-End Validation
Deferred to Kaggle session. The notebook was taken from sprint/v0.5.4 which has reporting upgrades but hasn't been validated against the v0.5.5 data changes. Key cells to verify:
- Cell 3: dataset loading (117 cal items)
- Cell 10: Family B loading (84 items)
- Cell 4/12: self-tests with updated gold answers
- Cell 16: audit export

### 5. Kaggle Dataset Upload
`kaggle-upload/` directory needs re-sync with updated data files before next Kaggle submission. Files to copy:
- `data/metajudge_benchmark_v1.json` → `kaggle-upload/`
- `data/adjudication_registry.json` → `kaggle-upload/`
- `data/family_b_pilot_v2.json` → `kaggle-upload/`
- `metajudge/` package → `kaggle-upload/metajudge/`

### 6. False-Premise Interpretation
The false-premise items (abs_059, 070, 072, 073) use "premise-handling success" not pure "abstention success." The scorer gives partial credit for corrective answers. This framing should be documented in the writeup to prevent misinterpretation of Family B abstention rates.

### 7. Statistical Power
The statistics module supports paired comparisons, but with only 117 calibration items and 84 Family B items, some pairwise tests may be underpowered. The bootstrap CIs will be wide for small effect sizes. This is a reporting caveat, not a code fix.

### 8. Tri-Label "Contested" Items
7 contested items were reviewed and confirmed, but some (gen_a2_001, gen_a2_007) had only 4/5 confidence from reviewers. These should be re-examined if model sweep data shows consistent mislabeling.
