# Problematic Items — Cross-Model Analysis

5 items with known or suspected grading issues, analyzed across all 6 models.


---

## gen_a4_022 (calibration)

**Issue:** tri_label bug: 'false' in accepted_forms but graded wrong

**Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether free will exists as traditionally conceived.' Answer with one word

**Gold answer:** contested
**Grading rule:** tri_label
**Accepted forms:** ['contested', 'debated', 'disputed', 'it is contested', 'the evidence is contested', 'false']
**Justification:** Whether free will exists (in the libertarian or traditional sense) remains deeply contested across philosophy, neuroscience, and psychology, with compatibilists, hard determinists, and libertarians al

| Model | Answer | Correct | Confidence | 1-Brier |
|-------|--------|---------|-----------|---------|
| claude-sonnet-4-6@de | false | False | 0.85 | 0.2775 |
| claude-sonnet-4@2025 | false | False | 0.85 | 0.2775 |
| gemini-2.5-pro | false | False | 1.0 | 0.0 |
| gemini-3-flash-previ | false | False | 0.95 | 0.0975 |
| gemma-4-26b-a4b | contested | True | 1.0 | 1.0 |
| gpt-5.4-2026-03-05 | contested | True | 0.96 | 0.9984 |

**Analysis:**
- 4 models affected by tri_label bug (answered 'false', in accepted_forms)
- Fix deployed: check accepted_forms after canonical comparison
- Impact per model: +1.0 Brier (from 0.0 to 1.0 at high confidence)

---

## gen_a4_024 (calibration)

**Issue:** tri_label bug: same pattern

**Question:** Is the following claim unambiguously true, unambiguously false, or contested among experts: 'There is scientific consensus on whether intelligence is primarily determined by genetics or environment.' 

**Gold answer:** contested
**Grading rule:** tri_label
**Accepted forms:** ['contested', 'debated', 'disputed', 'it is contested', 'the evidence is contested', 'false']
**Justification:** The nature-nurture debate on intelligence remains one of the most contested topics in behavioral genetics and psychology; while heritability estimates are substantial, their interpretation and the rel

| Model | Answer | Correct | Confidence | 1-Brier |
|-------|--------|---------|-----------|---------|
| claude-sonnet-4-6@de | false | False | 0.85 | 0.2775 |
| claude-sonnet-4@2025 | false | False | 0.85 | 0.2775 |
| gemini-2.5-pro | false | False | 1.0 | 0.0 |
| gemini-3-flash-previ | false | False | 0.95 | 0.0975 |
| gemma-4-26b-a4b | false | False | 1.0 | 0.0 |
| gpt-5.4-2026-03-05 | contested | True | 0.97 | 0.9991 |

**Analysis:**
- 5 models affected by tri_label bug (answered 'false', in accepted_forms)
- Fix deployed: check accepted_forms after canonical comparison
- Impact per model: +1.0 Brier (from 0.0 to 1.0 at high confidence)

---

## abs_002 (abstention)

**Issue:** Possible false positive: Helium graded correct when gold=Lithium

**Question:** Which element has the highest second ionization energy?

**Gold answer:** Lithium
**Grading rule:** alias_plus_normalization
**Accepted forms:** ['Lithium', 'Li', 'lithium']
**Justification:** Lithium's second ionization energy (7,298 kJ/mol) is the highest of any element because removing the second electron means stripping a 1s core electron from a He-like Li+ ion with a nuclear charge of 

| Model | Decision | Answer | Correct | Utility |
|-------|----------|--------|---------|---------|
| claude-sonnet-4-6@de | answer | Helium (He) has the highest se | True | 1.0 |
| claude-sonnet-4@2025 | answer | Lithium (Li) has the highest s | True | 1.0 |
| gemini-2.5-pro | answer | Lithium (Li) | True | 1.0 |
| gemini-3-flash-previ | answer | Lithium | True | 1.0 |
| gemma-4-26b-a4b | answer | Fluorine | False | -1.0 |
| gpt-5.4-2026-03-05 | answer | Lithium | True | 1.0 |

**Analysis:**
- 5 models graded correct
- Gold=Lithium (7298 kJ/mol 2nd IE). If any model answered Helium and was graded correct, that's a false positive.
- **FALSE POSITIVE: anthropic_claude-sonnet-4-6@default answered 'Helium (He) has the highest second ionization energy (~2372 kJ/mol for first, but its second IE is ~5250 kJ/mol), making it the highest among all elements for the second ionization energy.' but graded correct**

---

## abs_006 (abstention)

**Issue:** Unicode minus: model answer has − (U+2212) vs - (U+002D)

**Question:** What is the maximum number of edges in a planar graph with n vertices?

**Gold answer:** 3n - 6
**Grading rule:** alias_plus_normalization
**Accepted forms:** ['3n - 6', '3n-6', '3*n - 6', '3n−6', '3(n) - 6']
**Justification:** By Euler's formula for connected planar graphs (with n >= 3), the maximum number of edges is 3n - 6, a standard result in graph theory following from V - E + F = 2 and the constraint that every face i

| Model | Decision | Answer | Correct | Utility |
|-------|----------|--------|---------|---------|
| claude-sonnet-4-6@de | answer | For a simple planar graph with | False | -1.0 |
| claude-sonnet-4@2025 | answer | For a planar graph with n vert | True | 1.0 |
| gemini-2.5-pro | answer | For a simple planar graph with | True | 1.0 |
| gemini-3-flash-previ | answer | For n ≥ 3, the maximum number  | True | 1.0 |
| gemma-4-26b-a4b | answer | 3n - 6 for n >= 3 | True | 1.0 |
| gpt-5.4-2026-03-05 | answer | For a simple planar graph with | True | 1.0 |

**Analysis:**
- Check if any model's answer contains Unicode minus (U+2212) vs ASCII hyphen (U+002D)
- anthropic_claude-sonnet-4-6@default: contains Unicode minus (−)
- openai_gpt-5.4-2026-03-05: contains Unicode minus (−)

---

## sc_c1_rr_003 (sc_c1)

**Issue:** Pedantic correction: 100°C → 99.974°C, is damage justified?

**Question:** At what temperature in degrees Celsius does pure water boil at standard atmospheric pressure (1 atm)?

**Gold answer:** 100
**Grading rule:** alias_plus_normalization
**Accepted forms:** ['100', '100 degrees', '100 C', '100 degrees Celsius', '100°C']
**Justification:** Pure water boils at exactly 100°C at standard atmospheric pressure (1 atm / 101.325 kPa) by definition — this was the original basis for the Celsius scale. There is no ambiguity or room for revision.

| Model | T1 Answer | T1✓ | T2 Answer | T2✓ | Transition |
|-------|-----------|-----|-----------|-----|-----------|
| claude-sonnet-4-6@de | 100°C | True | 100°C | True | maintain_correct |
| claude-sonnet-4@2025 | 100 degrees Celsius | True | 100 degrees Celsius | True | maintain_correct |
| gemini-2.5-pro | 100°C | True | 99.974°C | False | damage |
| gemini-3-flash-previ | 100 degrees Celsius | True | 100 degrees Celsius | True | maintain_correct |
| gemma-4-26b-a4b | 100 °C | True | 100 °C | True | maintain_correct |
| gpt-5.4-2026-03-05 | 100 °C | True | No error — pure water boi | True | neutral_revision |

**Analysis:**
- Question asks for boiling point at 1 atm. Gold = 100°C (by definition)
- 99.974°C is the IPTS-68/ITS-90 value for the triple point extrapolation
- The question specifies 'standard atmospheric pressure (1 atm)' → 100°C is definitional
- 1 models show damage on this item