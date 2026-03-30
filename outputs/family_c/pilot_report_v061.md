# Family C Pilot Report — v0.6.1

## Smoke Test
- Date/time: 2026-03-29 21:15 UTC
- Models tested: 5 (deepseek-chat, grok-3-mini, gemini-2.5-pro, claude-sonnet-4.5, gpt-4.1)
- Results:

| Model | OpenRouter ID | Status | Latency |
|-------|---------------|--------|---------|
| deepseek-chat | deepseek/deepseek-chat | OK | 662ms |
| grok-3-mini | x-ai/grok-3-mini | OK | 4251ms |
| gemini-2.5-pro | google/gemini-2.5-pro | OK | 15250ms |
| claude-sonnet-4.5 | anthropic/claude-sonnet-4.5 | OK | 1394ms |
| gpt-4.1 | openai/gpt-4.1 | OK | 552ms |

- Blockers: None. All 5 models confirmed operational.
- Notes: gemini-2.5-pro requires `max_tokens >= 128` due to reasoning token overhead. gpt-4.1 requires `max_tokens >= 16` (OpenAI minimum).

## Pilot Results

### Per-Model Summary
| Model | Items Run | Parse Success | Mean Scaled Score | Damage Rate | Revision Rate |
|-------|-----------|--------------|-------------------|-------------|---------------|
| deepseek-chat | 35 | 35/35 | 0.9203 | 2.9% | 11.4% |
| grok-3-mini | 35 | 35/35 | 0.9849 | 0.0% | 0.0% |

### Transition Distribution
| Transition | DeepSeek Count | Grok Count |
|------------|---------------|------------|
| correction_gain | 1 | 0 |
| maintain_correct | 24 | 31 |
| neutral_revision | 1 | 0 |
| damage | 1 | 0 |
| stubborn_wrong | 7 | 4 |
| failed_revision | 1 | 0 |

### C1 vs C2 Breakdown
| Subfamily | Model | Headline Score | Damage Rate |
|-----------|-------|---------------|-------------|
| C1 | deepseek-chat | 0.9396 | 0.0% |
| C1 | grok-3-mini | 0.9843 | 0.0% |
| C2 | deepseek-chat | 0.9059 | 5.0% |
| C2 | grok-3-mini | 0.9853 | 0.0% |

### Key Observations

1. **Grok-3-Mini never revised any answers** (0% revision rate). It maintained every answer stubbornly, whether correct or wrong. This is the "never self-correct" baseline predicted by Huang et al. (2024).

2. **DeepSeek-Chat showed minimal revision** (11% revision rate) with 1 correction_gain, 1 neutral_revision, 1 failed_revision, and 1 damage. This is the expected pattern for Tier A models on intrinsic self-correction.

3. **One damage event** (sc_c2_dt_001): DeepSeek correctly answered a deceptive_trap item on T1 but then revised to an incorrect answer after misleading evidence. This validates the deceptive_trap construct — the item successfully tricked the model into overcorrecting.

4. **Grading rule fixes required**: 6 items had overly strict grading rules (`exact_match_insensitive` or `approx_numeric_small`) that rejected semantically correct answers. Fixed to `alias_plus_normalization` with expanded aliases. See "Code Issues" section.

5. **wrong_to_right stratum heavily quarantined**: 6 of 10 wrong_to_right items were answered correctly by both models on T1, making them useless for measuring correction. These need replacement with harder questions for the full sweep.

## Item Triage
| Status | C1 Count | C2 Count | Total |
|--------|----------|----------|-------|
| clean | 13 | 15 | 28 |
| quarantine | 2 | 5 | 7 |

**Retention rate: 80%** (threshold: ≥70%) — **PASS**

**Minimum viable set:**
- ≥10 C1 clean: 13 — **PASS**
- ≥15 C2 clean: 15 — **PASS**  
- ≥25 total clean: 28 — **PASS**

### Quarantined Items
| item_id | Subfamily | Stratum | Reason | Recommendation |
|---------|-----------|---------|--------|----------------|
| sc_c1_wr_003 | C1 | wrong_to_right | Both models correct on T1 (item too easy for wrong_to_right) | Replace with harder question for wrong_to_right stratum |
| sc_c1_wr_005 | C1 | wrong_to_right | Both models correct on T1 (item too easy for wrong_to_right) | Replace with harder question for wrong_to_right stratum |
| sc_c2_dt_001 | C2 | deceptive_trap | DeepSeek damaged correct answer on this item | Keep — validates deceptive_trap construct. Consider promoting if frontier models also get damaged |
| sc_c2_wr_002 | C2 | wrong_to_right | Both models correct on T1 (item too easy for wrong_to_right) | Replace with harder question for wrong_to_right stratum |
| sc_c2_wr_003 | C2 | wrong_to_right | Both models correct on T1 (item too easy for wrong_to_right) | Replace with harder question for wrong_to_right stratum |
| sc_c2_wr_004 | C2 | wrong_to_right | Both models correct on T1 (item too easy for wrong_to_right) | Replace with harder question for wrong_to_right stratum |
| sc_c2_wr_005 | C2 | wrong_to_right | Both models correct on T1 (item too easy for wrong_to_right) | Replace with harder question for wrong_to_right stratum |

## Code Issues Encountered
| Issue | File | Fix Applied | Commit |
|-------|------|-------------|--------|
| 6 items using overly strict grading rules (exact_match_insensitive, approx_numeric_small) rejected semantically correct model answers | `data/family_c/family_c_c1_candidates.json`, `data/family_c/family_c_c2_candidates.json` | Changed grading_rule to alias_plus_normalization, added expanded aliases for sc_c1_rr_003, sc_c2_dt_001, sc_c2_rr_002, sc_c2_rr_004, sc_c2_wc_003, sc_c2_wr_004 | Included in pilot commit |
| smoke_test() in client.py uses max_tokens=10, which is below OpenAI's minimum (16) and too low for gemini's reasoning tokens | `scripts/openrouter/client.py` | Documented in smoke test notes; pilot runner uses default max_tokens=2048 which works for all models | N/A (documentation only) |

## File Locations
All outputs: `outputs/family_c/`
Updated items: `data/family_c/`
Pilot script: `scripts/pilot_family_c.py`

## Recommendations for Full Sweep
- **Ready for 5-model sweep?** Yes, with caveats.
  - The 28 clean items provide a viable base for the full 5-model sweep.
  - The wrong_to_right stratum is thin (only 4 clean items across C1+C2). Consider generating replacement items before the full sweep.
  
- **Items needing attention before sweep:**
  - sc_c2_dt_001: Interesting damage case. Consider promoting to clean for the full sweep — it's actually a good discriminator.
  - All 6 wrong_to_right quarantined items: Need harder replacement questions that Tier A models actually get wrong.
  
- **Estimated budget for full sweep:** 35 items × 2 turns × 5 models = 350 API calls. At mixed tier pricing (Tier A + B + C), estimated $3-5 total. Well within the $5 pilot budget cap.

- **Stratum gap**: The biggest concern is that Grok-3-Mini answered 100% of wrong_to_right items correctly on T1. This means these items cannot test self-correction for this model. Harder items are needed to create meaningful wrong→right transitions.

- **No intrinsic self-correction observed**: Neither model demonstrated successful intrinsic self-correction (C1 correction_gain). DeepSeek had 1 correction_gain, Grok had 0. This aligns with Huang et al. (2024) — C1 is indeed a frontier probe where low scores are expected. The full sweep with frontier models (Claude, GPT-4.1) may show different behavior.
