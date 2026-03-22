# v0.5.5 State Reconciliation

## Baseline
- Branch: `claude/audit-metajudge-v0.5.4-ofVQ9` with `sprint/v0.5.4` merged
- Calibration: 117 items (all in adjudication registry)
- Family B: 84 items (answer=15, clarify=13, verify=27, abstain=29)
- Tests: 263 passing

## P0 Calibration Defects — Status After Merge

| Item | Problem | Status | Notes |
|------|---------|--------|-------|
| `v42_mx_003` | Bookworm alias fragility | **FIXED** | Expanded accepted_forms in registry |
| `v42_mx_004` | Great Wall unit/tolerance | **FIXED** | contains_any mode + mi/km variants |
| `v42_mx_005` | Black box "bright orange" aliases | **FIXED** | In registry with orange variants |
| `v42_mx_008` | Wrong gold answer ($2007.14) | **STILL WRONG** | Correct: $2000.50 (annual compound 7.18% × 10yr) |
| `v41_crt_012` | Explanatory answers under-credited | **FIXED** | contains_any matching for explanations |
| `gen_b_004` | Source text / gold correctness | **CORRECT** | 4/5 verified via proper Bayesian analysis |
| `gen_a4_012` | Category ambiguity | **NEEDS REVIEW** | "banana" as gold for production volume is defensible but ambiguous |

## Completed in v0.5.5
1. Fixed `v42_mx_008` gold: $2007.14 → $2000.50
2. Rewrote `gen_a4_012` with FAOSTAT source qualifier
3. Tri-label queue: 9 items reviewed (2 changed, 7 confirmed)
4. Family B: 4 clarify rewrites, 7 verify widenings, 1 gold fix
5. Statistics module: McNemar, permutation, bootstrap, Stuart-Maxwell, Holm
6. 290 tests passing, all data consistency checks pass
