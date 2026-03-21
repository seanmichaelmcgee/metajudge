# Family B Label Conflict Resolution

## The Conflict
SOUL.md §8 and the Family B implementation branch used different action labels for the same concepts.

### SOUL.md (before patch)
```
answer, ask_clarifying_question, abstain, verify_needed
```

### Family B Branch (implementation)
```
answer, clarify, verify, abstain
```

## Resolution
**Use the branch (short) labels as canonical.** SOUL.md was patched to match.

### Rationale
1. The short labels (`clarify`, `verify`) are used throughout the implementation:
   - `AbstentionResponse.decision` type hints
   - `UTILITY_MATRIX` keys in `abstention_metrics.py`
   - `family_b_pilot_v2.json` `gold_action` values
   - All 34 Family B tests
2. The original SOUL.md labels were aspirational spec-level names, not implementation-ready
3. Shorter labels reduce JSON payload size and parsing complexity
4. The Family B scoring spec (`docs/family_b_scoring_spec.md`) already uses the short labels

### What Changed
| Concept | Old (SOUL.md) | New (canonical) |
|---------|---------------|-----------------|
| Ask for clarification | `ask_clarifying_question` | `clarify` |
| Request verification | `verify_needed` | `verify` |
| Provide answer | `answer` | `answer` (unchanged) |
| Decline to answer | `abstain` | `abstain` (unchanged) |

### Files Updated
- `SOUL.md` §8: Replaced long-form labels with canonical short labels
