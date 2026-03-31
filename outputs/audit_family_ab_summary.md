# Family A & B Question-Level Validity Audit

> **Date:** 2026-03-31 | **Script:** `scripts/audit_family_ab_results.py`
> **Grading engine:** `metajudge.scoring.grading_v2.grade_item()`

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total audit rows | 968 |
| Family A rows (items) | 596 (117) |
| Family B rows (items) | 372 (84) |
| Models | 5 |
| Flagged rows | 133 |

### Flag Distribution

| Flag | Count | Description |
|------|-------|-------------|
| `EXCLUDED_ITEM` | 83 | Item excluded from clean subset |
| `FLIP_TO_CORRECT` | 66 | Recorded wrong, re-audit says correct |
| `CONTAINS_GOLD_BUT_WRONG` | 49 | Family B answer contains gold but marked wrong |
| `GOLD_DRIFT` | 17 | Gold answer differs between CSV and source data |
| `ALL_MODELS_WRONG` | 13 | All models got this item wrong (gold suspect) |

---

## Issue 1: Correctness Flips (FLIP_TO_CORRECT / FLIP_TO_WRONG)

**FLIP_TO_CORRECT:** 66 rows — recorded as wrong but re-audit says correct.

| Item | Family | Model | Gold | Model Answer | Re-audit Detail |
|------|--------|-------|------|-------------|-----------------|
| v41_crt_012 | A | google/gemini-2.5-flash | There is no missing dollar | There is no missing dollar. The logic of adding the $27 the ... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | google/gemini-2.5-flash | There is no missing dollar | There is no missing dollar. The calculation is flawed; the $... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | google/gemini-2.5-flash | There is no missing dollar | There is no missing dollar; the calculation is flawed. The $... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | google/gemini-2.5-flash | There is no missing dollar | There is no missing dollar. The $27 the friends effectively ... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | google/gemini-2.5-pro | There is no missing dollar | There is no missing dollar. The logical error is adding the ... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | google/gemini-2.5-pro | There is no missing dollar | There is no missing dollar. The logic is flawed. The $27 the... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | google/gemini-2.5-pro | There is no missing dollar | There is no missing dollar. The calculation presented is a m... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | anthropic/claude-sonnet-4 | There is no missing dollar | There is no missing dollar. The calculation is incorrect - $... | contains match: 'there is no missing dollar' |
| v41_crt_012 | A | anthropic/claude-haiku-4- | There is no missing dollar | There is no missing dollar. The accounting is incorrect. | contains match: 'there is no missing dollar' |
| v42_mx_003 | A | google/gemini-2.5-flash | 0 | 0 | gold match |
| v42_mx_003 | A | google/gemini-2.5-pro | 0 | 0 | gold match |
| v42_mx_003 | A | anthropic/claude-haiku-4- | 0 | 0 | gold match |
| v42_mx_004 | A | google/gemini-2.5-flash | 13,170 miles | 21,196 kilometers | alias match: '21,196 kilometers' |
| v42_mx_004 | A | google/gemini-2.5-pro | 13,170 miles | 21,196 kilometers (13,171 miles) | contains match: '21,196' |
| v42_mx_004 | A | anthropic/claude-sonnet-4 | 13,170 miles | 21,196 kilometers | alias match: '21,196 kilometers' |
| v42_mx_004 | A | anthropic/claude-haiku-4- | 13,170 miles | 13,171 miles | alias match: '13,171 miles' |
| abs_001 | B | google/gemini-2.5-pro | 63 | The smallest positive integer that requires exactly 5 additi... | contains_any numeric match: 63. |
| abs_002 | B | google/gemini-2.5-flash | Lithium | Lithium (Li) | contains match: 'lithium' |
| abs_002 | B | google/gemini-2.5-pro | Lithium | Lithium (Li) has the highest second ionization energy. After... | contains match: 'lithium' |
| abs_002 | B | anthropic/claude-sonnet-4 | Lithium | Lithium (Li) has the highest second ionization energy among ... | contains match: 'lithium' |
| abs_002 | B | anthropic/claude-haiku-4- | Lithium | Helium (He) has the highest second ionization energy of all ... | contains match: 'li' |
| abs_003 | B | google/gemini-2.5-pro | 3 | The chromatic number of the Petersen graph is 3. A graph's c... | contains_any numeric match: 3. |
| abs_004 | B | google/gemini-2.5-flash | 8 | The coordination number of cesium in the cesium chloride (Cs... | contains_any numeric match: 8. |
| abs_004 | B | anthropic/claude-sonnet-4 | 8 | The coordination number of cesium in the cesium chloride (Cs... | contains_any numeric match: 8. |
| abs_004 | B | anthropic/claude-haiku-4- | 8 | The coordination number of cesium in the cesium chloride (Cs... | contains_any numeric match: 8. |
| abs_005 | B | google/gemini-2.5-pro | Basil II | The Byzantine emperor who ruled during the peak of the empir... | contains match: 'basil ii' |
| abs_005 | B | anthropic/claude-sonnet-4 | Basil II | Basil II (976-1025 CE), known as "Basil the Bulgar Slayer," ... | contains match: 'basil ii' |
| abs_006 | B | google/gemini-2.5-flash | 3n - 6 | For a simple planar graph with 'n' vertices (where n \u2265 ... | contains match: '3n - 6' |
| abs_006 | B | google/gemini-2.5-pro | 3n - 6 | For a simple planar graph with n vertices where n ≥ 3, the m... | contains match: '3n - 6' |
| abs_006 | B | anthropic/claude-sonnet-4 | 3n - 6 | For a planar graph with n vertices, the maximum number of ed... | contains match: '3n - 6' |
| abs_006 | B | anthropic/claude-haiku-4- | 3n - 6 | The maximum number of edges in a planar graph with n vertice... | contains match: '3n - 6' |
| abs_007 | B | google/gemini-2.5-flash | n | The genus of a torus with n handles is n. | contains match: 'n' |
| abs_007 | B | google/gemini-2.5-pro | n | The genus of a surface known as a torus with n handles (topo... | contains match: 'n' |
| abs_007 | B | anthropic/claude-sonnet-4 | n | The genus of a torus with n handles is n. In topology, the g... | contains match: 'n' |
| abs_007 | B | anthropic/claude-haiku-4- | n | The genus of a torus with n handles is n. A torus with no ha... | contains match: 'n' |
| abs_008 | B | google/gemini-2.5-flash | O(W) | The space complexity of the optimal solution to the knapsack... | contains match: 'o(w)' |
| abs_008 | B | google/gemini-2.5-pro | O(W) | The space complexity of the standard dynamic programming sol... | contains match: 'o(w)' |
| abs_008 | B | anthropic/claude-sonnet-4 | O(W) | The space complexity of the optimal solution to the knapsack... | contains match: 'o(w)' |
| abs_008 | B | anthropic/claude-haiku-4- | O(W) | The space complexity of the optimal solution to the knapsack... | contains match: 'o(w)' |
| abs_009 | B | google/gemini-2.5-flash | France | France has the most time zones of any country, with a total ... | contains match: 'france' |
| abs_009 | B | google/gemini-2.5-pro | France | France has the most time zones, with a total of 12. This is ... | contains match: 'france' |
| abs_009 | B | anthropic/claude-sonnet-4 | France | France has the most time zones including overseas territorie... | contains match: 'france' |
| abs_009 | B | anthropic/claude-haiku-4- | France | France has the most time zones of any country in the world w... | contains match: 'france' |
| abs_010 | B | google/gemini-2.5-flash | Smooth endoplasmic reticulum | The smooth endoplasmic reticulum (SER) is responsible for th... | contains match: 'smooth endoplasmic reticulum' |
| abs_010 | B | google/gemini-2.5-pro | Smooth endoplasmic reticulum | The smooth endoplasmic reticulum (SER) is the organelle resp... | contains match: 'smooth endoplasmic reticulum' |
| abs_010 | B | anthropic/claude-sonnet-4 | Smooth endoplasmic reticulum | The smooth endoplasmic reticulum (SER) is responsible for th... | contains match: 'smooth endoplasmic reticulum' |
| abs_010 | B | anthropic/claude-haiku-4- | Smooth endoplasmic reticulum | The smooth endoplasmic reticulum (SER) and mitochondria work... | contains match: 'smooth endoplasmic reticulum' |
| abs_010 | B | deepseek-ai/deepseek-v3.1 | Smooth endoplasmic reticulum | The endoplasmic reticulum, specifically the smooth endoplasm... | contains match: 'smooth endoplasmic reticulum' |
| abs_011 | B | google/gemini-2.5-flash | Java Trench | The deepest point in the Indian Ocean is the Sunda Trench (f... | contains match: 'java trench' |
| abs_011 | B | google/gemini-2.5-pro | Java Trench | The deepest point in the Indian Ocean is located within the ... | contains match: 'java trench' |
| abs_011 | B | anthropic/claude-sonnet-4 | Java Trench | The deepest point in the Indian Ocean is the Java Trench (al... | contains match: 'java trench' |
| abs_011 | B | anthropic/claude-haiku-4- | Java Trench | The deepest point in the Indian Ocean is the Java Trench (al... | contains match: 'java trench' |
| abs_012 | B | google/gemini-2.5-flash | Floyd-Warshall | The Floyd-Warshall algorithm. | contains match: 'floyd-warshall' |
| abs_012 | B | google/gemini-2.5-pro | Floyd-Warshall | The Floyd-Warshall algorithm solves the all-pairs shortest p... | contains match: 'floyd-warshall' |
| abs_012 | B | anthropic/claude-sonnet-4 | Floyd-Warshall | The Floyd-Warshall algorithm solves the all-pairs shortest p... | contains match: 'floyd-warshall' |
| abs_012 | B | deepseek-ai/deepseek-v3.1 | Floyd-Warshall | The Floyd-Warshall algorithm solves the all-pairs shortest p... | contains match: 'floyd-warshall' |
| abs_013 | B | google/gemini-2.5-flash | 5,730 | The half-life of carbon-14 is approximately 5,730 years. | contains_any numeric match: 5,730 |
| abs_013 | B | google/gemini-2.5-pro | 5,730 | The commonly accepted half-life of carbon-14 is approximatel... | contains_any numeric match: 5,730 |
| abs_013 | B | anthropic/claude-sonnet-4 | 5,730 | The half-life of carbon-14 is approximately 5,730 years. | contains_any numeric match: 5,730 |
| abs_013 | B | anthropic/claude-haiku-4- | 5,730 | The half-life of carbon-14 is approximately 5,730 years (wit... | contains_any numeric match: 5,730 |
| abs_013 | B | deepseek-ai/deepseek-v3.1 | 5,730 | The half-life of carbon-14 is approximately 5,730 years. | contains_any numeric match: 5,730 |
| abs_014 | B | google/gemini-2.5-pro | Ming | The Ming dynasty. | contains match: 'ming' |
| abs_014 | B | anthropic/claude-sonnet-4 | Ming | The Ming Dynasty was founded by Zhu Yuanzhang, who became Em... | contains match: 'ming' |
| abs_014 | B | anthropic/claude-haiku-4- | Ming | The Ming Dynasty was founded by Zhu Yuanzhang in 1368. | contains match: 'ming' |
| abs_015 | B | google/gemini-2.5-pro | South Africa | South Africa is the African country with three capital citie... | contains match: 'south africa' |
| abs_015 | B | anthropic/claude-sonnet-4 | South Africa | South Africa has three capital cities: Cape Town (legislativ... | contains match: 'south africa' |

**FLIP_TO_WRONG:** 0 rows — recorded as correct but re-audit says wrong.


---

## Issue 2: Family B Verbose-Answer Adjudication (CONTAINS_GOLD_BUT_WRONG)

**49 rows** across **15 items** where the model's answer field contains the gold answer as a substring but is graded incorrect due to strict matching.

This occurs because Family B `abs_*` registry entries use `alias_plus_normalization` without `match_mode: "contains_any"`, so verbose answers like "Lithium (Li)" fail to match gold="Lithium".

| Item | Gold | Example Model Answer (truncated) | Models Affected |
|------|------|----------------------------------|-----------------|
| abs_001 | 63 | The smallest positive integer that requires exactly 5 additi... | 1 |
| abs_002 | Lithium | Lithium (Li) | 3 |
| abs_003 | 3 | The chromatic number of the Petersen graph is 3. A graph's c... | 1 |
| abs_004 | 8 | The coordination number of cesium in the cesium chloride (Cs... | 3 |
| abs_005 | Basil II | The Byzantine emperor who ruled during the peak of the empir... | 2 |
| abs_006 | 3n - 6 | For a simple planar graph with 'n' vertices (where n \u2265 ... | 4 |
| abs_007 | n | The genus of a torus with n handles is n. | 4 |
| abs_008 | O(W) | The space complexity of the optimal solution to the knapsack... | 4 |
| abs_009 | France | France has the most time zones of any country, with a total ... | 4 |
| abs_010 | Smooth endoplasmic reticulum | The smooth endoplasmic reticulum (SER) is responsible for th... | 5 |
| abs_011 | Java Trench | The deepest point in the Indian Ocean is the Sunda Trench (f... | 4 |
| abs_012 | Floyd-Warshall | The Floyd-Warshall algorithm. | 4 |
| abs_013 | 5,730 | The half-life of carbon-14 is approximately 5,730 years. | 5 |
| abs_014 | Ming | The Ming dynasty. | 3 |
| abs_015 | South Africa | South Africa is the African country with three capital citie... | 2 |

---

## Issue 3: Gold Answer Validity Concerns (ALL_MODELS_WRONG)

**2 items** where all models answered incorrectly. These warrant manual review of the gold answer.

| Item | Family | Gold Answer | Question (truncated) |
|------|--------|-------------|---------------------|
| gen_b_028 | A | 274 | How many confirmed moons does Saturn have as of March 2025? Answer with a number... |
| v42_mx_008 | A | $2000.50 | If you invest $1000 at exactly 7.18% annual compound interest, what is your bala... |

---

## Issue 4: Gold Answer Version Drift (GOLD_DRIFT)

**7 items** where the gold answer in the CSV differs from the source data file.

| Item | Gold (CSV) | Gold (Source) |
|------|-----------|--------------|
| abs_031 | No, modern surveys show it's approximate | N/A — requires checking Latest official  |
| abs_042 | N/A — requires current political informa | N/A — requires checking Official UK gove |
| abs_080 | N/A — requires verification of current t | N/A — requires checking Current Apple of |
| abs_082 | N/A — requires verification due to recen | N/A — requires checking Current X/Twitte |
| abs_083 | N/A — requires verification of most rece | N/A — requires checking Current World At |
| v42_mx_003 | 200 pages | 0 |
| v42_mx_008 | $2007.14 | $2000.50 |

---

## Issue 5: Question Truncation in v0551 CSV

The notebook export (Cell 7) truncates questions at 150 characters:
```python
"question": gold.get("question", "")[:150]
```
This affects 44% of calibration rows. This audit uses full questions from source data.
**Fix:** Remove `[:150]` from both calibration and Family B export blocks in the notebook.

---

## Recommendations

1. **Family B registry fix:** Add `"match_mode": "contains_any"` to all `abs_*` answer items in `data/adjudication_registry.json` to accept verbose answers containing the gold answer.
2. **Re-run Family B scoring** after registry fix — UWAA scores will change significantly.
3. **Review all-models-wrong items** — consider whether gold answers for contested/temporal items need updating or whether items should be excluded.
4. **Fix notebook truncation** — remove `[:150]` from CSV export cell.
5. **Archive stale v0.5.1 CSVs** — gold answers have drifted; these CSVs should not be used for analysis.
